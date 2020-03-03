############################################
#### Evelyn - the Ultimate Puzzle Game ##### 
######### read Spotify Information #########
############################################

import sys
import spotipy
import requests
import spotipy.util as util
from os import path
from pydub import AudioSegment

class SpotifyInfo():
    def __init__(self, username):
        self.username = username
        self.displayName = None
        self.getAuth()
        self.playListDict = {}
        self.songURLs = {}
        self.playlistsNames = []
        if self.gotAuth:
            self.getPlaylistInfo()
            self.getPlaylistNames()
            
    def getAuth(self):
        ID = 'dcf8fdb9aff7434d8dfc70e62aee8e09'
        SECRET = 'e31c9a50e0f949f8a6082a2bf893af26'
        REDIRECT = 'https://sites.google.com/andrew.cmu.edu/spotipyauthorized/home'
        # private auth info gotten from Spotify Developer
        scope = 'user-library-read'
        token = util.prompt_for_user_token(self.username, scope, client_id=ID,
                                           client_secret=SECRET,
                                           redirect_uri=REDIRECT)
        if token:
            self.sp = spotipy.Spotify(auth=token)
            self.playlists = self.sp.user_playlists(self.username)
            self.gotAuth = True
        else:
            self.gotAuth = False
    
    def getPlaylistInfo(self):
        for playlist in self.playlists['items']:
            self.playlistSongs = []
            if playlist['owner']['id'] == self.username:
                self.displayName = playlist['owner']['display_name']
                listName = playlist['name']
                results = self.sp.user_playlist(self.username, playlist['id'],fields="tracks,next")
                tracks = results['tracks']
                self.show_tracks(tracks)
                self.playListDict[listName] = set(self.playlistSongs)
                while tracks['next']:
                    tracks = self.sp.next(tracks)
                    self.show_tracks(tracks)

    def show_tracks(self, tracks):
        for i, item in enumerate(tracks['items']):
            track = item['track']
            name = track['name']
            url = track['preview_url']
            if url != None:
                self.playlistSongs.append(name)
                self.songURLs[name] = url   

    def getPlaylistNames(self):
        for item in self.playListDict.keys():
            self.playlistsNames.append(item)

    def getPlaylistSongNames(self, playlist):
        playlistSongs = self.playListDict[playlist]
        return playlistSongs
    
    def getFile(self, songName):
        songURL = self.songURLs[songName]
        SpotifyInfo.downloadFile(songURL)
        return "songwave.wav"

    @staticmethod
    def downloadFile(AFileName):
        # modified from https://www.pluralsight.com/guides/guide-scraping-media-from-the-web-python
        filename = "song.mp3"
        rawImage = requests.get(AFileName, stream=True)
        with open(filename, 'wb') as fd:
            for chunk in rawImage.iter_content(chunk_size=1024):
                fd.write(chunk)

        # mp3 -> wav modified from https://pythonbasics.org/convert-mp3-to-wav/                                                                        
        src = "song.mp3"
        dst = "songwave.wav"
        # convert wav to mp3                                                            
        sound = AudioSegment.from_mp3(src)
        sound.export(dst, format="wav")
        return None