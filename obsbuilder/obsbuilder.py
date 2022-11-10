import asyncio
import datetime
import logging
import simpleobsws
import pprint
import json
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.WARNING, format='%(asctime)s [%(levelname)s] [%(name)s] %(message)s')

import dreamkast
import obs

def main():
    DK_URL = "event.cloudnativedays.jp"
    EVENT_ABBR = "cndt2022"
    NEXTCLOUD_BASE_PATH = "/home/ubuntu/Nextcloud/Broadcast/CNDT2022"
    UPLOADER_BASE_PATH = "/home/ubuntu/Nextcloud2/cndt2022"
    NGINX_CONFIGS = {
        "A" : "rtmp://nginx01.cloudnativedays.jp:10002/live/cndt2022-studio-a",
        "B" : "rtmp://nginx01.cloudnativedays.jp:10002/live/cndt2022-studio-b",
        "C" : "rtmp://nginx01.cloudnativedays.jp:10002/live/cndt2022-studio-c",
        "D" : "rtmp://nginx01.cloudnativedays.jp:10002/live/cndt2022-studio-d",
        "E" : "rtmp://nginx01.cloudnativedays.jp:10002/live/cndt2022-remote-e",
        "F" : "rtmp://nginx01.cloudnativedays.jp:10002/live/cndt2022-remote-f"
    }
    OBS_CONFIGS = {
        "host": "192.168.50.254",
        "port": "4444",
        "pass": "password"
    }
    
    parameters = simpleobsws.IdentificationParameters(ignoreNonFatalRequestChecks = False)
    HOST = OBS_CONFIGS["host"]
    PORT = OBS_CONFIGS["port"]
    PASS = OBS_CONFIGS["pass"]
    ws = simpleobsws.WebSocketClient(url = f'ws://{HOST}:{PORT}',
                                     password = PASS,
                                     identification_parameters = parameters)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(obs.init(ws))
    
    talks_days = dreamkast.create_talks(DK_URL, EVENT_ABBR)
    with open('talks_cndt2022.json', 'w') as fp:
        json.dump(talks_days, fp, indent=4, ensure_ascii=False)

    for day in talks_days:
        # print(day['date'])
        
        for track in day['tracks']:
            # print("|-{}".format(track['name']))
            
            scenecollection_name = "{}_{}".format(day['date'], track['name'])
            obs.create_scenecollection(scenecollection_name)
            
            # 調整中シーンを作成する
            obs.create_maintenance_scene(NEXTCLOUD_BASE_PATH)
            
            for talk in track['talks']:
                # start_at = datetime.datetime.fromisoformat(talk['start_at'])
                # start_at_time = "{:d}:{:02d}".format(start_at.hour, start_at.minute)
                
                # end_at = datetime.datetime.fromisoformat(talk['end_at'])
                # end_at_time = "{:d}:{:02d}".format(end_at.hour, end_at.minute)
                
                # print("| |-{}-{}_{}".format(start_at_time, end_at_time, talk['title']))

                if talk['presentation_method'] == "事前収録":
                    obs.create_vidoe_standard(NEXTCLOUD_BASE_PATH, UPLOADER_BASE_PATH, talk)
                elif talk['presentation_method'] == "現地登壇":
                    obs.create_offline_standard(talk, NGINX_CONFIGS)
                elif talk['presentation_method'] == "オンライン登壇":
                    obs.create_online_standard(talk, NGINX_CONFIGS)
                    
                if (talk['is_after_rest']):
                    obs.create_rest_scene(NEXTCLOUD_BASE_PATH, talk)
                    
                obs.delete_default_scene()
    
            if not track['name'] == 'A':
                continue
    
            # scenecollectionごとにリクエストする
            # loop.run_until_complete(obs.send_request(ws, NEXTCLOUD_BASE_PATH))

if __name__ == "__main__":
    main()