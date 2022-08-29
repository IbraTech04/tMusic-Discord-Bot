# tMusic Discord Music Bot V2022.8.1
# By IbraTech04 (github.com/IbraTech04)
# Powered by Deemix and IbraSoft tApps 

# Discord Imports, to interact with API

from ast import alias
import asyncio
from cgitb import text
import shutil
from telnetlib import TM
import threading
import traceback
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
from Errors import *
from song import *
SPOTIPY_CLIENT_ID = 'c630433b292d477990ebb8dcc283b8f5'
SPOTIPY_CLIENT_SECRET = 'a96c46ec319a4e878d3ac80058301041'
sp = spotipy.Spotify(client_credentials_manager=spotipy.SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET))

color = 0xFF5F00

currentSongs = {} # Will store current song playing in each server - {server.id: song}
try:
    computerName = os.environ['COMPUTERNAME'] # Get the computer name so we know whether to use prod or dev bot
except KeyError:
    computerName = "Heroku"
# Bot intents, setting all to True
intents = nextcord.Intents.all()

if (computerName == "IBRAPC"): # If the code is running on my computer, do not run the main bot - run the dev bot
    tMusic = commands.Bot(intents = intents, command_prefix = 'd', activity = nextcord.Activity(type=nextcord.ActivityType.listening, name="TechMaster complain about my code"))
    color = 0x00a0ff
else:
    tMusic = commands.Bot(intents = intents, command_prefix = 't', activity = nextcord.Activity(type=nextcord.ActivityType.watching, name="Myself get beta tested"))
    color = 0xFF5F00
tMusic.remove_command('help') # Remove the help command


async def downloadSpotify(ctx, playlist):
    """
    Method which downloads a spotify playlist and adds it to the queue
    :param ctx: The context of the command
    :param playlist: The playlist to download
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
    :param ctx: The context of the command
    :param playlist: The playlist to download
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
    :param ctx: The context of the command
    """
    return ctx.author.voice and ctx.author.voice.channel.id == ctx.voice_client.channel.id

async def getVideoTitle(youtubeLink):
    """
    Method which uses ytdl to get the title of a youtube video, and returns it
    Legacy Code: Likely will not be rewritten to support tCodeV2 standards
    Feature wasn't really used in the end, but I'm keeping it here in case it's needed in the future
    :param youtubeLink: The link to the youtube video
    """
    ydl = youtube_dl.YoutubeDL({})
    video = ydl.extract_info(youtubeLink, download=False)
    #check if artist and track aren not null
    #get the title
    try:
        if (video['track'] != None and video['artist'] != None):
            return video['artist'] + " " + video['track']
    except:
        return video['title'].split("(")[0].split("[")[0].split("|")[0] #Extract pure song title from video
    """
    Most of the time, YouTube Content ID adds metadata to the video telling us what the song is, but for songs without content ID we need to use the title
    
    Most song titles are in th form of "Artist - Track (<media type>)" The <media type> is often separated by the beginning of the title by either '(', '[' or '|'. So, if we split the title by these characters, we can get the pure song title
    """      

