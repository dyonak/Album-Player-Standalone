from soco import SoCo, discover
from soco.music_services import MusicService
from soco.plugins.sharelink import ShareLinkPlugin
import DBConnector
from time import sleep
import json

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

    def play_mp3(self, link):
        self.pause()
        sleep(0.3)
        self.clear_queue()
        sleep(0.3)
        self.volume(VOLUME)
        sleep(0.3)
        self.player.play_uri(link)

    def get_state(self):
        try:
            transport_info = self.player.get_current_transport_info()
            print(transport_info)
            state = transport_info.get('current_transport_state')
            print(state)

            if state == 'PLAYING':
                print(f"{sonos.player_name} is currently playing.")
            elif state == 'PAUSED_PLAYBACK':
                print(f"{sonos.player_name} is currently paused.")
            elif state == 'STOPPED':
                print(f"{sonos.player_name} is currently stopped.")
            elif state == 'TRANSITIONING':
                print(f"{sonos.player_name} is transitioning between states.")
            else:
                print(f"Unknown state: {state}")
            
            return state

        except:
            return None

    def play_album(self, uri):
        self.pause()
        sleep(0.3)
        self.clear_queue()
        sleep(0.3)
        self.stop()
        sleep(0.3)
        self.volume(VOLUME)
        sleep(0.3)
        sharelink = ShareLinkPlugin(self.player)
        sharelink.add_share_link_to_queue(uri)
        sleep(0.3)
        self.player.play_from_queue(0)
        DBConnector.update_play_count(uri)

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
