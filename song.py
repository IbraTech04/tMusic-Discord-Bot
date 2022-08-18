import nextcord
from nextcord import FFmpegOpusAudio
import os
import requests
import eyed3
class DonwloadedSong():
    def __init__(self, songName, guildID) -> None:
        self.songName = songName
        self.guildID = guildID
        self.nextSong = None # This is for a linked list
        
        #---- This is for album art extraction ----#
        
        eyed = eyed3.load(os.path.join(str(self.guildID), self.songName[:-1] + ".mp3"))
        if (eyed.tag.images):
            albumArtFile = open(os.path.join(str(self.guildID), songName[:-1] + ".jpg"), "wb")
            albumArtFile.write(eyed.tag.images[0].image_data)
            self.albumArt = os.path.join(str(self.guildID), songName[:-1] + ".jpg")
        else:
            self.albumArt = "defaultAlbumArt.png"
            
    def getAudio(self):
        return FFmpegOpusAudio(os.path.join(str(self.guildID), self.songName[:-1] + ".mp3"))
    
    def getSongName(self):
        return self.songName
    
    def getAlbumArt(self):
        file = nextcord.File(self.albumArt, filename='albumArt.jpg') #Since the album art is extracted from the song, we cannot return the album art directly
        # We must return a discord.File object, which is a file that can be sent to discord
        return file