import logging
import pprint
import requests
logger = logging.getLogger(__name__)
import os
import datetime
import jwt

def get_token(env_file_path):
    token_file = open(env_file_path, "r")
    token = token_file.read()
    token_file.close()

    return token

def check_dk_env(env_file_path):
    if os.path.isfile(env_file_path):
        token = get_token(env_file_path=env_file_path)
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

def get_track(DK_URL, EVENT_ABBR):
    logger.debug("get_track_name()")

    req_url = "https://" + DK_URL + "/api/v1/tracks?eventAbbr={}".format(EVENT_ABBR)
    res = requests.get(req_url)
    res_payload = res.json()
    
    return res_payload

def get_track_name(DK_URL, EVENT_ABBR, TRACK_ID):
    logger.debug("get_track_name")
    
    tracks = get_track(DK_URL, EVENT_ABBR)
    for track in tracks:
        if track['id'] == TRACK_ID:
            return track
    

def get_conference_day_ids(DK_URL, EVENT_ABBR):
    logger.debug("get_conference_day_ids()")

    req_url = "https://" + DK_URL + "/api/v1/events"
    res = requests.get(req_url)
    res_payload = res.json()

    # get event id
    i = 0
    for event in res_payload:
        if event['abbr'] == EVENT_ABBR:
            event_list_position = i
        i = i + 1
    
    return res_payload[event_list_position]['conferenceDays']

def get_talks(DK_URL, EVENT_ABBR, CONFERENCE_DAY_ID):
    logger.debug("get_talks()")
    
    talks = list()

    req_url = "https://" + DK_URL + "/api/v1/talks?eventAbbr={}&conferenceDayIds={}".format(EVENT_ABBR, CONFERENCE_DAY_ID)
    res = requests.get(req_url)
    res_payload = res.json()
    
    for talk in res_payload:
        talks.append(talk)

    return talks

def create_talks(DK_URL, EVENT_ABBR):
    conference_day_ids = get_conference_day_ids(DK_URL, EVENT_ABBR)
    tracks_list = get_track(DK_URL, EVENT_ABBR)
    
    talks = list()
        
    for day_id in conference_day_ids:
        if day_id['internal']:
            continue
        insert_track_list = list()
        
        for track in tracks_list:
            insert_talks_list = list()
        
            for talk in get_talks(DK_URL, EVENT_ABBR, day_id['id']):
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