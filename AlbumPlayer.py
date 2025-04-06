#TODO:
# Remove depependency on Sonos HTTP API, can Spotipy do this?
#
#Structure:
#   -NFCPoller.py - Handles NFC polling and tag detection
#   -SonosController.py - Handles Sonos API interactions
#   -SpotifyController.py - Handles Spotify API interactions
#   -AlbumPlayer.py - Main script that integrates everything
#   -DBConnector.py - Handles database connections and queries
#   -config.py - Configuration file for API keys and settings

from time import sleep
import requests
from NFCPoller import NFCPoller
from DBConnector import DBConnector
from Registrar import Registrar
from SonosController import SonosController
import Webapp
import json

configfile = open('./config.json')
data = json.load(configfile)
SERVICE = data["service"]
VOLUME = data["volume"]
PLAYER = data["player"]
PORT = data["port"]

if __name__ == "__main__":

    nfc = NFCPoller()
    db = DBConnector()
    sc = SonosController()
    reg = Registrar()

    while True:
        sleep(1.0)
        nfc.poll()

        #No tag found, make sure nothing is playing and move on
        if nfc.tag == None:
            sc.stop()
            continue

        #This is the same tag that's been on the player, no change needed
        if nfc.tag == nfc.last_tag:
            continue
        
        result = reg.lookup_tag(nfc.tag)

        if result != None:
            sc.play_album(result[4])
        else:
            sc.play_mp3("http://album:3029/audio/detected.mp3")
            album = None
            playing = []
            while not album:
                playing.append(sc.now_playing())
                #Scan currently playing, capture a snapshot when it's playing
                #Wait about 10 seconds and capture another snapshot
                #If it's the same track and it's been playing consistently add this album
                sleep(3.0)
                if len(playing) > 2 and (int(playing[-1]['position'][-2:]) - int(playing[0]['position'][-2:])) > 10 and playing[0]['artist'] == playing[2]['artist']:
                    #Album has been playing for over 10 seconds, this seems intentional
                    album = reg.lookup_album(playing[-1]['artist'] + " " + playing[-1]['album'])
                    reg.add_album_to_db(album, nfc.tag)
                    sc.play_mp3("http://album:3029/audio/registered.mp3")

                    print("Album registered: " + album['artist'] + " " + album['album_name'])
                    result = reg.lookup_tag(nfc.tag)
                    if result != None:
                        sc.play_album(result[4])

                if len(playing) > 20:
                    sc.play_mp3("http://album:3029/audio/timeout.mp3")
                    break