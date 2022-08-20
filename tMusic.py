# tMusic Discord Music Bot V2022.8.1
# By IbraTech04 (github.com/IbraTech04)
# Powered by Deemix and IbraSoft tApps 

# Discord Imports, to interact with API

import asyncio
import shutil
import threading
from urllib.request import urlopen
import requests
import nextcord
from nextcord.ext import commands
from subprocess import Popen, PIPE
import os
import spotipy
import subprocess
import youtube_dl
from bs4 import BeautifulSoup
from song import *
SPOTIPY_CLIENT_ID = 'c630433b292d477990ebb8dcc283b8f5'
SPOTIPY_CLIENT_SECRET = 'a96c46ec319a4e878d3ac80058301041'
sp = spotipy.Spotify(client_credentials_manager=spotipy.SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET))

currentSongs = {} # Will store current song playing in each server - {server.id: song}
try:
    computerName = os.environ['COMPUTERNAME'] # Get the computer name so we know whether to use prod or dev bot
except KeyError:
    computerName = "Heroku"
# Bot intents, setting all to True
intents = nextcord.Intents.all()

if (computerName == "IBRAPC"): # If the code is running on my computer, do not run the main bot - run the dev bot
    tMusic = commands.Bot(intents = intents, command_prefix = 'd', activity = nextcord.Activity(type=nextcord.ActivityType.listening, name="TechMaster complain about my code"))
else:
    tMusic = commands.Bot(intents = intents, command_prefix = 't', activity = nextcord.Activity(type=nextcord.ActivityType.listening, name="tMusic - The Rewrite...."))

tMusic.remove_command('help') # Remove the help command

async def downloadSpotify(ctx, playlist):
    """
    Method which downloads a spotify playlist and adds it to the queue
    """
    song = currentSongs[ctx.message.guild.id]
    while (song.nextSong):
        song = song.nextSong
    
    directory = os.path.join(os.path.dirname(os.path.realpath(__file__)),str(ctx.message.guild.id))
    if (not os.path.isdir(directory)):
        #make directory
        os.makedirs(directory)
    for i in range (1,len(playlist['tracks']['items'])):
        try:
        #download the song 
            songName = await downloadSong(playlist['tracks']['items'][i]['track']['external_urls']['spotify'], ctx)
            song.nextSong = DonwloadedSong(songName, ctx.message.guild.id)
            song = song.nextSong
        except:
            pass

async def downloadDeezer(ctx, playlist):
    """
    Method which downloads a deezer playlist and adds it to the queue
    """
    song = currentSongs[ctx.message.guild.id]
    while (song.nextSong):
        song = song.nextSong
    
    directory = os.path.join(os.path.dirname(os.path.realpath(__file__)),str(ctx.message.guild.id))
    if (not os.path.isdir(directory)):
        #make directory
        os.makedirs(directory)
    for i in range (1,len(playlist['tracks']['data'])):
        try:
        #download the song 
            songName = await downloadSong(playlist["tracks"]["data"][i]["link"], ctx)
            song.nextSong = DonwloadedSong(songName, ctx.message.guild.id)
            song = song.nextSong
        except:
            pass

def inSameVC(ctx):
    """
    Method which checks if the user is in the same voice channel as the bot
    This is used to prevent random people from messing with the bot while it's playing music
    """
    return ctx.author.voice and ctx.author.voice.channel.id == ctx.voice_client.channel.id

def getVideoTitle(youtubeLink):
    """
    Method which uses ytdl to get the title of a youtube video, and returns it
    Legacy Code: Likely will not be rewritten to support tCodeV2 standards
    Feature wasn't really used in the end, but I'm keeping it here in case it's needed in the future
    """
    try:
        ydl = youtube_dl.YoutubeDL({})
        with ydl:
            video = ydl.extract_info(youtubeLink, download=False)
            #check if artist and track aren not null
            #get the title
            title = video['title']
            try: #check if the video has an artist
                toReturn = ('{} - {}'.format(video['artist'], video['track']))
            except:
                if ("(" in title):
                    toReturn = title.split("(")[0].split("ft.")[0]
                else:
                    #get channel name
                    channel = video['uploader']
                    toReturn = channel[:-1] + " " + title
        return toReturn
    except:
        return None

