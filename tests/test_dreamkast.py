import json
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

talks_data = [
    {
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
        "conferenceDayDate": "2020-09-09",
        "startOffset": 0,
        "endOffset": 0,
        "actualStartTime": "2000-01-01T13:05:00.000+09:00",
        "actualEndTime": "2000-01-01T13:45:00.000+09:00",
        "presentationMethod": "オンライン登壇",
        "slotNum": 2,
    },
    {
        "id": 2,
        "conferenceId": 6,
        "trackId": 1,
        "videoPlatform": None,
        "videoId": "https://dummy/mediapackage/event2022/talks/1433a/12/playlist.m3u8",
        "title": "Simplify Cloud Native Security with Trivy",
        "abstract": "クラウド環境への移行に伴い必要なセキュリティ対策も大きく変化しました。しかしこれらの対策には多くのツールを組み合わせて使う必要があり、導入・学習コストが高くなっています。そこで本発表では、OSSであるTrivyを用いて特に攻撃へと繋がりやすい依存ライブラリの脆弱性や脆弱なインフラ設定、誤ってコミットされたパスワード等の検知を一括で行う方法について説明します。また、実際にCloudFormationやHelmチャートをスキャンすることでデプロイ前に危険な設定を検知するデモを行います。",
        "speakers": [{"id": 11, "name": "Tama"}],
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
        "conferenceDayDate": "2020-09-09",
        "startOffset": 0,
        "endOffset": 0,
        "actualStartTime": "2000-01-01T13:05:00.000+09:00",
        "actualEndTime": "2000-01-01T13:45:00.000+09:00",
        "presentationMethod": "オンライン登壇",
        "slotNum": 2,
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

event_data = [
    {
        "id": 1,
        "name": "CloudNative Days Tokyo 2020",
        "abbr": "cndt2020",
        "status": "archived",
        "theme": "+Native 〜ともに創るクラウドネイティブの世界〜",
        "about": "CloudNative Days はコミュニティ、企業、技術者が一堂に会し、クラウドネイティブムーブメントを牽引することを目的としたテックカンファレンスです。\n最新の活用事例や先進的なアーキテクチャを学べるのはもちろん、ナレッジの共有やディスカッションの場を通じて登壇者と参加者、参加者同士の繋がりを深め、初心者から熟練者までが共に成長できる機会を提供します。\n皆様がクラウドネイティブ技術を適切に選択し、活用し、次のステップに進む手助けになることを願っています。\nクラウドネイティブで、未来を共に創造しましょう。\n",
        "privacy_policy": '#### 個人情報保護方針(プライバシー ポリシー)\n\nご登録頂きました個人情報はイベントの運営会社である株式会社インプレスが管理し、電話/電子メール/郵送等による、各種サービスやセミナー開催情報などの情報提供に利用させて頂きます。 インプレス社の詳しいプライバシーポリシーに関しましては[こちらをご覧下さい。](https://www.impress.co.jp/privacy.html)\n\nなお、今回ご登録いただきました個人情報は、本セミナー協賛企業（各種スポンサー）へ提供いたします。以下に記載の協賛企業からご登録者の皆様に、直接電子メールや郵送でご案内をさせていただく場合がございます。\n\nリスト提供企業社名一覧（順不同）\n\n- 日本アイ・ビー・エム株式会社\n- 富士通株式会社\n- F5ネットワークスジャパン合同会社\n- New Relic株式会社\n- JFrog Japan株式会社\n- サイオステクノロジー株式会社\n- 株式会社はてな\n- CircleCI合同会社\n- 株式会社ディバータ\n- Sysdig Japan合同会社\n- 株式会社カサレアル\n- グーグル・クラウド・ジャパン合同会社\n- 株式会社サイバーエージェント\n- 日本オラクル株式会社\n- レッドハット株式会社\n- 株式会社エヌ・ティ・ティ・データ\n- Canonical/Ubuntu\n- 日本マイクロソフト株式会社/Microsoft Corporation\n- GMOペパボ株式会社\n- SUSE ソフトウエア ソリューションズ ジャパン株式会社\n- ヴイエムウェア株式会社\n- 株式会社LegalForce\n- Linux Foundation\n- ミランティス・ジャパン株式会社\n- Elastic\n- Rancher Labs, Inc.\n- 日本電気株式会社\n- Linux Foundation\n\n業務委託先または提携先へ業務預託する場合がございますが、個人情報をお客様の承諾なしに目的外利用すること、及び第三者に提供することはございません。なお、開催日までに協賛企業（各種スポンサー）、講演提供企業が追加となりました場合は、セミナーWebサイトに公開しますとともに、追加となりました協賛企業ともご登録情報を共有させていただきます。あらかじめご了承の上、お申し込みをお願いいたします。\n\n#### IBMおよびIBMの⼦会社、関連会社からの情報提供\n\nIBMおよび [IBMの⼦会社、関連会社](https://www.ibm.com/ibm/jp/ja/keireki.pdf#subsidiaries) から、製品、サービス、オファリングに関する情報をお送りさせていただく場合があります。\n\nマーケティングに関する同意は、 [opt-out request](https://www.ibm.com/account/reg/jp-ja/signup?formid=urx-42537) を送信することにより、いつでも取り消すことができます。また、該当のEメール内の、購読を中⽌するためのリンクをクリックすることで、マーケティングに関するEメールの受信を中⽌することができます。 処理に関する詳しい情報は、<a href="https://www.ibm.com/privacy/jp/ja/" target="_blank">IBMプライバシー・ステートメント</a>をご覧ください。このフォームを送信することで、私はIBMプライバシー・ステートメントを読み、これを理解したものとします。\n\n#### 日本マイクロソフト株式会社/Microsoft Corporationからの情報提供\n\n日本マイクロソフト株式会社/Microsoft Corporationから情報提供を希望される場合、申し込み者情報に記載いただいた内容を日本マイクロソフト株式会社/Microsoft Corporationへ提供させていただきます。利用目的は当該企業の製品・サービスに関する情報またはマーケティング活動に関する情報をお知らせすることです。個人情報の取り扱いにつきましては、日本マイクロソフト株式会社/Microsoft Corporationのプライバシーポリシーに準拠します\n\n[プライバシーステートメント](https://privacy.microsoft.com/ja-jp/privacystatement/)',
        "privacy_policy_for_speaker": "",
        "copyright": "© CloudNative Days Tokyo 2020 (Secretariat by Impress Corporation)",
        "coc": "#### Code of Conduct (行動規範)\n\nイベント主催者は、参加者が人権侵害や差別を受けることのないよう努力しています。本イベントは技術情報の共有や技術者同士のコラボレーションを目指したものです。講演者、来場者、スポンサー、展示関係者、スタッフなどすべての参加者は、いかなる形でもハラスメントに関わってはなりません。\n\nハラスメント行為を目撃したり懸念を感じた場合はCloudNative Days 実行委員会 [@cloudnativedays](https://twitter.com/cloudnativedays) まで速やかにお知らせください。（この行動規範はLinux Foundationのドキュメントを参考にしています）\n\n##### 容認できない行為\n\n- 性的な言語や画像の使用\n- 個人的な攻撃\n- 侮辱/軽蔑的なコメント\n- 公的または私的なハラスメント\n- 許可なく他人の個人情報を公開すること\n- その他の非倫理的な行為\n",
        "conferenceDays": [
            {"id": 3, "date": "2020-09-02", "internal": True},
            {"id": 1, "date": "2020-09-08", "internal": False},
            {"id": 2, "date": "2020-09-09", "internal": False},
            {"id": 4, "date": "2020-09-09", "internal": True},
            {"id": 5, "date": "2020-09-09", "internal": True},
        ],
    },
    {
        "id": 2,
        "name": "CloudNative Days Spring 2021 ONLINE",
        "abbr": "cndo2021",
        "status": "archived",
        "theme": "ともに踏み出す CloudNative祭",
        "about": "    『クラウドネイティブ』って何だっけ？ 私たち自身ずっと考えてきました。\n    CNCFによる定義によると、『近代的でダイナミックな環境で、スケーラブルなアプリケーションを構築・実行するための能力を組織にもたらす』のがクラウドネイティブ技術です。\n    また、オープンソースでベンダー中立なエコシステムを育成・維持し、このパラダイムの採用を促進したいとも述べられています。\n    私たちはこの考えに賛同します。クラウドネイティブ技術を日本にも浸透させるべく、過去数年にわたりイベントを行ってきました。\n\n    しかし世の中が大きく変わりつつある昨今。我々はこう考えました。\n    『今ならオンラインの特性を生かして、CloudNative Daysをダイナミックな環境でスケーラブルな形に更に進化させられるのではないか？』\n\n    オンラインでは、誰でも情報を得ることができ、誰もが発信することもできます。オープンな思想のもとに作られたインターネットには境界がありません。\n    そうしたインターネットの成り立ちを思い出し、初心者から達人まで、住んでいる場所を問わず、クラウドネイティブに取り組む人が、\n\n    ・今まで参加者だった人が壁を感じずに発信できる\n    ・参加者が、これまで以上に多様な視点から学びを得られる\n\n    そんな機会を創り出し、登壇者・参加者・イベント主催者といった垣根を超えて、クラウドネイティブ・コミュニティを広げていきたいと考えています。\n    CloudNative Days Spring 2021 Onlineでは、クラウドネイティブ技術を通じて培った知見やマインドセットを最大限に活用し、これまでに無かった斬新なイベントを目指しています。\n",
        "privacy_policy": "#### 個人情報保護方針(プライバシー ポリシー)\n\nご登録頂きました個人情報はイベントの運営会社である株式会社インプレスが管理し、電話/電子メール/郵送等による、各種サービスやセミナー開催情報などの情報提供に利用させて頂きます。\nインプレス社の詳しいプライバシーポリシーに関しましては[こちらをご覧下さい。](https://www.impress.co.jp/privacy.html)\n\nなお、今回ご登録いただきました個人情報は、本セミナー協賛企業（各種スポンサー）へ提供いたします。以下に記載の協賛企業からご登録者の皆様に、直接電子メールや郵送でご案内をさせていただく場合がございます。\n\nリスト提供企業社名一覧（順不同）\n\n- CircleCI合同会社\n- New Relic株式会社\n- GMOインターネットグループ\n- JFrog Japan株式会社\n- SUSE ソフトウエア ソリューションズ ジャパン株式会社\n- アクイアジャパン合同会社\n- LINE株式会社\n- SCSK株式会社\n- Datadog Japan 合同会社\n- ヴイエムウェア株式会社\n- レッドハット株式会社\n- F5ネットワークスジャパン合同会社／NGINX\n- 日本マイクロソフト株式会社\n- 株式会社クラウドネイティブ\n\n業務委託先または提携先へ業務預託する場合がございますが、個人情報をお客様の承諾なしに目的外利用すること、及び第三者に提供することはございません。\nなお、開催日までに協賛企業（各種スポンサー）、講演提供企業が追加となりました場合は、セミナーWebサイトに公開しますとともに、追加となりました協賛企業ともご登録情報を共有させていただきます。あらかじめご了承の上、お申し込みをお願いいたします。\n",
        "privacy_policy_for_speaker": "#### 登壇者向け 個人情報保護方針(プライバシー ポリシー)\n\nご登録頂きました個人情報はイベントの運営会社である株式会社インプレスが管理し、電話/電子メール/郵送等による、各種サービスやセミナー開催情報などの情報提供に利用させて頂きます。\nインプレス社の詳しいプライバシーポリシーに関しましては[こちらをご覧下さい。](https://www.impress.co.jp/privacy.html)\n\nなお、今回ご登録いただきました個人情報は、本イベントの運営に必要な範囲でのみ利用致します。\n業務委託先または提携先へ業務預託する場合がございますが、個人情報をお客様の承諾なしに目的外利用すること、及び第三者に提供することはございません。\nあらかじめご了承の上、お申し込みをお願いいたします。\n",
        "copyright": "© CloudNative Days Spring 2021 ONLINE (Secretariat by Impress Corporation)",
        "coc": "#### Code of Conduct (行動規範)\n\nイベント主催者は、参加者が人権侵害や差別を受けることのないよう努力しています。本イベントは技術情報の共有や技術者同士のコラボレーションを目指したものです。講演者、来場者、スポンサー、展示関係者、スタッフなどすべての参加者は、いかなる形でもハラスメントに関わってはなりません。\n\nハラスメント行為を目撃したり懸念を感じた場合はCloudNative Days 実行委員会 [@cloudnativedays](https://twitter.com/cloudnativedays) まで速やかにお知らせください。（この行動規範はLinux Foundationのドキュメントを参考にしています）\n\n##### 容認できない行為\n\n- 性的な言語や画像の使用\n- 個人的な攻撃\n- 侮辱/軽蔑的なコメント\n- 公的または私的なハラスメント\n- 許可なく他人の個人情報を公開すること\n- その他の非倫理的な行為\n",
        "conferenceDays": [
            {"id": 8, "date": "2021-02-26", "internal": True},
            {"id": 6, "date": "2021-03-11", "internal": False},
            {"id": 7, "date": "2021-03-12", "internal": False},
        ],
    },
]


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

                with mock.patch.object(dk, "_Dreamkast__request_dk_api") as mock_put:
                    mock_put.return_value = {"message": "success"}

                    # execute
                    dk.onair(talk_id)

                    # verify
                    assert mock_put.return_value["message"] == "success"


def test_onair_next():
    # prepare
    # テスト用の入力値を設定.
    answer = "y"
    sys.stdin = StringIO(answer)
    dk = new_dreamkast()
    track_name = "A"
    event_date = "2020-09-09"

    with mock.patch("cndctl.Dreamkast.requests.get") as mock_get:
        mock_get.return_value = new_http_response(
            status_code=200, reason="OK", content=json.dumps(event_data).encode("utf-8")
        )

        with mock.patch.object(dk, "get_talks") as mock_get_talks:
            mock_get_talks.return_value = talks_data

            with mock.patch.object(dk, "get_track") as mock_get_track:
                mock_get_track.return_value = tracks_data

                with mock.patch.object(dk, "get_talk") as mock_get_track:
                    mock_get_track.return_value = current_talk_data

                    # execute
                    result = dk.onair_next(track_name=track_name, event_date=event_date)

                    # verify
                    assert result == True
