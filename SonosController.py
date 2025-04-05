from soco import SoCo, discover
from soco.music_services import MusicService
from soco.plugins.sharelink import ShareLinkPlugin
from DBConnector import DBConnector
from time import sleep
import json
from flask import g

configfile = open('./config.json')
data = json.load(configfile)
SERVICE = data["service"]
VOLUME = data["volume"]
PLAYER = data["player"]

class SonosController:
    def __init__(self):
        self.player = None
        self.current_track = None
        players = discover()
        self.player = None
        for p in players:
            if p.player_name == PLAYER:
                self.player = p
                break

    def get_db(self):
        """Get the database connection for the current request."""
        if 'db' not in g:
            g.db = DBConnector()
        return g.db

    def clear_queue(self):
        self.player.clear_queue()

    def play(self):
        self.player.play()

    def pause(self):
        try:
          self.player.pause()
        except:
          return

    def stop(self):
        self.player.stop()

    def next(self):
        self.player.next()

    def previous(self):
        self.player.previous()

    def volume(self, volume):
        self.player.volume = volume
    
    def now_playing(self):
        return self.player.get_current_track_info()

    def play_album(self, uri):
        self.pause()
        sleep(0.3)
        self.clear_queue()
        sleep(0.3)
        self.volume(VOLUME)
        sleep(0.3)
        sharelink = ShareLinkPlugin(self.player)
        sharelink.add_share_link_to_queue(uri)
        sleep(0.3)
        self.play()
        db = self.get_db()
        db.update_play_count(uri)
        db.close()

if __name__ == "__main__":
  sc = SonosController()
  sc.volume(VOLUME)

  sc.play_album("")
  sleep(60)
  sc.pause()
  # sharelink = ShareLinkPlugin(player)
  # sharelink.add_share_link_to_queue("https://open.spotify.com/album/14IYDXybb1XKu51QHDryak")
  # sc.play()
  # sleep(5)
  # sc.pause()

  # album = sc.now_playing()["album"]
  # print(sc.now_playing())

  # service = MusicService(SERVICE)
  # sc.clear_queue()
