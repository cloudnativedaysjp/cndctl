import asyncio
import json
import logging
import pprint
import sys
import simpleobsws

import requests

from .Dreamkast import Dreamkast

logger = logging.getLogger(__name__)
import datetime
import logging


logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s [%(levelname)s] [%(name)s] %(message)s')


class Switcher:

    def __init__(self, nextcloud_base_path: str,
                 uploader_base_path: str) -> None:
        """Switcher関連の初期化

        Args:
            nextcloud_base_path (str): NextcloudのベースPATH
            uploader_base_path (str): UploaderのベースPATH
        """
        self.requests = []
        self.talks = []

        self.nextcloud_base_path = nextcloud_base_path
        self.uploader_base_path = uploader_base_path

    def __generate_scene_name(self, talk: dict) -> str:
        """与えられたTalk情報からシーン名を生成します

        Args:
            talk (dict): 単一のtalk

        Returns:
            str: {TRACK-NAME}_{TALK-ID}_{START-TIME}_{END-TIME}_{TRACK-TITLE} フォーマットの文字列を返します
        """
        start_at = datetime.datetime.fromisoformat(talk['start_at'])
        end_at = datetime.datetime.fromisoformat(talk['end_at'])

        start_at_time = f"{start_at.hour:d}:{start_at.minute:02d}"
        end_at_time = f"{end_at.hour:d}:{end_at.minute:02d}"

        return f"{talk['track_name']}_{talk['id']}_{start_at_time}-{end_at_time}_{talk['title']}"

    def __create_scenecollection(self, scenecollection_name: str) -> None:
        """指定された名前でシーンコレクションを作成します
        作成後は対象のシーンコレクションに切り替わるので注意

        Args:
            scenecollection_name (str): 作成したいシーンコレクションの名前
        """

        self.requests.append(
            simpleobsws.Request('CreateSceneCollection',
                                {'sceneCollectionName': scenecollection_name}))

    # シーンとシーンに紐づくソースをまとめて作成する
    def __create_presentation_scene(self, scene_name: str, input_kind: str,
                                    input_settings: dict) -> None:
        """シーンとシーンに紐づくソースをまとめて作成する

        Args:
            scene_name (str): シーンに利用するシーン名
            input_kind (str): シーンの種類。（Ex: ffmepg_source, vlc_source...）
            input_settings (dict): input_settings としてOBSに渡すソースの設定
        """
        # シーンの作成
        self.requests.append(
            simpleobsws.Request('CreateScene', {'sceneName': scene_name}))

        # インプットソースを作成
        self.requests.append(
            simpleobsws.Request(
                'CreateInput', {
                    'sceneName': scene_name,
                    'inputName': f"{scene_name}_media",
                    'inputKind': input_kind,
                    'inputSettings': input_settings
                }))

        # ソースにFullHDのFilterを追加
        self.requests.append(
            simpleobsws.Request(
                'CreateSourceFilter', {
                    'sourceName': f"{scene_name}_media",
                    'filterName': 'スケーリング/アスペクト比',
                    'filterKind': 'scale_filter',
                    'filterSettings': {
                        'resolution': '1920x1080'
                    }
                }))

    def __create_maintenance_scene(self) -> None:
        """メンテナンスシーンを作成します
        """

        scene_name = "調整中"
        input_kind = "ffmpeg_source"
        input_url = self.nextcloud_base_path + '/Sync/Media/z-common/please_wait(調整中).mp4'

        config = {'local_file': input_url, 'looping': True}

        self.requests.append(
            simpleobsws.Request(
                'CreateInput', {
                    'sceneName': "調整中",
                    'inputName': "調整中_media",
                    'inputKind': 'ffmpeg_source',
                    'inputSettings': {
                        'local_file': self.nextcloud_base_path +
                        '/Sync/Media/z-common/please_wait(調整中).mp4',
                        'looping': True
                    }
                }))

        self.__create_presentation_scene(scene_name, input_kind, config)

    def __create_rest_scene(self, talk: dict) -> None:
        """休憩シーンを作成する

        Args:
            talk (dict): 休憩シーンを作成する直前のプレゼンシーンを渡す
        """
        scene_name = f"{talk['id']}_makuai"
        input_kind = "vlc_source"

        config = {
            "playlist": [
                {
                    # 幕間
                    "hidden":
                    False,
                    "selected":
                    False,
                    "value":
                    f"{self.nextcloud_base_path}/Sync/Media/broadcast-{talk['track_name']}/makuai/0.mp4"
                },
                {
                    # CM をディレクトリとして追加
                    "hidden": False,
                    "selected": False,
                    "value":
                    "{self.nextcloud_base_path}//Sync/Media/z-common/cm"
                },
            ]
        }

        self.__create_presentation_scene(scene_name, input_kind, config)

    def delete_default_scene(self):
        """デフォルトで作成される'シーン'という名前のシーンを削除する
        """
        pass

    def __create_vidoe_standard(self, talk: dict) -> None:
        """事前収録動画フォーマットのシーンを作成する

        Args:
            talk (dict): 作成したい単一セッションのdictオブジェクト
        """

        scene_name = self.__generate_scene_name(talk)
        input_kind = "vlc_source"

        config = {
            "playlist": [
                {
                    # uploader
                    "hidden":
                    False,
                    "selected":
                    False,
                    "value":
                    f"{self.nextcloud_base_path}/Sync/Media/z-common/cndt2022_Countdown60.mp4"
                },
                {
                    # speaker video
                    "hidden": False,
                    "selected": False,
                    "value": f"{self.uploader_base_path}/{talk['title']}.mp4"
                },
            ]
        }

        self.__create_presentation_scene(scene_name, input_kind, config)

    def __create_offline_standard(self, talk: dict,
                                  nginx_configs: dict) -> None:
        """現地登壇フォーマットのシーンを作成する

        Args:
            talk (dict): 作成したい単一セッションのdictオブジェクト
            nginx_configs (dict): Nginxのリストを持つdictオブジェクト
        """
        scene_name = self.__generate_scene_name(talk)
        input_kind = "ffmpeg_source"
        input_url = nginx_configs[talk['track_name']]

        config = {
            "is_local_file": False,
            "restart_on_activate": False,
            "buffering_mb": 2,
            "input": input_url
        }

        self.__create_presentation_scene(scene_name, input_kind, config)

    def __create_online_standard(self, talk: dict,
                                 nginx_configs: dict) -> None:
        """オンライン登壇フォーマットのシーンを作成する

        Args:
            talk (dict): 作成したい単一セッションのdictオブジェクト
            nginx_configs (dict): Nginxのリストを持つdictオブジェクト
        """
        scene_name = self.__generate_scene_name(talk)
        input_kind = "ffmpeg_source"
        input_url = nginx_configs[talk['track_name']]

        config = {
            "is_local_file": False,
            "restart_on_activate": False,
            "buffering_mb": 2,
            "input": input_url
        }

        self.__create_presentation_scene(scene_name, input_kind, config)

    async def build(self, dk: Dreamkast, ws: simpleobsws) -> None:
        """SwitcherのOBSにシーンコレクションを作成します

        Args:
            dk (Dreamkast): Dreamkastのインスタンスオブジェクト
            ws (simpleobsws): simpleobswsのインスタンスオブジェクト
        """
        nginx_configs = {
            "A":
            "rtmp://nginx01.cloudnativedays.jp:10002/live/cndt2022-studio-a",
            "B":
            "rtmp://nginx01.cloudnativedays.jp:10002/live/cndt2022-studio-b",
            "C":
            "rtmp://nginx01.cloudnativedays.jp:10002/live/cndt2022-studio-c",
            "D":
            "rtmp://nginx01.cloudnativedays.jp:10002/live/cndt2022-studio-d",
            "E":
            "rtmp://nginx01.cloudnativedays.jp:10002/live/cndt2022-remote-e",
            "F":
            "rtmp://nginx01.cloudnativedays.jp:10002/live/cndt2022-remote-f"
        }

        talks_days = dk.create_talks()
        with open('talks_cndt2022.json', 'w', encoding="utf-8") as file_pointa:
            json.dump(talks_days, file_pointa, indent=4, ensure_ascii=False)

        for day in talks_days:
            # print(day['date'])

            for track in day['tracks']:

                # print(f"|-{track['name']}")

                scenecollection_name = f"{day['date']}_{track['name']}"
                self.__create_scenecollection(scenecollection_name)

                # 調整中シーンを作成する
                # self.__create_maintenance_scene()

                for talk in track['talks']:
                    # start_at = datetime.datetime.fromisoformat(
                    #     talk['start_at'])
                    # start_at_time = f"{start_at.hour:d}:{start_at.minute:02d}"

                    # end_at = datetime.datetime.fromisoformat(talk['end_at'])
                    # end_at_time = f"{end_at.hour:d}:{end_at.minute:02d}"

                    # print(f"| |-{start_at_time}-{end_at_time}_{talk['title']}")

                    if talk['presentation_method'] == "事前収録":
                        self.__create_vidoe_standard(talk)
                    elif talk['presentation_method'] == "現地登壇":
                        self.__create_offline_standard(talk, nginx_configs)
                    elif talk['presentation_method'] == "オンライン登壇":
                        self.__create_online_standard(talk, nginx_configs)
                    else:
                        print(
                            f"undefined method: {talk['presentation_method']}, talk: {talk}"
                        )

                    # if (talk['is_after_rest']):
                    #     self.__create_rest_scene(talk)

                # scenecollectionごとにリクエストする
                # pprint.pprint(self.requests)
                for request in self.requests:
                    ret = await ws.call(request)
                    if not ret.ok():
                        logger.error(
                            f"Request error. Request:{request} Response:{ret}")
                        # sys.exit()

                # 送信完了したので初期化する
                self.requests = []