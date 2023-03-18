import datetime
import sys
import pprint

from .Dreamkast import Dreamkast
from .Scene import Scene

class Operator:
    def __init__(self, dreamkast, loop, scene):
        self.dk = dreamkast
        self.loop = loop
        self.scene = scene

    def next_cmd(self, track_name: str, event_date: str):
        if event_date == "":
            event_date = datetime.datetime.now().strftime('%Y-%m-%d')

        print("||| CURRENT TRACK TALKS |||")
        self.dk.get_track_talks_cmd(track_name, event_date)
        
        print("\n")
        if not self.dk.onair_next(track_name, event_date):
            sys.exit(1)

        print("\n||| CURRENT SWICHER SCENES |||")
        self.loop.run_until_complete(self.scene.get())
        
        print("\n")
        self.loop.run_until_complete(self.scene.next())
    
    def now_cmd(self, track_name: str, event_date: str):
        if event_date == "":
            event_date = datetime.datetime.now().strftime('%Y-%m-%d')

        tracks = self.dk.get_track()
        for track in tracks:
            if track['name'] == track_name:
                track_id = track['id']
        current_talk = self.dk.get_current_onair_talk(track_id)
        current_scene = self.loop.run_until_complete(self.scene.current())
        print(f"talk  : {current_talk['id']}_{current_talk['title']}")
        print(f"scene : {current_scene}")