async def downloadSong (songName, ctx): #Downloads the song and returns the path to the file
    """
    Method which can take either a URL or a song name and download the track from it's respective platform (youtube, soundcloud, spotify)
    Legacy Code: Likely will not be rewritten to support tCodeV2 standards
    This method is very annoying to rewrite, and in its current state it works fine but is not very efficient
    """
    if(str(songName).startswith("https")):
        #check if its spotify or deezer link
        if ("deezer" in str(songName) or "spotify" in str(songName)):
            directory = os.path.join(os.path.dirname(os.path.realpath(__file__)),str(ctx.message.guild.id))
            if (not os.path.isdir(directory)):
                os.makedirs(directory)
            cmd = "deemix --portable -p {0} {1}".format(directory, songName)
            deezer = True
        #otherwise if its a youtube link
        elif ("youtube" in str(songName).lower()):
            #get the youtube video title
            video = str(getVideoTitle(songName))
            if (video != "None"):
                print(video)
                song = sp.search(video, limit=1)
                finalLink = song['tracks']['items'][0]['external_urls']['spotify']
                directory = os.path.join(os.path.dirname(os.path.realpath(__file__)),str(ctx.message.guild.id))
                if (not os.path.isdir(directory)):
                    os.makedirs(directory)
                cmd = "deemix --portable -p {0} {1}".format(directory, finalLink)
                deezer = True
        else: #its a soundcloud link 
            directory = os.path.join(os.path.dirname(os.path.realpath(__file__)),str(ctx.message.guild.id))
            if (not os.path.isdir(directory)):
                os.makedirs(directory)
            cmd = "scdl -c --path {0} -l {1}".format(directory, songName)
            deezer = False #dont use deezer
    else:
        deezer = True
        #search using deezer api and use async requests
        song = requests.get("https://api.deezer.com/search?q={0}&limit=1".format(songName))

        #get song link
        finalLink = song.json()['data'][0]['link']

        directory = os.path.join(os.path.dirname(os.path.realpath(__file__)),str(ctx.message.guild.id))
        if (not os.path.isdir(directory)):
            os.makedirs(directory)
        cmd = "deemix --portable -p {0} {1}".format(directory, finalLink)
    if (deezer):
        proc = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await proc.communicate() 
        return stdout.decode().splitlines()[4].split(':')[0].split(']')[1].lstrip().rstrip()
    
    else:
        #download song iwth scdl   
        proc = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await proc.communicate() 
        
        output = (stderr.decode('utf-8')).replace("\r", "").split("\n")[2][12:] #Getting songname from scdl output
        
        #Now we're done with getting hte songname. we need to get album art. We'll use beautiful soup to do this
        htmldata = urlopen(songName) 
        soup = BeautifulSoup(htmldata, 'html.parser')
        images = soup.find_all('img')
        if images != []:
            with (open(os.path.join(str(ctx.message.guild.id), output + ".png"), 'wb')) as f:
                f.write(urlopen(images[0]['src']).read())
        return output
    
@tMusic.command(pass_context = True, aliases=['Help', 'help', "HelpMeWithThisStupidBot", "Commands"])
async def commands(ctx):
    embed=nextcord.embeds.Embed(color=0xff0000)
    embed.add_field(name="tMusic Commands", value="Pretty much the stuff that you should be using")
    embed.add_field(name="tPlay", value="To play or queue a song. Must be in a VC to use this command. We support YouTube links, SoundCloud links, Spotify links, Deezer links, search queries, and local files in both playlist and track variety.", inline=False)
    embed.add_field(name="tLoop", value="Used to toggle the server-wide song/queue loop feature")
    embed.add_field(name="tQueue", value="To view the song queue")
    embed.add_field(name="tSong", value="Used to view the currently playing song")
    embed.add_field(name="tCredits", value="Used to view the people behind tMusic")
    embed.add_field(name="tPause and tResume", value="To pause and resume the currently playing song", inline = True)
    await ctx.send(embed=embed)    

