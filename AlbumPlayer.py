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
import json

configfile = open('./config.json')
data = json.load(configfile)
SERVICE = data["service"]
VOLUME = data["volume"]
PLAYER = data["player"]

if __name__ == "__main__":

    nfc = NFCPoller("test")
    db = DBConnector()
    sc = SonosController(PLAYER)
    reg = Registrar()

    while True:
        tag = nfc.poll()

        if tag != nfc.current_tag:
            # Check for album in db
            db.connect()
            results = db.get_album(tag)
            db.close()

            print(results)
            if results:
                sc.play_album(results[4])
            else:
                print("Need to register this album")

        sleep(1)
        sc.pause()

