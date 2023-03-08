import logging

logger = logging.getLogger(__name__)
import datetime
import json
import os
import sys

import jwt
import requests

from .Cli import Cli


class Dreamkast:
    def __init__(
        self, dk_url, auth0_url, client_id, client_secrets, event_abbr
    ) -> None:
        self.dk_url = dk_url
        self.auth0_url = auth0_url
        self.client_id = client_id
        self.client_secrets = client_secrets
        self.event_abbr = event_abbr

    def __read_token(self, env_file_path):
        token_file = open(env_file_path, "r", encoding="utf-8")
        token = token_file.read()
        token_file.close()

        return token

    def __check_dk_env(self, env_file_path):
        if os.path.isfile(env_file_path):
            token = self.__read_token(env_file_path=env_file_path)
        else:
            print(
                f"The '{env_file_path}' not found. Please, generate token using 'cndctl dk update'"
            )
            return False

        if not token:
            print(f"token '{env_file_path}' is empty")
            return False

        token_payload = jwt.decode(token, options={"verify_signature": False})
        token_expire = datetime.datetime.fromtimestamp(token_payload["exp"])

        if datetime.datetime.now() < token_expire:
            return True
        else:
            print("The token is expired. Please update using `cndctl dk update`")
            return False

    # cndctl dk update
    def update(self):
        logger.debug("dreamkast_update()")
        env_file_path = ".dk.env"
        cli = Cli()

        if self.__check_dk_env(env_file_path=env_file_path):
            print("token not expired")
            sys.exit()

        msg = "Dk token update ok?"
        if not cli.accept_continue(msg):
            sys.exit()

        req_url = "https://" + self.auth0_url + "/oauth/token"
        headers = {"content-type": "application/json"}
        data = {
            "client_id": "",
            "client_secret": "",
            "audience": "https://event.cloudnativedays.jp/",
            "grant_type": "client_credentials",
        }
        data["client_id"] = self.client_id
        data["client_secret"] = self.client_secrets

        res = requests.post(req_url, headers=headers, data=json.dumps(data))
        res.raise_for_status()
        res_payload = res.json()
        print("token update successfully ({})".format(res_payload))

        token_file = open(".dk.env", "w", encoding="utf-8")
        token_file.write(res_payload["access_token"])
        token_file.close()

    def talks(self):
        logger.debug("dreamkast_update()")

    def put_upload_url(talkid, upload_url, token):
        req_url = "https://event.cloudnativedays.jp/api/v1/talks/{}/video_registration".format(
            talkid
        )
        headers = {"Authorization": "Bearer {}".format(token)}
        data = {"url": ""}
        data["url"] = upload_url

        res = requests.put(req_url, headers=headers, data=json.dumps(data))

    def set_video_registration(self, talkid: int, video_drop_url: str) -> bool:
        """talkごとのアップロードURLをセットします

        Args:
            talkid (int): セットしたいtalkのid
            video_drop_url (str): 登壇者がアップロードするNextcloudのURL

        Returns:
            bool: リクエストが成功した場合はTrue, それ以外はFalseを返します
        """

        res = self.__request_dk_api(
            f"/talks/{talkid}/video_registration", "put", video_drop_url
        )

        if res["message"] == "OK":
            return True
        else:
            return False

    def __request_dk_api(
        self, api_path: str, method: str, data: dict = {}, param: str = ""
    ) -> dict:
        """DKへAPIリクエストし、レスポンスボディを返します

        Args:
            api_path (str): /api/v1配下のPATHを指定します（ex: /talks）
            param (str): リクエスト時に付与するURLパラメーターを指定します（ex: ?eventAbbr=cndt2022）
            method (str): リクエスト形式を指定します（get, put, post）
            data (dict): データを送信する場合は、送信するデータを指定します。

        Returns:
            dict: レスポンスボディを返します
        """
        if not self.__check_dk_env(env_file_path=".dk.env"):
            logging.error(f"failed check env file. Please type 'dk update'")
            return {}

        token = self.__read_token(env_file_path=".dk.env")

        if not param == "":
            param = f"?{param}"

        req_url = f"https://{self.dk_url}/api/v1{api_path}{param}"
        headers = {"Authorization": f"Bearer {token}"}
        logging.debug(
            "request\nmethod: %s\nurl   : %s\nheader: %s\ndata  : %s",
            method,
            req_url,
            headers,
            data,
        )

        if method == "get":
            res = requests.get(req_url, headers=headers)
        elif method == "put":
            res = requests.put(req_url, headers=headers, data=json.dumps(data))
        elif method == "post":
            res = requests.post(req_url, headers=headers, data=json.dumps(data))
        else:
            logging.error("undefined request method: %s", method)
            return {}

        res.raise_for_status()
        res_payload = res.json()
        return res_payload

    def get_current_onair_talk(self, track_id: int) -> dict:
        tracks = self.get_track()
        for track in tracks:
            if track["id"] == track_id and track["onAirTalk"] is not None:
                return self.get_talk(track["onAirTalk"]["talk_id"])
            else:
                return {"id": 0, "title": "None"}

    def get_track_talks(self, track_name, conference_day_id) -> list:
        talks = self.get_talks(conference_day_id)
        tracks = self.get_track()
        track_id = 0
        for track in tracks:
            if track["name"] == track_name:
                track_id = track["id"]

        talks_for_track = [talk for talk in talks if talk["trackId"] == track_id]
        return talks_for_track

    def get_track_talks_cmd(self, track_name: str, event_date: str) -> None:
        talks = self.get_talks_in_track_and_event_date(track_name, event_date)
        for talk in talks:
            talk["start_at"] = datetime.datetime.fromisoformat(
                talk["actualStartTime"]
            ).time()
            talk["end_at"] = datetime.datetime.fromisoformat(
                talk["actualEndTime"]
            ).time()
            talk["duration"] = datetime.datetime.fromisoformat(
                talk["actualEndTime"]
            ) - datetime.datetime.fromisoformat(talk["actualStartTime"])

        tracks = self.get_track()
        track_id = self.get_track_id(track_name, tracks)
        current_onair_talk_id = self.get_current_onair_talk(track_id)["id"]
        for talk in sorted(talks, key=lambda x: x["start_at"]):
            onair_status = " "
            if current_onair_talk_id == talk["id"]:
                onair_status = "*"
            print(
                f"{onair_status} {talk['id']} [{talk['start_at']} - {talk['end_at']}]({talk['duration']}): {talk['title']}"
            )

    def onair_next(self, track_name: str, event_date: str):
        talks = self.get_talks_in_track_and_event_date(track_name, event_date)

        for talk in talks:
            talk["start_at"] = datetime.datetime.fromisoformat(
                talk["actualStartTime"]
            ).time()
            talk["end_at"] = datetime.datetime.fromisoformat(
                talk["actualEndTime"]
            ).time()
            talk["duration"] = datetime.datetime.fromisoformat(
                talk["actualEndTime"]
            ) - datetime.datetime.fromisoformat(talk["actualStartTime"])

        tracks = self.get_track()
        track_id = self.get_track_id(track_name, tracks)
        current_onair_talk_id = self.get_current_onair_talk(track_id)["id"]

        sorted_talks = sorted(talks, key=lambda x: x["start_at"])
        for i, talk in enumerate(sorted_talks):
            if current_onair_talk_id == talk["id"]:
                if len(sorted_talks) != i + 1:
                    # 最後のtalk以外の場合、オンエア切り替えを実施.
                    self.onair(sorted_talks[i + 1]["id"])

    def onair(self, dk_talk_id):
        cli = Cli()

        next_talk = self.get_talk(dk_talk_id)
        next_talk_track_id = next_talk["trackId"]
        track_name = self.get_track_name(next_talk_track_id)["name"]
        current_talk = self.get_current_onair_talk(next_talk_track_id)

        print(f"Track: {track_name}")
        # OnAirなTalkがない場合の対応
        if current_talk["id"] == 0:
            print(f"current talk | No onAir 'Track {track_name}!'")
        else:
            print(
                f"current talk | id: {current_talk['id']} title: {current_talk['title']}"
            )
        print(f"next    talk | id: {next_talk['id']} title: {next_talk['title']}")

        msg = f"Change onair to '{dk_talk_id}'"
        if not cli.accept_continue(msg):
            sys.exit()

        path = f"/talks/{dk_talk_id}"
        data = {"on_air": True}

        print(self.__request_dk_api(path, "put", data)["message"])

    def get_track(self):
        logger.debug("get_track_name()")

        req_url = (
            "https://"
            + self.dk_url
            + "/api/v1/tracks?eventAbbr={}".format(self.event_abbr)
        )
        res = requests.get(req_url)
        res.raise_for_status()
        res_payload = res.json()

        return res_payload

    def get_track_name(self, TRACK_ID):
        logger.debug("get_track_name")

        tracks = self.get_track()
        for track in tracks:
            if track["id"] == TRACK_ID:
                return track

    def get_conference_day_ids(self):
        logger.debug("get_conference_day_ids()")

        req_url = "https://" + self.dk_url + "/api/v1/events"
        res = requests.get(req_url)
        res.raise_for_status()
        res_payload = res.json()

        # get event id
        i = 0
        event_list_position = 0
        for event in res_payload:
            if event["abbr"] == self.event_abbr:
                event_list_position = i
            i += 1

        return res_payload[event_list_position]["conferenceDays"]

    def get_talks(self, conference_day_id):
        talks = []

        req_url = f"https://{self.dk_url}/api/v1/talks?eventAbbr={self.event_abbr}&conferenceDayIds={conference_day_id}"
        logging.debug("request url: %s", req_url)
        res = requests.get(req_url)
        res.raise_for_status()
        res_payload = res.json()

        for talk in res_payload:
            talks.append(talk)

        return talks

    def get_talks_cmd(self):
        day_ids = self.get_conference_day_ids()

        talks = list()
        for day_id in day_ids:
            talks.extend(self.get_talks(day_id["id"]))

        print(json.dumps(talks, ensure_ascii=False))

    def get_talk(self, talk_id):
        req_url = f"https://{self.dk_url}/api/v1/talks/{talk_id}"
        logging.debug("request url: %s", req_url)
        res = requests.get(req_url)
        res.raise_for_status()

        return res.json()

    def request_dk_get(self, path, data):
        res = self.__request_dk_api(path, "get", data)
        print(json.dumps(res, ensure_ascii=False))

    def create_talks(self):
        if not self.__check_dk_env(".dk.env"):
            print("token expired. please type 'cndctl dk update'")
            sys.exit()
        conference_day_ids = self.get_conference_day_ids()
        tracks_list = self.get_track()

        talks = list()

        for day_id in conference_day_ids:
            if day_id["internal"]:
                continue
            insert_track_list = list()

            for track in tracks_list:
                insert_talks_list = list()

                for talk in self.get_talks(day_id["id"]):
                    if not track["id"] == talk["trackId"]:
                        continue

                    # change start_at date
                    start_at = datetime.datetime.fromisoformat(
                        talk["actualStartTime"]
                    ).replace(
                        year=int(day_id["date"].split("-")[0]),
                        month=int(day_id["date"].split("-")[1]),
                        day=int(day_id["date"].split("-")[2]),
                    )
                    # change end_at date
                    end_at = datetime.datetime.fromisoformat(
                        talk["actualEndTime"]
                    ).replace(
                        year=int(day_id["date"].split("-")[0]),
                        month=int(day_id["date"].split("-")[1]),
                        day=int(day_id["date"].split("-")[2]),
                    )

                    talk_time = int((end_at - start_at).seconds / 60)

                    is_after_rest = False

                    insert_talk = {
                        "id": talk["id"],
                        "title": talk["title"],
                        "abstract": talk["abstract"],
                        "category": talk["talkCategory"],
                        "start_at": start_at.isoformat(),
                        "end_at": end_at.isoformat(),
                        "start_offset": talk["startOffset"],
                        "end_offset": talk["endOffset"],
                        "talk_time": talk_time,
                        "is_after_rest": is_after_rest,
                        "track_id": talk["trackId"],
                        "track_name": track["name"],
                        "presentation_method": talk["presentationMethod"],
                        "scene_template": "",
                    }
                    insert_talks_list.append(insert_talk)

                insert_talks_list.sort(key=lambda x: x["start_at"])
                insert_track = {
                    "id": track["id"],
                    "name": track["name"],
                    "talks": insert_talks_list,
                }
                insert_track_list.append(insert_track)

            insert_track_list.sort(key=lambda x: x["name"])
            talks_info = {"date": day_id["date"], "tracks": insert_track_list}
            talks.append(talks_info)

        return talks

    def get_talks_in_track_and_event_date(
        self, track_name: str, event_date: str
    ) -> list:
        day_ids = self.get_conference_day_ids()
        for day_id in day_ids:
            if day_id["date"] == event_date:
                return self.get_track_talks(track_name, day_id["id"])

    def get_track_id(self, want_track_name: str, tracks: list) -> int:
        for track in tracks:
            if track["name"] == want_track_name:
                return track["id"]