@tMusic.command(pass_context=True)
async def loop(ctx, type: str = None):
    """
    Command which manipulates the linkedlists in the currentSongs dictionary to loop either a particular song or a queue
    """
    if (not ctx.voice_client):
        await ctx.reply(embed = nextcord.embeds.Embed(title = ":x: Error", description = "I'm not in a VC", color = 0xFF0000))
        return
    if (not inSameVC(ctx)):
        await ctx.reply(embed = nextcord.embeds.Embed(title = ":x: Error", description = "You must be in the same VC as me to use this command", color = 0xFF0000))
        return
    if (not ctx.voice_client.is_playing()):
        await ctx.reply(embed = nextcord.embeds.Embed(title = ":x: Error", description = "I'm not playing anything", color = 0xFF0000))
        return
    if (type == None or type.lower() == "song"):
        currentSongs[ctx.message.guild.id].nextSong = currentSongs[ctx.message.guild.id]
        await ctx.reply(embed=nextcord.embeds.Embed(title="Looping current song", description="Looping the track which is currently playing. To disable looping, add another song to the queue", color = 0x00008b))
        return
    if (type.lower() == "queue"):
        song = currentSongs[ctx.message.guild.id]
        while (song.nextSong != None):
            song = song.nextSong
            if (song == song.nextSong or song.nextSong == currentSongs[ctx.message.guild.id]): #If looping is enabled, break the loop since this could go on forever. 
                break
        song.nextSong = currentSongs[ctx.message.guild.id]
        await ctx.reply(embed = nextcord.embeds.Embed(title = "Looping queue", description = "Looping the queue. If you would like to disable queue looping, add another song to the queue, or clear the queue", color=0x00008B))
        return
    await ctx.reply(embed = nextcord.embeds.Embed(title = "Invalid loop type", description = "Valid loop types are: song, queue", color=0xff000))
@tMusic.command(pass_context=True)
async def ping(ctx):
    """
    Simple function which replies with pong
    """
    await ctx.reply('Pong!')

def checkQueue(ctx, firstSong: bool):
    """
    Proceeds the queue of songs and plays the next song if there is one
    Utilizes linkedlists to keep track of the songs in the queue
    """
    voice = ctx.guild.voice_client
    if (firstSong):
        player = voice.play(currentSongs[ctx.message.guild.id].getAudio(), after=lambda x=None: (checkQueue(ctx, False)))
        return
    if (not currentSongs[ctx.message.guild.id].nextSong == None and voice):
        player = voice.play(currentSongs[ctx.message.guild.id].nextSong.getAudio(), after=lambda x=None: (checkQueue(ctx, False)))            
        currentSongs[ctx.message.guild.id] = currentSongs[ctx.message.guild.id].nextSong
        embed = nextcord.embeds.Embed(title=":notes: Now Playing", description="{0}".format(currentSongs[ctx.message.guild.id].getSongName()), color=0x00008B)
        file = currentSongs[ctx.message.guild.id].getAlbumArt()
        embed.set_thumbnail(url="attachment://albumArt.jpg")
        channel = tMusic.get_channel(ctx.channel.id)
        tMusic.loop.create_task(channel.send(file = file, embed = embed)) 
        
        return

@tMusic.command(pass_context=True)
async def printAllEmojis(ctx):
    #For each emoji in the server, print its name and id, and send it in chat
    emojis = ctx.guild.emojis
    toSend = ""
    for emoji in emojis:
        toSend += (emoji.name + " " + str(emoji.id))
        toSend += "\n"
    await ctx.reply(toSend)       
