from typing_extensions import Self
import nextcord
from nextcord import FFmpegOpusAudio
import os
import eyed3

class DonwloadedSong():
    def __init__(self, songName, guildID, startTime, requester) -> None:
        self.songName = songName
        self.guildID = guildID
        self.nextSong = None # This is for a linked list
        self.startTime = startTime
        self.realSongName = None
        #---- This is for album art extraction ----#
        
        eyed = eyed3.load(os.path.join(str(self.guildID), self.songName + ".mp3"))
        if (eyed.tag.images):
            albumArtFile = open(os.path.join(str(self.guildID), songName + ".jpg"), "wb")
            albumArtFile.write(eyed.tag.images[0].image_data)
            self.albumArt = os.path.join(str(self.guildID), songName + ".jpg")
        elif (os.path.exists(os.path.join(str(self.guildID), songName + ".png"))):
            self.albumArt = os.path.join(str(self.guildID), songName + ".png")
        else:
            self.albumArt = "defaultAlbumArt.png"
        
        # Get total duration of the song
        self.songDuration = eyed.info.time_secs
        self.requester = requester
        
        #check if song has lyrics tag
        if eyed.tag.lyrics:
            self.lyrics = u"".join([i.text + "\n" for i in eyed.tag.lyrics])
        else:
            self.lyrics = None
        
        # Check if the song has artist and title tags
        if eyed.tag.artist and eyed.tag.title:
            self.realSongName = eyed.tag.artist + " - " + eyed.tag.title
        
        
        """
        Instead of using the deezer API to search for the song and locate it's album art, we can use the eyed3 library to extract the album art from the song directly. That way, we have a unified way to extract album art from any song; Whether it be through deemix, scdl, or an uploaded track on discord.
        
        This implementation may be a little slower than the deezer API, but it is more reliable.
        """
    def getSongDescription(self):
        """
        Returns all the info in the tags of a song
        """
        song = eyed3.load(os.path.join(str(self.guildID), self.songName + ".mp3"))
        songInfo = ""
        for tag in [a for a in dir(song.tag) if not a.startswith('__')]:
            songInfo += str(tag) + "\n"
        if songInfo == "":
            return "No tags found"
        return songInfo
        
    def getAudio(self):
        return FFmpegOpusAudio(os.path.join(str(self.guildID), self.songName.replace("*", "_") + ".mp3")) # We must return an audio object, which is a file that can be played in discord
    
    def getSongName(self):
        if self.realSongName:
            return self.realSongName
        return self.songName
    
    def getAlbumArt(self):
        file = nextcord.File(self.albumArt, filename='albumArt.jpg') #Since the album art is extracted from the song, we cannot return the album art directly
        # We must return a discord.File object, which is a file that can be sent to discord
        return file
    def getRequester(self):
        return self.requester
    def getStartTime(self):
        return self.startTime
    def getDuration(self):
        return self.songDuration
    def hasLyrics(self):
        return self.lyrics != None
    def getLyrics(self):
        return self.lyrics

class InProgressSong():
    def __init__(self) -> None:
        pass