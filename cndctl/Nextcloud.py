import logging
logger = logging.getLogger(__name__)

import csv
import json
import sys
import requests
import os

import urllib3
urllib3.disable_warnings()
from nextcloud import NextCloud

class Nextcloud:

    def __init__(self, dk, NEXTCLOUD_URL, NEXTCLOUD_USERNAME, NEXTCLOUD_PASSWORD, NEXTCLOUD_DIR_PATH, EVENT_TALK_FILE_PATH, DRY_RUN) -> None:
        self.dk = dk
        self.NEXTCLOUD_URL = f"https://{NEXTCLOUD_URL}:443"
        self.NEXTCLOUD_USERNAME = NEXTCLOUD_USERNAME
        self.NEXTCLOUD_PASSWORD = NEXTCLOUD_PASSWORD
        self.NEXTCLOUD_DIR_PATH = NEXTCLOUD_DIR_PATH
        self.EVENT_TALK_FILE_PATH = EVENT_TALK_FILE_PATH
        self.DRY_RUN = DRY_RUN

    def put_upload_url(talkid, upload_url, token):
        req_url = "https://event.cloudnativedays.jp/api/v1/talks/{}/video_registration".format(talkid)
        headers = {
            'Authorization': 'Bearer {}'.format(token)
        }
        data = {
            "url":""
        }
        data['url'] = upload_url

        res = requests.put(req_url, headers=headers, data=json.dumps(data))
    
    def dirsync(self):
        print("uploader dirsync command can not use!")
        os.exit()

        talks = {}
        
        # conference_day_ids = self.dk.get_conference_day_ids()
        # for day_id in conference_day_ids:
        #     if day_id['internal'] == True:
        #         continue
        #     talks = self.dk.get_talks(day_id['id'])
        # print(talks)
        talks = csv.DictReader(open(self.EVENT_TALK_FILE_PATH, encoding='utf_8', mode='r'))
        # print("id,title,speaker,url")

        with NextCloud(
                self.NEXTCLOUD_URL,
                user=self.NEXTCLOUD_USERNAME,
                password=self.NEXTCLOUD_PASSWORD,
                session_kwargs={
                    'verify': False
                    }) as nxc:
            nxc_ping = nxc.get_connection_issues()
            if not nxc_ping is None:
                logging.error("Nextcloud connection failed! msg: %s", nxc_ping)
                sys.exit()

            for talk in talks:
                # 休憩などはスキップする
                if talk['abstract'] == "intermission":
                    continue
                
                dir_name = talk['id'] + "_" + talk['title']

                print(f"{self.NEXTCLOUD_DIR_PATH}{dir_name.replace('/', '_')}")
                path = nxc.get_folder(path=f"{self.NEXTCLOUD_DIR_PATH}{dir_name.replace('/', '_')}")['href'][27:-1]

                share_data = list(filter(lambda item : item['path'] == path, nxc.get_shares().data))
                share = ""

                if len(share_data) == 0:
                    print("no share " + path)
                    if not self.DRY_RUN:
                        share = nxc.create_share(path=path, share_type=3)
                        print(share)
                        nxc.update_share(sid=share['id'], public_upload=True, permissions=4)
                        print(talk['id'] + "," + talk['title'] + "," + talk['speaker'] + "," + share['url'])
                else:
                    print("shared " + path + "(" + str(len(share_data)) + ")")
                    share = share_data[0]
                
                # self.put_upload_url(talk['id'], share_data[0]['url'])
                if not self.DRY_RUN:
                    if not self.dk.set_video_registration(talk['id'], share_data[0]['url']):
                        print(f"Failed requests: {talk['id']},{share_data[0]['url']}\n")