@tMusic.command(pass_context=True)
async def play(ctx, *, song: str = None):
    """Plays a song.
    If there is a song currently in the VC, it will be queued.
    This mode also supports files attached to the message
    """
    loadingEmoji = tMusic.get_emoji(1009876091927805972) #Loading emoji - spinning circle shown while song is loading
    voice = nextcord.utils.get(tMusic.voice_clients,guild=ctx.guild) #Getting the voice client - this will tell us if tMusic is connected to a voice channel or not
    if (not ctx.message.author.voice or not ctx.message.author.voice.channel): #If the author is not in a voice channel, tell them to join one
        await ctx.reply(embed = nextcord.embeds.Embed(title = ":x: Error", description = "You must be in a voice channel to use this command", color = 0xFF0000))
        return
    if (voice and voice.is_paused()): #If the bot is in a VC, and the user is not in the same VC, tell them to join the same VC
        if (not inSameVC(ctx)):
            await ctx.reply(embed = nextcord.embeds.Embed(title = ":x: Error", description = "You must be in the same VC as me to use this command", color = 0xFF0000))
            return
        voice.resume() #Otherwise resume the voice client
        await ctx.reply(embed = nextcord.embeds.Embed(title = ":arrow_forward: Resumed", description = "Resuming the current song", color = 0x00008B))
        return
    if (not song and ctx.message.attachments == []):
        await ctx.reply(embed = nextcord.embeds.Embed(title = ":x: Error", description = "You must provide a song to play", color = 0xFF0000))
        return
    
    if (not voice):
        await ctx.message.author.voice.channel.connect()
        voice = nextcord.utils.get(tMusic.voice_clients,guild=ctx.guild) #Getting the voice client - this will tell us if tMusic is connected to a voice channel or not
    if (not inSameVC(ctx)):
        await ctx.reply(embed = nextcord.embeds.Embed(title = ":x: Error", description = "You must be in the same VC as me to use this command", color = 0xFF0000))
        return
    try:
        embed = nextcord.embeds.Embed(title=str(loadingEmoji) + " Loading Song", description="Please wait", color=0xFFFF00)
        await ctx.send(embed = embed)
        #get id of last message sent in channel
        channel = ctx.channel
        message = channel.last_message
        if (ctx.message.attachments == []):
            if (song.__contains__("playlist") and song.__contains__("spotify")):
                playlist = sp.playlist(song.split("/")[-1])
                songName = await downloadSong(playlist['tracks']['items'][0]['track']['external_urls']['spotify'], ctx)
                if (voice.is_playing()):
                    song = currentSongs[ctx.message.guild.id]
                    while (song.nextSong != None):
                        song = song.nextSong #find the last song in the queue; traverse the linked list
                        if (song == song.nextSong or song.nextSong == currentSongs[ctx.message.guild.id]): #If looping is enabled, break the loop since this could go on forever. 
                            break
                    song.nextSong = DonwloadedSong(songName, ctx.message.guild.id)
                else:
                    currentSongs[ctx.message.guild.id] = DonwloadedSong(songName, ctx.message.guild.id)
                    song = currentSongs[ctx.message.guild.id]
                    checkQueue(ctx, True)
                embed=nextcord.embeds.Embed(title=":notepad_spiral: Added to queue", description=playlist['name'], color=0x00008B)
                embed.set_thumbnail(playlist['images'][0]['url'])
                await ctx.send(embed = embed)
                await downloadSpotify(ctx,playlist)
                await message.delete()
                return
                
            if(song.__contains__("deezer")):
                #since its a deezer link we dont know what it will forward to
                #We need to use requests to get the forwarded link
                request = requests.get(song)
                #check url for deezer link
                if(str(request.url).__contains__("playlist")):                    
                    playlist = requests.get("https://api.deezer.com/playlist/" + str(request.url).split("/")[-1])
                    playlist = playlist.json()
                    songName = await downloadSong(playlist['tracks']['data'][0]['link'], ctx)
                    if (voice.is_playing()):
                        song = currentSongs[ctx.message.guild.id]
                        while (song.nextSong != None):
                            song = song.nextSong #find the last song in the queue; traverse the linked list
                            if (song == song.nextSong or song.nextSong == currentSongs[ctx.message.guild.id]): #If looping is enabled, break the loop since this could go on forever. 
                                break
                        song.nextSong = DonwloadedSong(songName, ctx.message.guild.id)
                    else:
                        currentSongs[ctx.message.guild.id] = DonwloadedSong(songName, ctx.message.guild.id)
                        song = currentSongs[ctx.message.guild.id]
                        checkQueue(ctx, True)
                    embed=nextcord.embeds.Embed(title=":notepad_spiral: Added to queue", description=playlist['title'], color=0x00008B)
                    embed.set_thumbnail(playlist['picture_xl'])
                    await ctx.send(embed = embed)
                    await downloadDeezer(ctx,playlist)
                    await message.delete()
                    return
                pass
            if (song.__contains__("playlist") and song.__contains_("youtube")):                 
                await ctx.send(embed = nextcord.embeds.Embed(title = ":x: Error", description = "YouYube playlists are not yet supported. Stay tuned for the next update which will bring YouTube playlist support!", color = 0xFF0000))
                return
            songName = await downloadSong(song, ctx) #Download the song and get the name of the song, if no playlist is detected
        else:
            fileName = ctx.message.attachments[0].filename
            if (not fileName.endswith(".mp3")):
                await message.delete()
                await ctx.reply(embed = nextcord.embeds.Embed(title = ":x: Error", description = "You must provide a .mp3 file. Support for more filetypes will be added in a future update", color = 0xFF0000))
                #delete message
                return
            songName = fileName[:-4]
            await ctx.message.attachments[0].save(os.path.join(str(ctx.message.guild.id), fileName))
    except Exception as e:
        embed = nextcord.embeds.Embed(title=":x: Error", description="Song not found. Try pasting a Spotify/Deezer link instead", color=0xff0000)
        await message.delete()
        await ctx.reply(embed = embed)
        #disconnect from voice channel
        await ctx.voice_client.disconnect()
    else:
        if (voice and voice.is_playing()):
            song = currentSongs[ctx.message.guild.id]
            while (song.nextSong != None):
                song = song.nextSong #find the last song in the queue; traverse the linked list
                if (song == song.nextSong or song.nextSong == currentSongs[ctx.message.guild.id]): #If looping is enabled, break the loop since this could go on forever. 
                    break
            song.nextSong = DonwloadedSong(songName, ctx.message.guild.id)
            embed = nextcord.embeds.Embed(title=":notepad_spiral: Added to Queue", description=songName, color= 0x006400)
            file = song.nextSong.getAlbumArt()
            embed.set_thumbnail(url="attachment://albumArt.jpg")
            await message.delete()
            await ctx.send(file = file, embed=embed)
            return
        currentSongs[ctx.message.guild.id] = DonwloadedSong(songName, ctx.message.guild.id)
        embed = nextcord.embeds.Embed(title=":notes: Now Playing", description=songName, color=0x00008B)
        file = currentSongs[ctx.message.guild.id].getAlbumArt()
        embed.set_thumbnail(url="attachment://albumArt.jpg")
        await message.delete()
        await ctx.send(file = file, embed=embed)
        checkQueue(ctx, True)
        return

