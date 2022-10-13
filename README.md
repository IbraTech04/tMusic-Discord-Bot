# tMusic Discord Bot

A proof-of-concept Discord bot that plays music using Deemix and Scdl

## About tMusic
tMusic was a passion project I started working on in 2020 to learn about Discord Bot development. Coincidentally, I also learned a lot about more advanced Python concepts, the guard-clause technique, and OOP concepts within python. 

The following GitHub repository is a fork of the "original" tMusic. Over the summer I took the opportunity to completely rewrite tMusic since I didn't code it using the best practices I know now. I also added a lot of new features and fixed a lot of bugs. For instance, queues now use a linked list instead of a list, which makes it easier to add and remove songs from the queue, loop the queue, and shuffle the queue. I will likely never release the legacy codebase since it's a mess- Okay mess is an understatement but the good thing is I learned from it

I never liked the idea of streaming music because of the latency and decreased quality. I wanted to create a bot that would download music directly and playback a file, rather than lose quality from streaming. Now, the way I achieve this is probably not the best way, but it works. I utilized a Python module called [Deemix](https://deemix.app/) to fetch music from. Deemix contains a translation layer for Spotify URLs, which meant I had two popular music services covered. For search queries, I made requests directly to [Deezer's APIs](https://developers.deezer.com/api) - Which allows native support for Deezer URLs.

I also wanted to make sure that the bot could play music from YouTube. I utilized yt-dl to download the webpage and extract the song data (Y'know, that tag in the description that says "Song: Artist - Song Name") - If it exists. If that information doesn't exist, I made a simple algorithm to convert the video title to a song name, and passed that to the Deezer API.

Finally, for SoundCloud, I utilized a Python module called [Scdl](https://github.com/flyingrub/scdl) - Sadly SoundCloud support is in limbo at the moment due to how it saves the music files. I'm working on a fix for this at the moment. 

I also didn't forget to add local file playback! You can now play music from your local machine, which is great for those who have a lot of music on their computer. One thing I've noticed is that many music bots (pretty much all of them....) don't extract ID3 tags from local files. Using [eyeD3](https://eyed3.readthedocs.io/en/latest/), I was able to add this functionality and make tMusic feel like a truly seamless experience. You can now see the song name, artist, and album art for local files!

## Features
* Play music from YouTube, Deezer, Spotify, and SoundCloud
* Play music from local files
* Display ID3 tags for local files (Song name, artist, album art)
* Queue system
    * Queue Looping
    * Queue Shuffling
* Playlist support from Deezer, and Spotify
    * YouTube Playlist support is coming soon!
* Search for songs, or search for queries
* Lyrics! 
    * Some songs don't have lyrics, but most do!
    * For most songs, I extract the lyrics directly from their ID3 tags
    * Some songs don't have ID3-tagged lyrics, and their lyrics are fetched from [Genius](https://genius.com/)
* EXCLUSIVE FEATURE: Synced Lyrics
    * Ever wonder what an artist is saying in a song? Now you can see the lyrics in real time! 
    * This feature is only available for select tracks - Some tracks have their lyrics downloaded by Deemix, and some get their lyrics fetched from Spotify using [Syrics](https://github.com/akashrchandran/syrics)
    * Some tracks don't have synced lyrics at all :(
* 320kbps audio quality! 
    * This is the highest quality audio of any music bot I've seen
* Slash commands coming soon!

## Commands
All of tMusics commands can be found within the `tHelp` command. This command will display all of the commands, and their descriptions. By typing `tHelp <command>`, you can get more information about a specific command. But alas, here are the basics:

* `tPlay <query>` - Play a song/playlist from YouTube, Deezer, Spotify, or SoundCloud. Or you can attach a file and tMusic will parse and play it!
* `tPause` - Pause the current song
* `tResume` - Resume the current song
* `tSkip` - Skip the current song
* `tLyrics` - Display the lyrics for the current song - If they exist
* `tSyncedLyrics` - Display the synced lyrics for the current song - If they exist
* `tQueue` - Display the current queue
* `tSong` - Display the current song
* `tLoop` - Toggle queue/song looping
* `tShuffle` - Shuffle the queue - Still a work in progress
* `tLeave` - Leave the voice channel
* `tRemove <index>` - Remove a song from the queue

## Installation

### Requirements
* Python 3.8+ - I personally test this on Python 3.10.4, but any version of Python 3.8+ should work.
* [NextCord](https://github.com/nextcord/nextcord) - The rewrite of tMusic fully utilizes (or at least, will at some point) NextCord's features, so it's required.
* [Deemix](https://pypi.org/project/deemix/) - This is used to download music from Deezer and Spotify. You can install it using pip.
* [Scdl](https://github.com/flyingrub/scdl) - This is used to download music from SoundCloud. You can install it using pip.
* [eyeD3](https://eyed3.readthedocs.io/en/latest/) - This is used to extract ID3 tags from music files. You can install it using pip.
* [FFmpeg](https://ffmpeg.org/) - This is used to convert music files to the correct format - In this case OPUS audio encoding. You can install it using your package manager of choice, or download prebuilt binaries from the FFmpeg website.
* [youtube-dl](https://youtube-dl.org/) - This is used to extract information from YouTube videos. You can install it using pip.
* [Spotipy](https://spotipy.readthedocs.io/en/2.19.0/) - This is used to obtain track information from Spotify Playlists. You can install it using pip.
* [bs4](https://pypi.org/project/beautifulsoup4/) - This is used to scrape various websites for information. You can install it using pip.

### Setup
1. Clone the repository using `git clone
2. Install the requirements using `pip install -r requirements.txt`
3. Create environment variables for the following:
    * `tMusicToken` - This is your Discord Bot Token. You can get this from the [Discord Developer Portal](https://discord.com/developers/applications).
    * `SpotifyClientID` - This is your Spotify Client ID. You can get this from the [Spotify Developer Portal](https://developer.spotify.com/dashboard/applications).
    * `SpotifyClientSecret` - This is your Spotify Client Secret. You can get this from the [Spotify Developer Portal](https://developer.spotify.com/dashboard/applications).
    * 'GeniusToken' - This is your Genius Token. You can get this from the [Genius Developer Portal](https://genius.com/api-clients).
    These are all required for full functionality of all of tMusic's features
4. Run using `python tMusic.py`
5. Enjoy the bot... or not 

## Post Setup Notes
In order for tMusic to function completely, it needs some tokens from you

### For Deemix: 
* Your `arl` is required. To obtain it, you need to create and log into a Deezer account. Once logged in from the Deezer homepage, open DevTools (Inspect Element) using `Ctrl + Shift + I`. Navigate to the `Application` tab, and then to `Cookies`. Find the cookie named `arl`, and copy the value. This is your `arl` token. 
* Paste this into the `config/.arl` file.

### For Syrics (Synced Lyrics):
* Assuming you created a Spotify Developer account, have configured an application, and setup the environment variables, all that's left is to paste your sp_dc token. 
* To obtain this, you need to create and log into a Spotify account. Once logged in, open DevTools (Inspect Element) using `Ctrl + Shift + I`. Navigate to the `Application` tab, and then to `Cookies`. Find the cookie named `sp_dc`, and copy the value. This is your `sp_dc` token. 
* Paste this into the `config/.sp_dc` file.


**NOTICE: This bot is a proof-of-concept, and is not meant to be used in production. I am not responsible for any reprocussions that result from the use of this bot**