async def downloadSong (songName, ctx): #Downloads the song and returns the path to the file
    """
    Method which can take either a URL or a song name and download the track from it's respective platform (youtube, soundcloud, spotify)
    Legacy Code: Likely will not be rewritten to support tCodeV2 standards
    This method is very annoying to rewrite, and in its current state it works fine but is not very efficient
    :param songName: The name of the song to download. Could be a URL or a song name
    :param ctx: The context of the command
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
            songTitle = str(await getVideoTitle(songName))
            print(songTitle)
            #user deezer api to get the song
            request = requests.get("https://api.deezer.com/search?q={0}".format(songTitle))
            request = request.json()
            #check if deezer api returned an error
            if (request['total']==0):
                raise SongNotFoundException("No song found")
            directory = os.path.join(os.path.dirname(os.path.realpath(__file__)),str(ctx.message.guild.id))
            if (not os.path.isdir(directory)):
                os.makedirs(directory)
            finalLink = request['data'][0]['link']
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
        try:
            finalLink = song.json()['data'][0]['link']
        except:
            #throw SongNotFoundException
            raise SongNotFoundException("Song not found")
        directory = os.path.join(os.path.dirname(os.path.realpath(__file__)),str(ctx.message.guild.id))
        if (not os.path.isdir(directory)):
            os.makedirs(directory)
        cmd = "deemix --portable -p {0} {1}".format(directory, finalLink)
    if (deezer):
        proc = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        try:
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=15)
        except asyncio.TimeoutError:
            #throw new error called ARLException
            raise ARLException("ARL Error")
        
        output = stdout.decode()
        if (output == "Paste here your arl:"):
            raise ARLException("ARL Error")
        
        #stdout, stderr = await proc.communicate(timeout=10) 
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

@tMusic.command(pass_context=True)
async def setARL(ctx, arl):
    """
    Command which updates the .arl file in the config directory
    """
    #check if it's techmaster or not
    if (ctx.message.author.id == 516413751155621899):
        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "config", ".arl"), "w") as f:
            f.write(arl)
        await ctx.send("ARL Updated")
        return
    await ctx.send("You do not have permission to use this command. Only my owner can :pleading_face:")

@tMusic.event
async def on_guild_join(guild):
    embed=nextcord.embeds.Embed(title=":notes: Welcome to tMusic", description="Hi :wave:! Thank you for inviting me to your server! Use tPlay to get started!", color=color) 
    embed.add_field(name="Important Note:", value="Some users may experience degraded audio quality when setting tMusic's user volume to 100. For optimal results, we reccomend setting tMusic's user volume to ~80%", inline=False)
    embed.set_footer(text="Hint: Use the command `tHelp` to see a list of commands")
    channel = guild.system_channel
    if guild.system_channel: # If it is not None
        await channel.send(embed=embed)
    else: #If the server doesn't have a system channel, we need to get creative with a way to inform the user
        guildTextChannels = guild.text_channels
        #Now, we have to sort the guild text channels by their position
        guildTextChannels.sort(key=lambda x: x.position)
        #now that we have sorted the channels, we need to iterate and find the first one with general in the name
        for channel in guildTextChannels:
            if "general" in channel.name.lower():
                await channel.send(embed=embed)
                return
        #if we get here, we didn't find a general channel - we'll just send it to the first channel
        guildTextChannels[0].send(embed=embed)
        return

@tMusic.event
async def on_ready():
    """
    Displays information about the bot when it is ready
    """
    print("Logged in as " + tMusic.user.name)
    print("tMusic is ready to go!")

@tMusic.command(pass_context=True)
async def delete(ctx, amount: int):
    #check if it's techmaster or not
    if (ctx.message.author.id == 516413751155621899):
        #delete the amount of messages specified
        await ctx.message.channel.purge(limit=amount + 1)
@tMusic.command(pass_context = True, aliases=['Help', 'help', "HelpMeWithThisStupidBot", "Commands", 'about', 'aboutme', 'About', 'AboutMe'])
async def commands(ctx, command: str = None):
    if (not command):
        embed=nextcord.embeds.Embed(color=color)
        embed.title=":information_source: About tMusic"
        embed.description = "tMusic is the BEST Discord Music bot, supporting music from more sources than the competition! Here are the commands for tMusic:"
        embed.add_field(name="tPlay", value="Used to play and add songs to the queue")
        embed.add_field(name="tLoop", value="Used to toggle the server-wide song/queue loop feature.")
        embed.add_field(name="tQueue", value="To view the song queue")
        embed.add_field(name="tSong", value="Used to view the currently playing song")
        embed.add_field(name="tPause and tResume", value="To pause and resume the currently playing song", inline = True)
        embed.add_field(name="tSkip", value="Used to skip the currently playing song.", inline = True)
        embed.set_footer(text="Hint: Use tCommands followed by a command name to get more info about a specific command")
        await ctx.send(embed=embed)
        return
    command = command.lower()
    if (command == "tplay"):
        embed = nextcord.embeds.Embed(title = "About tPlay", description="tPlay is the main command utilized witih tMusic" ,color=color)
        embed.add_field(name="Description", value="Used to play and add songs to the queue", inline = True)
        embed.add_field(name="Usage", value="tPlay <song>", inline = True)
        embed.add_field(name="Supported <song> formats", value="tMusic supports a wide array of sources for your music. tMusic supports Spotify links, Deezer links, YouTube links, SoundCloud links, Search Queries, Spotify Playlists, Deezer Playlists, and attached files", inline = True)
        embed.add_field(name="Example", value="`tPlay https://open.spotify.com/track/4cOdK2wGLETKBW3PvgPWqT?si=3d28f2ff6178489d`", inline = True)
        embed.add_field(name="Coming Soon" ,value="tMusic will soon support YouTube Playlists and mutliple attached files!", inline = True)     
        await ctx.send(embed=embed)
        return
    if (command == "tloop"):
        embed = nextcord.embeds.Embed(title = "About tLoop", description="tLoop is an integral part of tMusic's experience" ,color=color)
        embed.add_field(name="Description", value="Used to loop the currently playing song, or the current queue", inline = True)
        embed.add_field(name="Usage", value="tLoop <optional argument>", inline = True)
        embed.add_field(name="Supported <optional argument> formats", value="By default, leaving the argument blank loops the currently playing song. However, by adding the 'queue' keyword after tLoop, tMusic will instead enable queue looping" , inline = True)
        embed.add_field(name="Example", value="`tLoop queue`", inline = True)
        await ctx.send(embed=embed)
        return
    if (command == "tqueue"):
        embed = nextcord.embeds.Embed(title = "About tQueue", description="tQueue is an integral part of tMusic's experience" ,color=color)
        embed.add_field(name="Description", value="Used to view the upcoming queue of songs", inline = True)
        embed.add_field(name="Usage", value="tQueue", inline = True)
        embed.add_field(name="Example", value="`tQueue`", inline = True)
        await ctx.send(embed=embed)
        return
    if (command == "tsong"):
        embed = nextcord.embeds.Embed(title = "About tSong", description="tSong is a unique yet important part of tMusic" ,color=color)
        embed.add_field(name="Description", value="Used to view the currently playing song", inline = True)
        embed.add_field(name="Usage", value="tSong", inline = True)
        embed.add_field(name="Example", value="`tSong`", inline = True)
        await ctx.send(embed=embed)
        return
    if (command == "tpause"):
        embed=nextcord.embeds.Embed(title = "About tPause", description="tPause is an important part of tMusic's functionality" ,color=color)
        embed.add_field(name="Description", value="Used to pause the currently playing song", inline = True)
        embed.add_field(name="Usage", value="tPause", inline = True)
        embed.add_field(name="Example", value="`tPause`", inline = True)
        await ctx.send(embed=embed)
        return
    if (command == "tresume"):
        embed = nextcord.embeds.Embed(title = "About tResume", description="tResume is an important part of tMusic's functionality" ,color=color)
        embed.add_field(name="Description", value="Used to resume a currently playing song", inline = True)
        embed.add_field(name="Usage", value="tResume", inline = True)
        embed.add_field(name="Example", value="`tResume`", inline = True)
        await ctx.send(embed=embed)
        return
    if (command == "tskip"):
        embed = nextcord.embeds.Embed(title = "About tSkip", description="tSkip is an important part of tMusic's functionality" ,color=color)
        embed.add_field(name="Description", value="Used to skip songs in queue", inline = True)
        embed.add_field(name="Usage", value="tSkip <optional argument>", inline = True)
        embed.add_field(name="Supported <optional argument> formats", value="By default, leaving the argument blank skips the currently playing song. However, by adding the a number after tSkip, tMusic will instead skip that amount of songs in queue" , inline = True)
        embed.add_field(name="Example", value="`tSkip 2`", inline = True)
        await ctx.send(embed=embed)
        return
    await ctx.send(embed=nextcord.embeds.Embed(title = "Command not found", description="The command you entered was not found. Please check your spelling and try again", color=0xff0000).set_footer(text="Hint: Use tCommands to view a list of commands"))

@tMusic.command(pass_context=True, aliases=['Loop', 'repeat', 'Repeat'])
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
        await ctx.reply(embed = nextcord.embeds.Embed(title = "Looping queue", description = "Looping the queue. If you would like to disable queue looping, add another song to the queue, or clear the queue", color=color))
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
        embed = nextcord.embeds.Embed(title=":notes: Now Playing", description="{0}".format(currentSongs[ctx.message.guild.id].getSongName()), color=color)
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
   
@tMusic.command(pass_context = True, aliases=['Play', 'p','pleasePlay', 'FindSong', "findSong", "getSongToPause"])
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
        if (not os.path.isdir(str(ctx.message.guild.id))): #If the server's folder doesn't exist, create it
            os.makedirs(str(ctx.message.guild.id))
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
                await ctx.reply(embed = nextcord.embeds.Embed(title = ":x: Error", description = "YouYube playlists are not yet supported. Stay tuned for the next update which will bring YouTube playlist support!", color = 0xFF0000))
                return
            songName = await downloadSong(song, ctx) #Download the song and get the name of the song, if no playlist is detected
        else:
            fileName = ctx.message.attachments[0].filename
            if (not fileName.endswith(".mp3") and not fileName.endswith(".wav")):
                await message.delete()
                await ctx.reply(embed = nextcord.embeds.Embed(title = ":x: Error", description = "You must provide an .mp3 or .wav file. Support for more filetypes will be added in a future update", color = 0xFF0000))
                #delete message
                return
            songName = fileName[:-4]
            await ctx.message.attachments[0].save(os.path.join(str(ctx.message.guild.id), fileName))
    except ARLException as e:
        await ctx.reply(embed = nextcord.embeds.Embed(title = ":x: Fatal Error", description = "tMusic has encountered a fatal error and cannot continue. Please try again later. This bug has automatically been reported to my author, along with any relavent context", color = 0xFF0000))
        channel = tMusic.get_channel(1010952626185179206) 
        await message.delete()
        #ping TechMaster04#5002
        user = tMusic.get_user(516413751155621899)
        await channel.send(user.mention + " my ARL might be out of date. Please update it!")
    except SongNotFoundException as e:
        embed = nextcord.embeds.Embed(title=":x: Error", description="Song not found. Try pasting a Spotify/Deezer link instead", color=0xff0000)
        await message.delete()
        await ctx.reply(embed = embed)
        #disconnect from voice channel
    except Exception as e:
        await ctx.reply(embed = nextcord.embeds.Embed(title = ":x: Fatal Error", description = "tMusic has encountered a fatal error and cannot continue. Please try again later. This bug has automatically been reported to my author, along with any relavent context", color = 0xFF0000))
        channel = tMusic.get_channel(1010952626185179206) 
        await message.delete()
        #ping TechMaster04#5002
        user = tMusic.get_user(516413751155621899)
        await channel.send(user.mention + f" I've encountered an error; Please investigate ``` {str(e)} ```  ``` {str(traceback.format_exc())} ``` My search query was: `{song}` \n This happened in: {ctx.message.guild.name} - {ctx.message.channel.name} \n {ctx.message.author.name} used this command") 
    else:
        if (voice and voice.is_playing()):
            song = currentSongs[ctx.message.guild.id]
            while (song.nextSong != None):
                song = song.nextSong #find the last song in the queue; traverse the linked list
                if (song == song.nextSong or song.nextSong == currentSongs[ctx.message.guild.id]): #If looping is enabled, break the loop since this could go on forever. 
                    break
            song.nextSong = DonwloadedSong(songName, ctx.message.guild.id)
            embed = nextcord.embeds.Embed(title=":notepad_spiral: Added to Queue", description=songName, color= color)
            file = song.nextSong.getAlbumArt()
            embed.set_thumbnail(url="attachment://albumArt.jpg")
            await message.delete()
            await ctx.send(file = file, embed=embed)
            return
        currentSongs[ctx.message.guild.id] = DonwloadedSong(songName, ctx.message.guild.id)
        embed = nextcord.embeds.Embed(title=":notes: Now Playing", description=songName, color=color)
        file = currentSongs[ctx.message.guild.id].getAlbumArt()
        embed.set_thumbnail(url="attachment://albumArt.jpg")
        await message.delete()
        await ctx.send(file = file, embed=embed)
        checkQueue(ctx, True)
        return

@tMusic.command(pass_context=True, aliases=['Resume'])
async def resume(ctx):
    if (not ctx.voice_client):
        await ctx.reply(embed = nextcord.embeds.Embed(title = ":x: Error", description = "I am not in a voice channel", color = 0xFF0000))
        return
    if (not ctx.message.author.voice):
        await ctx.reply(embed = nextcord.embeds.Embed(title = ":x: Error", description = "You are not in a voice channel", color = 0xFF0000))
        return
    if (not inSameVC(ctx)):
        await ctx.reply(embed = nextcord.embeds.Embed(title = ":x: Error", description = "YYou must be in the same VC as me to use this command", color = 0xFF0000))
        return
    if (not ctx.voice_client.is_paused()):
        await ctx.reply(embed = nextcord.embeds.Embed(title = ":x: Error", description = "Nothing's paused", color = 0xFF0000))
        return
    ctx.voice_client.resume()
    await ctx.send(embed = nextcord.embeds.Embed(title = ":play_pause: Resumed", description = "Resumed", color = 0x006400))

@tMusic.command(pass_context = True, aliases=['Pause', 'ununpause', "Ununpause", "UnUnpause"]) #Pause the current song
async def pause(ctx):
    voice = nextcord.utils.get(tMusic.voice_clients,guild=ctx.guild) #Getting the voice client - this will tell us if tMusic is connected to a voice channel or not
    
    if (voice and voice.is_playing()):
        if (not inSameVC(ctx)):
            await ctx.reply(embed = nextcord.embeds.Embed(title=":x: Error", description="You must be in the same voice channel as me to use this command", color=0xff0000))
            return
        voice.pause()
        await ctx.reply(embed = nextcord.embeds.Embed(title=":pause_button: Paused", description=currentSongs[ctx.message.guild.id].getSongName(), color=color))
        return
    await ctx.reply(embed = nextcord.embeds.Embed(title=":x: Error", description="There is nothing playing", color=0xff0000))
@tMusic.command(pass_context=True, aliases=['Leave', 'fuckOff', 'fuckoff', 'gtfo', 'Fuckoff', 'Gtfo'])
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
    await ctx.reply(embed = nextcord.embeds.Embed(title=":wave: Left Voice Channel", description="Goodbye!", color=color))
    currentSongs[ctx.message.guild.id] = None
    try:
        shutil.rmtree(str(ctx.message.guild.id))
    except OSError as e:
        pass

@tMusic.command(pass_context=True, aliases=['Queue', 'songList', 'songs', 'SongList', 'Songs'])
async def queue(ctx):
    """
    Command which displays the queue of songs
    """
    if (not currentSongs[ctx.message.guild.id]):
        await ctx.reply(embed = nextcord.embeds.Embed(title=":x: Error", description="There is nothing in the queue", color=0xff0000))
        return
    song = currentSongs[ctx.message.guild.id]
    embed = nextcord.embeds.Embed(title=":notepad_spiral: Queue", description="", color=color)
    i = 1
    while (song != None):
        embed.add_field(name = str(i), value=song.getSongName(), inline=False)
        if (song == song.nextSong or song.nextSong == currentSongs[ctx.message.guild.id]): #If looping is enabled, break the loop since this could go on forever. 
            break
        song = song.nextSong
        i += 1
    await ctx.send(embed = embed)

@tMusic.command(pass_context=True, aliases=['currentSong', 'CurrentSong', 'whatsPlaying', 'WhatsPlaying'])
async def song(ctx):
    song = currentSongs[ctx.message.guild.id]
    file = song.getAlbumArt()
    await ctx.send(file = file, embed = nextcord.embeds.Embed(title=":notes: Now Playing", description=song.getSongName(), color=color))

@tMusic.command(pass_context=True, aliases=['Skip', 'next', 'Next'])
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
        await ctx.reply(embed=nextcord.embeds.Embed(title=":x: Error", description="There is nothing in the queue. Try tPause instead", color=0xff0000))
        return
    embed = nextcord.embeds.Embed(title=":fast_forward: Skipped", description="{0}".format(currentSongs[ctx.message.guild.id].getSongName()), color=color)
    await ctx.send(embed=embed)
    song = currentSongs[ctx.message.guild.id]
    for i in range (0, amount):
        song = song.nextSong
    currentSongs[ctx.message.guild.id].nextSong = song
    voice.stop()

@tMusic.event
async def on_message(message):
    if tMusic.user.mention in message.content:
        await message.reply(embed=nextcord.embeds.Embed(title=":notes: Hi! I'm tMusic!", description="Use tPlay to get started, or tHelp to view a list of my commands!", color=color))
        return
    await tMusic.process_commands(message)
# Running the bot
if (computerName == "IBRAPC"): # If the code is running on my computer, do not run the main bot - run the dev bot
    tMusic.run(os.getenv('tMusicDevToken')) #Dev Token
else:
    tMusic.run(str(os.getenv('tMusicToken'))) #Main Token