@tMusic.command(pass_context=True)
async def pause(ctx):
    voice = nextcord.utils.get(tMusic.voice_clients,guild=ctx.guild) #Getting the voice client - this will tell us if tMusic is connected to a voice channel or not
    
    if (voice and voice.is_playing()):
        if (not inSameVC(ctx)):
            await ctx.reply(embed = nextcord.embeds.Embed(title=":x: Error", description="You must be in the same voice channel as me to use this command", color=0xff0000))
            return
        voice.pause()
        await ctx.reply(embed = nextcord.embeds.Embed(title=":pause_button: Paused", description=currentSongs[ctx.message.guild.id].getSongName(), color=0x00ff00))
        return
    await ctx.reply(embed = nextcord.embeds.Embed(title=":x: Error", description="There is nothing playing", color=0xff0000))
@tMusic.command(pass_context=True)
async def leave(ctx):
    """
    Command which leaves the voice channel the bot is in
    """
    voice = nextcord.utils.get(tMusic.voice_clients,guild=ctx.guild) #Getting the voice client - this will tell us if tMusic is connected to a voice channel or not
    if (not voice):
        await ctx.reply(embed = nextcord.embeds.Embed(title=":x: Error", description="I am not in a voice channel", color=0xff0000))
        return
    if (not inSameVC(ctx)):
        await ctx.reply(embed = nextcord.embeds.Embed(title=":x: Error", description="You must be in the same voice channel as me to use this command", color=0xff0000))
        return
    await voice.disconnect()
    await ctx.reply(embed = nextcord.embeds.Embed(title=":wave: Left Voice Channel", description="Goodbye!", color=0x00ff00))
    currentSongs[ctx.message.guild.id] = None
    try:
        shutil.rmtree(str(ctx.message.guild.id))
    except OSError as e:
        pass

