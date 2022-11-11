from email import header
import logging
logger = logging.getLogger(__name__)
import os
import sys
import json
import requests
import base64
import datetime
import jwt

from . import cli

class Dreamkast:
    
    def __init__(self, DK_URL, AUTH0_URL, CLIENT_ID, CLIENT_SECRETS, EVENT_ABBR) -> None:
        self.dk_url = DK_URL
        self.auth0_url = AUTH0_URL
        self.client_id = CLIENT_ID
        self.client_secrets = CLIENT_SECRETS
        self.event_abbr = EVENT_ABBR

    def __read_token(self, env_file_path):
        token_file = open(env_file_path, "r")
        token = token_file.read()
        token_file.close()

        return token

    def __check_dk_env(self, env_file_path):
        if os.path.isfile(env_file_path):
            token = self.__read_token(env_file_path=env_file_path)
        else:
            print("The '{}' not found. Please, generate token using 'cndctl dk update'".format(env_file_path))
            return False
        
        if not token:
            print("token '{}' is empty".format(env_file_path))
            return False
        
        token_payload = jwt.decode(token, options={"verify_signature": False})
        token_expire = datetime.datetime.fromtimestamp(token_payload['exp'])

        if datetime.datetime.now() < token_expire:
            return True
        else:
            print("The token is expired. Please update using `cndctl dk update`")
            return False

    # cndctl dk update
    def update(self):
        logger.debug("dreamkast_update()")
        env_file_path = ".dk.env"

        if self.__check_dk_env(env_file_path=env_file_path):
            print("token not expired")
            sys.exit()

        if not cli.accept_continue("Dk token update ok?"):
            sys.exit()

        req_url = "https://" + self.auth0_url + "/oauth/token"
        headers = {
            "content-type": "application/json"
        }
        data = {
            "client_id":"",
            "client_secret":"",
            "audience":"https://event.cloudnativedays.jp/",
            "grant_type":"client_credentials"
        }
        data['client_id'] = self.client_id
        data['client_secret'] = self.client_secrets

        res = requests.post(req_url, headers=headers, data=json.dumps(data))
        res_payload = res.json()
        print("token update successfully ({})".format(res_payload))

        token_file = open(".dk.env", "w")
        token_file.write(res_payload['access_token'])
        token_file.close()

    def talks(self):
        logger.debug("dreamkast_update()")

    def onair(self, DK_TALK_ID):
        logger.debug("dreamkast_onair()")

        if self.__check_dk_env(env_file_path=".dk.env"):
            token = self.__read_token(env_file_path=".dk.env")
            req_url = "https://" + self.dk_url + "/api/v1/talks/{}".format(DK_TALK_ID)
            headers = {
                'Authorization': 'Bearer {}'.format(token)
            }
            data = {
                "on_air": True
            }
            logger.debug("request\nurl   : {}\nheader: {}\ndata  : {}".format(req_url, headers, data))
            res = requests.put(req_url, headers=headers, data=json.dumps(data))
            res_payload = res.json()
            print(res_payload)

    def get_track(self):
        logger.debug("get_track_name()")

        req_url = "https://" + self.dk_url + "/api/v1/tracks?eventAbbr={}".format(self.event_abbr)
        res = requests.get(req_url)
        res_payload = res.json()
        
        return res_payload

    def get_track_name(self, TRACK_ID):
        logger.debug("get_track_name")
        
        tracks = self.get_track(self.dk_url, self.event_abbr)
        for track in tracks:
            if track['id'] == TRACK_ID:
                return track

    def get_conference_day_ids(self):
        logger.debug("get_conference_day_ids()")

        req_url = "https://" + self.dk_url + "/api/v1/events"
        res = requests.get(req_url)
        res_payload = res.json()

        # get event id
        i = 0
        for event in res_payload:
            if event['abbr'] == self.event_abbr:
                event_list_position = i
            i = i + 1
        
        return res_payload[event_list_position]['conferenceDays']

    def get_talks(self, CONFERENCE_DAY_ID):
        logger.debug("get_talks()")
        
        talks = list()

        req_url = "https://" + self.dk_url + "/api/v1/talks?eventAbbr={}&conferenceDayIds={}".format(self.event_abbr, CONFERENCE_DAY_ID)
        res = requests.get(req_url)
        res_payload = res.json()
        
        for talk in res_payload:
            talks.append(talk)

        return talks

    def create_talks(self):
        conference_day_ids = self.get_conference_day_ids(self.dk_url, self.event_abbr)
        tracks_list = self.get_track(self.dk_url, self.event_abbr)
        
        talks = list()
            
        for day_id in conference_day_ids:
            if day_id['internal']:
                continue
            insert_track_list = list()
            
            for track in tracks_list:
                insert_talks_list = list()
            
                for talk in self.get_talks(self.dk_url, self.event_abbr, day_id['id']):
                    if not track['id'] == talk['trackId']:
                        continue
                                    
                    # change start_at date
                    start_at = datetime.datetime.fromisoformat(talk['actualStartTime']).replace(
                                                                    year=int(day_id['date'].split('-')[0]), 
                                                                    month=int(day_id['date'].split('-')[1]), 
                                                                    day=int(day_id['date'].split('-')[2]))
                    # change end_at date
                    end_at   = datetime.datetime.fromisoformat(talk['actualEndTime']).replace(
                                                                    year=int(day_id['date'].split('-')[0]), 
                                                                    month=int(day_id['date'].split('-')[1]), 
                                                                    day=int(day_id['date'].split('-')[2]))

                    talk_time = int((end_at - start_at).seconds / 60)
                    
                    
                    is_after_rest = False
                    
                    insert_talk = {
                        "id": talk['id'],
                        "title": talk['title'],
                        "start_at": start_at.isoformat(),
                        "end_at": end_at.isoformat(),
                        "start_offset": talk['startOffset'],
                        "end_offset": talk['endOffset'],
                        "talk_time": talk_time,
                        "is_after_rest": is_after_rest,
                        "track_id": talk['trackId'],
                        "track_name": track['name'],
                        "presentation_method": talk['presentationMethod'],
                        "scene_template": ""
                    }
                    insert_talks_list.append(insert_talk)
                
                insert_talks_list.sort(key = lambda x:x['start_at'])
                insert_track = {
                    "id": track['id'],
                    "name": track['name'],
                    "talks": insert_talks_list
                }
                insert_track_list.append(insert_track)
                    
            insert_track_list.sort(key = lambda x:x['name'])
            talks_info = {
                "date": day_id['date'],
                "tracks": insert_track_list
            }
            talks.append(talks_info)
            
        return talks