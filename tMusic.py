# tMusic Discord Music Bot V2022.8.1
# By IbraTech04 (github.com/IbraTech04)
# Powered by Deemix and IbraSoft tApps 

# Discord Imports, to interact with API
import asyncio
import shutil
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

computerName = os.environ['COMPUTERNAME'] # Get the computer name so we know whether to use prod or dev bot
 
# Bot intents, setting all to True
intents = nextcord.Intents.all()

if (computerName == "IBRAPC"): # If the code is running on my computer, do not run the main bot - run the dev bot
    tMusic = commands.Bot(intents = intents, command_prefix = 'd', activity = nextcord.Activity(type=nextcord.ActivityType.listening, name="TechMaster complain about my code"))
else:
    tMusic = commands.Bot(intents = intents, command_prefix = 't', activity = nextcord.Activity(type=nextcord.ActivityType.listening, name="tcommands"))

def inSameVC(ctx):
    """
    Method which checks if the user is in the same voice channel as the bot
    This is used to prevent random people from messing with the bot while it's playing music
    """
    return ctx.author.voice and ctx.author.voice.channel.id == ctx.voice_client.channel.id

def getVideoTitle(youtubeLink):
    """
    Method which uses ytdl to get the title of a youtube video, and returns it
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
        output = (stdout.decode()) 
        #output = run(cmd ,capture_output=True,text = True).stdout.splitlines()
        output = output.splitlines()
        output = output[4].split(':')
        finalSongName = output[0].split(']')[1].lstrip()
        finalSongName.rstrip()
        return finalSongName
    else:
        #download song iwth scdl   
        proc = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await proc.communicate() 
        return await getSoundcloudSongTitle(songName)

async def getSoundcloudSongTitle(url):
    """
    Method which uses beautiful soup to get the title of a soundcloud song by scraping its URL name from the web
    """
    reqs = requests.get(url)
    # using the BeaitifulSoup module
    soup = BeautifulSoup(reqs.text, 'html.parser')
    title1 = ""
    for title in soup.find_all('title'):
        print(title.get_text())
        title1 = title.get_text()

    title = str(title1)

    #remove first 7 charactesr
    title = title1[7:]

    title = title.split("|")[0]

    #find the last "by" in the string

    title = title.split("by")
    finalTitle = ""
    for i in range(0, len(title)-1):
        finalTitle = finalTitle + title[i]  

    return(finalTitle)

@tMusic.command(pass_context=True)
async def loop(ctx, type: str = None):
    """
    Command which manipulates the linkedlists in the currentSongs dictionary to loop either a particular song or a queue
    """
    if (not ctx.voice_client):
        await ctx.reply("I need to be in a voice channel to do that")
        return
    if (not inSameVC(ctx)):
        await ctx.reply("You must be in the same voice channel as the bot to use this command")
        return
    if (not ctx.voice_client.is_playing()):
        await ctx.reply("I'm not playing anything right now")
        return
    if (type == None):
        currentSongs[ctx.message.guild.id].nextSong = currentSongs[ctx.message.guild.id]
        await ctx.reply("Looping current song")
        return
    if (type == "queue"):
        song = currentSongs[ctx.message.guild.id]
        while (song.nextSong != None):
            song = song.nextSong
        song.nextSong = currentSongs[ctx.message.guild.id]
        await ctx.reply("Looping queue")
@tMusic.command(pass_context=True)
async def ping(ctx):
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
    if (not currentSongs[ctx.message.guild.id].nextSong == None):
        player = voice.play(currentSongs[ctx.message.guild.id].nextSong.getAudio(), after=lambda x=None: (checkQueue(ctx, False)))            
        currentSongs[ctx.message.guild.id] = currentSongs[ctx.message.guild.id].nextSong
        
        embed = nextcord.embeds.Embed(title="Now Playing", description="{0}".format(currentSongs[ctx.message.guild.id].getSongName()), color=0x00ff00)
        file = currentSongs[ctx.message.guild.id].getAlbumArt()
        embed.set_thumbnail(url="attachment://albumArt.jpg")
        channel = tMusic.get_channel(ctx.channel.id)
        tMusic.loop.create_task(channel.send(file = file, embed = embed)) 
        
        return

@tMusic.command(pass_context=True)
async def play(ctx, *, song: str = None):
    """Plays a song.
    If there is a song currently in the VC, it will be queued.
    This mode also supports files attached to the message
    """
    voice = nextcord.utils.get(tMusic.voice_clients,guild=ctx.guild) #Getting the voice client - this will tell us if tMusic is connected to a voice channel or not
    
    if (not song):
        await ctx.reply('You must specify a song to play (...duh)')
        return
    if (voice and voice.is_paused()):
        if (not inSameVC(ctx)):
            await ctx.reply('You must be in the same voice channel as me to use this command')
            return
        await voice.resume()
        await ctx.reply('Resumed')
        return
    if (not voice or not voice.is_connected()):
        await ctx.author.voice.channel.connect()
        try:
            embed = nextcord.embeds.Embed(title="Loading Song", description="Please wait", color=0x00ff00)
            await ctx.send(embed = embed)
            songName = await downloadSong(song, ctx)
        except Exception as e:
            embed = nextcord.embeds.Embed(title="Error", description="Song not found. Try pasting a Spotify/Deezer link instead", color=0x00ff00)
            await ctx.reply(embed = embed)
            #disconnect from voice channel
            await ctx.voice_client.disconnect()
        else:
            currentSongs[ctx.message.guild.id] = DonwloadedSong(songName, ctx.message.guild.id)
            embed = nextcord.embeds.Embed(title="Now Playing", description=songName, color=0x00ff00)
            file = currentSongs[ctx.message.guild.id].getAlbumArt()
            embed.set_thumbnail(url="attachment://albumArt.jpg")
            await ctx.send(file = file, embed=embed)
            checkQueue(ctx, True)
            return
    if (voice and voice.is_playing()):
        if (not inSameVC(ctx)):
            await ctx.reply('You must be in the same voice channel as me to use this command')
            return
        try:
            embed = nextcord.embeds.Embed(title="Loading Song", description="Please wait", color=0x00ff00)
            await ctx.send(embed = embed)
            songName = await downloadSong(song, ctx)
        except Exception as e:
            embed = nextcord.embeds.Embed(title="Error", description="Song not found. Try pasting a Spotify/Deezer link instead", color=0x00ff00)
            await ctx.reply(embed = embed)
        else:
            song = currentSongs[ctx.message.guild.id]
            while (song.nextSong != None):
                song = song.nextSong #find the last song in the queue; traverse the linked list
            
            song.nextSong = DonwloadedSong(songName, ctx.message.guild.id)
            embed = nextcord.embeds.Embed(title="Added to Queue", description=songName, color=0x00ff00)
            file = song.nextSong.getAlbumArt()
            embed.set_thumbnail(url="attachment://albumArt.jpg")
            await ctx.send(file = file, embed=embed)
            return
        
@tMusic.command(pass_context=True)
async def leave(ctx):
    """
    Command which leaves the voice channel the bot is in
    """
    voice = nextcord.utils.get(tMusic.voice_clients,guild=ctx.guild) #Getting the voice client - this will tell us if tMusic is connected to a voice channel or not
    if (not voice):
        await ctx.reply('I am not in a voice channel')
        return
    if (not inSameVC(ctx)):
        await ctx.reply('You must be in the same voice channel as me to use this command')
        return
    await voice.disconnect()
    await ctx.reply("Bye!")
    currentSongs[ctx.message.guild.id] = None
    try:
        shutil.rmtree(ctx.message.guild.id)
    except OSError as e:
        pass

@tMusic.command(pass_context=True)
async def skip(ctx):
    """
    Command which skips the current song
    """
    voice = nextcord.utils.get(tMusic.voice_clients,guild=ctx.guild) #Getting the voice client - this will tell us if tMusic is connected to a voice channel or not
    
    if (not voice):
        await ctx.reply('I am not in a voice channel')
        return
    if (not inSameVC(ctx)):
        await ctx.reply('You must be in the same voice channel as me to use this command')
        return
    if (not voice.is_playing()):
        await ctx.reply('There is no song playing')
        return
    voice.stop()
    embed = nextcord.embeds.Embed(title="Skipped", description="{0}".format(currentSongs[ctx.message.guild.id].getSongName()), color=0x00ff00)
    await ctx.send(embed=embed)
@tMusic.event
async def on_ready():
    print("Logged in as " + tMusic.user.name)
    print("tMusic is ready to go!")

# Running the bot
if (computerName == "IBRAPC"): # If the code is running on my computer, do not run the main bot - run the dev bot
    tMusic.run('ODk1ODUyMjQ1MTIyNDQ5NDM4.YV-law.nnA02HDvyZuKXdCYrq_sZjl9XAM') #Dev Token
else:
    tMusic.run('ODg3NDgxMTY1MjkwODAzMjEw.YUExPg.6-5n60OMYfOPfNbMyTbXhim97fg') #Main Token