@tMusic.command(pass_context=True)
async def queue(ctx):
    """
    Command which displays the queue of songs
    """
    if (not currentSongs[ctx.message.guild.id]):
        await ctx.reply(embed = nextcord.embeds.Embed(title=":x: Error", description="There is nothing in the queue", color=0xff0000))
        return
    song = currentSongs[ctx.message.guild.id]
    embed = nextcord.embeds.Embed(title=":notepad_spiral: Queue", description="", color=0x00ff00)
    i = 1
    while (song != None):
        embed.add_field(name = str(i), value=song.getSongName(), inline=False)
        if (song == song.nextSong or song.nextSong == currentSongs[ctx.message.guild.id]): #If looping is enabled, break the loop since this could go on forever. 
            break
        song = song.nextSong
        i += 1
    await ctx.send(embed = embed)
@tMusic.command(pass_context=True)
async def skip(ctx, amount = 1):
    """
    Command which skips the current song
    """
    voice = nextcord.utils.get(tMusic.voice_clients,guild=ctx.guild) #Getting the voice client - this will tell us if tMusic is connected to a voice channel or not
    
    if (not voice):
        await ctx.reply(embed=nextcord.embeds.Embed(title=":x: Error", description="I am not in a voice channel", color=0xff0000))
        return
    if (not inSameVC(ctx)):
        await ctx.reply(embed = nextcord.embeds.Embed(title=":x: Error", description="You must be in the same voice channel as me to use this command", color=0xff0000))
        return
    if (not voice.is_playing()):
        await ctx.reply(embed=nextcord.embeds.Embed(title=":x: Error", description="I am not playing anything", color=0xff0000))
        return
    if (not currentSongs[ctx.message.guild.id].nextSong):
        await ctx.reply(embed=nextcord.embeds.Embed(title=":x: Error", description="There is nothing in the queue. Try tStop instead", color=0xff0000))
        return
    embed = nextcord.embeds.Embed(title=":fast_forward: Skipped", description="{0}".format(currentSongs[ctx.message.guild.id].getSongName()), color=0x00ff00)
    await ctx.send(embed=embed)
    song = currentSongs[ctx.message.guild.id]
    for i in range (0, amount):
        song = song.nextSong
    currentSongs[ctx.message.guild.id].nextSong = song
    voice.stop()

@tMusic.event
async def on_ready():
    """
    Displays information about the bot when it is ready
    """
    print("Logged in as " + tMusic.user.name)
    print("tMusic is ready to go!")

# Running the bot
if (computerName == "IBRAPC"): # If the code is running on my computer, do not run the main bot - run the dev bot
    tMusic.run('ODk1ODUyMjQ1MTIyNDQ5NDM4.YV-law.nnA02HDvyZuKXdCYrq_sZjl9XAM') #Dev Token
else:
    tMusic.run('ODg3NDgxMTY1MjkwODAzMjEw.YUExPg.6-5n60OMYfOPfNbMyTbXhim97fg') #Main Token