import sys
import unittest.mock as mock
from io import StringIO

import requests

from cndctl.Dreamkast import Dreamkast

tracks_data = [
    {
        "id": 1,
        "name": "A",
        "videoPlatform": "ivs",
        "videoId": 1,
        "channelArn": 1,
        "onAirTalk": {
            "id": 1,
            "talk_id": 1,
            "site": "",
            "url": "",
            "on_air": True,
            "created_at": "2022-08-04T03:20:57.000+09:00",
            "updated_at": "2022-08-05T18:45:51.000+09:00",
            "video_id": "",
            "slido_id": "",
            "video_file_data": "",
        },
    },
    {
        "id": 2,
        "name": "B",
        "videoPlatform": "ivs",
        "videoId": 2,
        "channelArn": 2,
        "onAirTalk": {
            "id": 2,
            "talk_id": 2,
            "site": "",
            "url": "",
            "on_air": True,
            "created_at": "2022-08-04T03:20:57.000+09:00",
            "updated_at": "2022-08-05T18:45:51.000+09:00",
            "video_id": "",
            "slido_id": "",
            "video_file_data": "",
        },
    },
    {
        "id": 3,
        "name": "C",
        "videoPlatform": "ivs",
        "videoId": 3,
        "channelArn": 3,
        "onAirTalk": {
            "id": 3,
            "talk_id": 3,
            "site": "",
            "url": "",
            "on_air": True,
            "created_at": "2022-08-04T03:20:57.000+09:00",
            "updated_at": "2022-08-05T18:45:51.000+09:00",
            "video_id": "",
            "slido_id": "",
            "video_file_data": "",
        },
    },
]

current_talk_data = {
    "id": 1,
    "conferenceId": 6,
    "trackId": 1,
    "videoPlatform": None,
    "videoId": "https://dummy/mediapackage/event2022/talks/1433a/12/playlist.m3u8",
    "title": "Simplify Cloud Native Security with Trivy",
    "abstract": "クラウド環境への移行に伴い必要なセキュリティ対策も大きく変化しました。しかしこれらの対策には多くのツールを組み合わせて使う必要があり、導入・学習コストが高くなっています。そこで本発表では、OSSであるTrivyを用いて特に攻撃へと繋がりやすい依存ライブラリの脆弱性や脆弱なインフラ設定、誤ってコミットされたパスワード等の検知を一括で行う方法について説明します。また、実際にCloudFormationやHelmチャートをスキャンすることでデプロイ前に危険な設定を検知するデモを行います。",
    "speakers": [{"id": 10, "name": "Tama"}],
    "dayId": 10,
    "showOnTimetable": True,
    "startTime": "2000-01-01T13:05:00.000+09:00",
    "endTime": "2000-01-01T13:45:00.000+09:00",
    "talkDuration": 0,
    "talkDifficulty": "初級者",
    "talkCategory": "",
    "onAir": True,
    "documentUrl": "https://speakerdeck.com/knqyf263/simplify-cloud-native-security-with-trivy/",
    "conferenceDayId": 10,
    "conferenceDayDate": "2022-08-05",
    "startOffset": 0,
    "endOffset": 0,
    "actualStartTime": "2000-01-01T13:05:00.000+09:00",
    "actualEndTime": "2000-01-01T13:45:00.000+09:00",
    "presentationMethod": "オンライン登壇",
    "slotNum": 2,
}


def new_dreamkast() -> Dreamkast:
    dk_url = "dummy_url"
    auth0_url = "dummy_auth0_url"
    client_id = "dummy_client_id"
    client_secrets = "dummy_client_secrets"
    event_abbr = "dummy_event_abbr"

    return Dreamkast(
        dk_url=dk_url,
        auth0_url=auth0_url,
        client_id=client_id,
        client_secrets=client_secrets,
        event_abbr=event_abbr,
    )


def new_http_response(
    status_code: int, reason: str, content: bytes
) -> requests.models.Response:
    mock_response = requests.models.Response()
    mock_response.status_code = status_code
    mock_response.reason = reason
    mock_response._content = content
    return mock_response


@mock.patch("builtins.open", new_callable=mock.mock_open)
def test_token_update(mock_file):
    # prepare
    # テスト用の入力値を設定.
    answer = "y"
    sys.stdin = StringIO(answer)
    dk = new_dreamkast()

    # GitHub上には「.dk.env」は存在しないため、偽の値を返す.
    with mock.patch("cndctl.Dreamkast.os.path.isfile") as mock_isfile:
        with mock.patch("cndctl.Dreamkast.requests.post") as mock_post:
            mock_isfile.return_value = False
            mock_post.return_value = new_http_response(
                status_code=200,
                reason="OK",
                content=b'{"message": "success", "access_token": "dummy_access_token"}',
            )

            # execute
            dk.update()

            # verify
            mock_file.assert_called_with(".dk.env", "w", encoding="utf-8")
            mock_file.return_value.write.assert_called_once_with("dummy_access_token")


def test_put_upload_url():
    # prepare
    dk = new_dreamkast()
    talk_id = 1
    put_upload_url = "https://dummy_url"
    token = "dummy_token"

    with mock.patch("cndctl.Dreamkast.requests.put") as mock_put:
        mock_put.return_value = new_http_response(
            status_code=204,
            reason="No Content",
            content=b'{"message": "success"}',
        )

        # execute
        dk.put_upload_url(talk_id, put_upload_url, token)

        # verify
        assert mock_put.return_value.status_code == 204


def test_onair():
    # prepare
    # テスト用の入力値を設定.
    answer = "y"
    sys.stdin = StringIO(answer)
    dk = new_dreamkast()
    talk_id = 1

    with mock.patch("cndctl.Dreamkast.requests.get") as mock_get:
        mock_get.return_value = new_http_response(
            status_code=200,
            reason="OK",
            content=b'{"message": "success", "access_token": "dummy_access_token", "trackId": 1}',
        )
        with mock.patch.object(dk, "get_track") as mock_get_track:
            mock_get_track.return_value = tracks_data

            with mock.patch.object(dk, "get_talk") as mock_get_track:
                mock_get_track.return_value = current_talk_data
                # execute

                with mock.patch.object(dk, "_Dreamkast__request_dk_api") as mock_put:
                    mock_put.return_value = {"message": "success"}
                    dk.onair(talk_id)

                    # verify
                    assert mock_put.return_value["message"] == "success"
