import datetime
import simpleobsws
import logging
import sys
import pprint
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.WARNING, format='%(asctime)s [%(levelname)s] [%(name)s] %(message)s')

requests = list()

def generate_scene_name(TALK):
    start_at = datetime.datetime.fromisoformat(TALK['start_at'])
    end_at = datetime.datetime.fromisoformat(TALK['end_at'])
    
    start_at_time = "{:d}:{:02d}".format(start_at.hour, start_at.minute)
    end_at_time = "{:d}:{:02d}".format(end_at.hour, end_at.minute)
    
    return "{}_{}_{}-{}_{}".format(TALK['track_name'], TALK['id'] ,start_at_time, end_at_time, TALK['title'])

async def init(ws):
    await ws.connect()
    await ws.wait_until_identified()

async def send_request(ws, NEXTCLOUD_BASE_PATH):
    global requests
    
    for request in requests:
        ret = await ws.call(request)
        if ret.ok():
            print("Request succeeded! Request:{} Response:{}".format(request, ret))
        else:
            logger.error("Request error. Request:{} Response:{}".format(request, ret))
            sys.exit()
            
    # 送信完了したので初期化する
    requests = list()

def create_scenecollection(SCENECOLLECTION_NAME):
    requests.append(simpleobsws.Request('CreateSceneCollection', {
        'sceneCollectionName': SCENECOLLECTION_NAME
    }))

# シーンとシーンに紐づくソースをまとめて作成する
def create_presentation_scene(SCENE_NAME, INPUT_KIND, INPUT_SETTINGS):
    global requests
    
    # シーンの作成  
    requests.append(simpleobsws.Request('CreateScene', {
        'sceneName': SCENE_NAME
    }))
    
    # インプットソースを作成
    requests.append(simpleobsws.Request('CreateInput', {
        'sceneName': SCENE_NAME,
        'inputName': "{}_media".format(SCENE_NAME),
        'inputKind': INPUT_KIND,
        'inputSettings': INPUT_SETTINGS
    }))

    # ソースにFullHDのFilterを追加
    requests.append(simpleobsws.Request('CreateSourceFilter', {
        'sourceName': "{}_media".format(SCENE_NAME),
        'filterName': 'スケーリング/アスペクト比',
        'filterKind': 'scale_filter',
        'filterSettings': {
            'resolution': '1920x1080'
        }
    }))

def create_maintenance_scene(NEXTCLOUD_BASE_PATH):
    scene_name = "調整中"
    input_kind = "ffmpeg_source"
    input_url = NEXTCLOUD_BASE_PATH + '/Sync/Media/z-common/please_wait(調整中).mp4'
    
    config = {
        'local_file': input_url,
        'looping': True
    }
    
    requests.append(simpleobsws.Request('CreateInput', {
        'sceneName': "調整中",
        'inputName': "調整中_media",
        'inputKind': 'ffmpeg_source',
        'inputSettings': {
            'local_file': NEXTCLOUD_BASE_PATH + '/Sync/Media/z-common/please_wait(調整中).mp4',
            'looping': True
        }
    }))
    
    create_presentation_scene(scene_name, input_kind, config)

def create_rest_scene(NEXTCLOUD_BASE_PATH, TALK):
    scene_name = "{}_makuai".format(TALK['id'])
    input_kind = "vlc_source"
    
    config = {
        "playlist": [
            {
                # 幕間
                "hidden": False,
                "selected": False,
                "value": "{}/Sync/Media/broadcast-{}/makuai/0.mp4".format(NEXTCLOUD_BASE_PATH, TALK['track_name'])
            },
            {
                # CM をディレクトリとして追加
                "hidden": False,
                "selected": False,
                "value": "{}//Sync/Media/z-common/cm".format(NEXTCLOUD_BASE_PATH)
            },
        ]
    }
    
    create_presentation_scene(scene_name, input_kind, config)
    
    requests.append(simpleobsws.Request('CreateInput', {
        'sceneName': f"{name}",
        'inputName':  f"{session['id']}_makuai_media",
        'inputKind': 'vlc_source',
        'inputSettings': {
            'playlist': [
                {
                    'hidden': False,
                    'selected': False,
                    'value': f"/home/ubuntu/Nextcloud/Broadcast/CNSec2022/Sync/Media/broadcast-{session['track_id']}/makuai/{makuai_id}.mp4"
                },
                {
                    'hidden': False,
                    'selected': False,
                    'value': '/home/ubuntu/Nextcloud/Broadcast/CNSec2022/Sync/Media/z-common/cm'
                }
            ]
        }
    }))
    pass

def delete_default_scene():
    pass

def create_vidoe_standard(NEXTCLOUD_BASE_PATH, UPLOADER_BASE_PATH, TALK):
    scene_name = generate_scene_name(TALK)
    input_kind = "vlc_source"
    
    config = {
        "playlist": [
            {
                # uploader
                "hidden": False,
                "selected": False,
                "value": "{}/Sync/Media/z-common/cndt2022_Countdown60.mp4".format(NEXTCLOUD_BASE_PATH)
            },
            {
                # speaker video
                "hidden": False,
                "selected": False,
                "value": "{}/{}.mp4".format(UPLOADER_BASE_PATH, TALK['title'])
            },
        ]
    }
    
    create_presentation_scene(scene_name, input_kind, config)

def create_offline_standard(TALK, NGINX_CONFIGS):
    scene_name = generate_scene_name(TALK)
    input_kind = "ffmpeg_source"
    input_url = NGINX_CONFIGS[TALK['track_name']]
    
    config = {
        "is_local_file": False,
        "restart_on_activate": False,
        "buffering_mb": 2,
        "input": input_url
    }
    
    create_presentation_scene(scene_name, input_kind, config)

def create_online_standard(TALK, NGINX_CONFIGS):
    scene_name = generate_scene_name(TALK)
    input_kind = "ffmpeg_source"
    input_url = NGINX_CONFIGS[TALK['track_name']]
    
    config = {
        "is_local_file": False,
        "restart_on_activate": False,
        "buffering_mb": 2,
        "input": input_url
    }
    
    create_presentation_scene(scene_name, input_kind, config)

def create_simul_standard(TALK):
    pass