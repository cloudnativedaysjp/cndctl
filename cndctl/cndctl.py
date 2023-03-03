import logging

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s [%(levelname)s] [%(name)s] %(message)s')

from .Dreamkast import Dreamkast
from .MediaSource import MediaSource
from .Scene import Scene
from .Source import Source
from .Switcher import Switcher
from .Nextcloud import Nextcloud

import argparse
import asyncio
import json
import os
import sys

import simpleobsws

parser = argparse.ArgumentParser(description="obs remote controll cli tool")
parser.add_argument("object")
parser.add_argument("operator")
parser.add_argument("--secret")
parser.add_argument("--obs-host")
parser.add_argument("--obs-port")
parser.add_argument("--obs-password")
parser.add_argument("--dk-url")
parser.add_argument("--dk-auth0-url")
parser.add_argument("--dk-client-id")
parser.add_argument("--dk-client-secrets")
parser.add_argument("--dk-talk-id")
parser.add_argument("--event-abbr")
parser.add_argument("--event-date")
parser.add_argument("--track")
parser.add_argument("--sceneName")
parser.add_argument("--sourceName")
parser.add_argument("--api-path")
parser.add_argument("--api-data")
parser.add_argument("--dry-run", action='store_true')

args = parser.parse_args()

OBS_HOST = ""
OBS_PORT = ""
OBS_PASS = ""
DK_URL = ""
DK_CLIENT_ID = ""
DK_CLIENT_SECRETS = ""
DK_AUTH0_URL = ""
DK_TALK_ID = ""
DK_API_PATH = ""
DK_API_METHOD = ""
DK_API_DATA = ""
EVENT_TRACK = ""
EVENT_ABBR = ""
EVENT_DATE = ""
DRY_RUN = False

# envirouments
if "WSHOST" in os.environ:
    OBS_HOST = os.environ["WSHOST"]
if "WSPORT" in os.environ:
    OBS_PORT = os.environ["WSPORT"]
if "WSPASS" in os.environ:
    OBS_PASS = os.environ["WSPASS"]
if "DK_URL" in os.environ:
    DK_URL = os.environ["DK_URL"]
if "DK_AUTH0_URL" in os.environ:
    DK_URL = os.environ["DK_AUTH0_URL"]
if "DK_CLIENT_ID" in os.environ:
    DK_CLIENT_ID = os.environ["DK_CLIENT_ID"]
if "DK_CLIENT_SECRET" in os.environ:
    DK_CLIENT_SECRETS = os.environ["DK_CLIENT_SECRET"]
if "EVENT_ABBR" in os.environ:
    EVENT_ABBR = os.environ["EVENT_ABBR"]

# json

if args.secret:
    with open(args.secret, encoding="utf-8") as f:
        secret = json.loads(f.read())

    if "obs" in secret:
        obs = secret['obs']
        logger.debug(obs)

        if "host" in secret['obs'] and secret['obs']['host']:
            OBS_HOST = secret['obs']['host']
        if "port" in secret['obs'] and secret['obs']['port']:
            OBS_PORT = secret['obs']['port']
        if "password" in secret['obs'] and secret['obs']['password']:
            OBS_PASS = secret['obs']['password']

    if "dreamkast" in secret:
        if "url" in secret['dreamkast'] and secret['dreamkast']['url']:
            DK_URL = secret['dreamkast']['url']
        if "auth0_url" in secret['dreamkast'] and secret['dreamkast'][
                'auth0_url']:
            DK_AUTH0_URL = secret['dreamkast']['auth0_url']
        if "client_id" in secret['dreamkast'] and secret['dreamkast'][
                'client_id']:
            DK_CLIENT_ID = secret['dreamkast']['client_id']
        if "client_secrets" in secret['dreamkast'] and secret['dreamkast'][
                'client_secrets']:
            DK_CLIENT_SECRETS = secret['dreamkast']['client_secrets']
        if "event_abbr" in secret['dreamkast'] and secret['dreamkast'][
                'event_abbr']:
            EVENT_ABBR = secret['dreamkast']['event_abbr']

    if "nextcloud" in secret:
        if "url" in secret['nextcloud'] and secret['nextcloud']['url']:
            UPLOADER_URL = secret['nextcloud']['url']
        if "base_path" in secret['nextcloud'] and secret['nextcloud']['base_path']:
            UPLOADER_BASE_DIR = secret['nextcloud']['base_path']
        if "user" in secret['nextcloud'] and secret['nextcloud']['user']:
            UPLOADER_USER = secret['nextcloud']['user']
        if "pass" in secret['nextcloud'] and secret['nextcloud']['pass']:
            UPLOADER_PASS = secret['nextcloud']['pass']
        if "event_talk_file_path" in secret['nextcloud'] and secret['nextcloud']['event_talk_file_path']:
            UPLOADER_TALK_FILE_PATH = secret['nextcloud']['event_talk_file_path']

# command option
if args.obs_host:
    OBS_HOST = args.obs_host
if args.obs_port:
    OBS_PORT = args.obs_port
if args.obs_password:
    OBS_PASS = args.obs_password
if args.dk_url:
    DK_URL = args.dk_url
if args.dk_auth0_url:
    DK_AUTH0_URL = args.dk_auth0_url
if args.dk_client_id:
    DK_CLIENT_ID = args.dk_client_id
if args.dk_client_secrets:
    DK_CLIENT_SECRETS = args.dk_client_secrets
if args.dk_talk_id:
    DK_TALK_ID = args.dk_talk_id
if args.event_abbr:
    EVENT_ABBR = args.event_abbr
if args.event_date:
    EVENT_DATE = args.event_date
if args.track:
    EVENT_TRACK = args.track
if args.dry_run:
    DRY_RUN = True
if args.api_path:
    DK_API_PATH = args.api_path
if args.api_data:
    DK_API_DATA = args.api_data

logger.info("{}:{}({})".format(OBS_HOST, OBS_PORT, OBS_PASS))

parameters = simpleobsws.IdentificationParameters(
    ignoreNonFatalRequestChecks=False)
ws = simpleobsws.WebSocketClient(url=f'ws://{OBS_HOST}:{OBS_PORT}',
                                 password=OBS_PASS,
                                 identification_parameters=parameters)

async def obsinit():
    await ws.connect()
    await ws.wait_until_identified()

def run():

    dreamkast = Dreamkast(DK_URL, DK_AUTH0_URL, DK_CLIENT_ID,
                          DK_CLIENT_SECRETS, EVENT_ABBR)

    if args.object == "dk":
        if args.operator == "update":
            if not DK_AUTH0_URL:
                print("No enough options: --dk-auth0-url")
                sys.exit()
            if not DK_CLIENT_ID:
                print("No enough options: --dk-client-id")
                sys.exit()
            if not DK_CLIENT_SECRETS:
                print("No enough options: --dk-client-secrets")
                sys.exit()
            dreamkast.update()
        elif args.operator == "onair":
            if not DK_TALK_ID:
                print("No enough options: --dk-talk-id")
                sys.exit()
            dreamkast.onair(DK_TALK_ID)

        elif args.operator == "track_talks":
            dreamkast.get_track_talks_cmd(EVENT_TRACK, EVENT_DATE)
        
        elif args.operator == "get_api":
            if not DK_API_PATH:
                print("No enough option: --api-path")
            dreamkast.request_dk_get(DK_API_PATH, DK_API_DATA)
        elif args.operator == "get_talks":
            if not EVENT_ABBR:
                print("No enough option: --event-abbr")
            dreamkast.get_talks_cmd()

        sys.exit()


    nextcloud = Nextcloud(
        dreamkast,
        UPLOADER_URL,
        UPLOADER_USER,
        UPLOADER_PASS,
        UPLOADER_BASE_DIR,
        UPLOADER_TALK_FILE_PATH,
        DRY_RUN
    )
    
    if args.object == "uploader":
        if args.operator == "dirsync":
            nextcloud.dirsync()
        
        sys.exit()

    NEXTCLOUD_BASE_PATH = "/home/ubuntu/Nextcloud/Broadcast/CNDT2022"
    UPLOADER_BASE_PATH = "/home/ubuntu/Nextcloud2/cndt2022"

    loop = asyncio.get_event_loop()
    loop.run_until_complete(obsinit())

    mediasource = MediaSource(ws)
    scene = Scene(ws)
    source = Source()
    switcher = Switcher(NEXTCLOUD_BASE_PATH, UPLOADER_BASE_PATH, "A")

    # scene
    if args.object == "scene":
        if args.operator == "get":
            loop.run_until_complete(scene.get())
        elif args.operator == "change":
            if not args.sceneName:
                logger.error("No enough options: --sceneName")
                sys.exit()
            loop.run_until_complete(scene.change(args.sceneName))
        elif args.operator == "next":
            loop.run_until_complete(scene.next())

    # source
    elif args.object == "source":
        if args.operator == "get":
            if not args.sceneName:
                logger.error("No enough options: --sceneName")
                sys.exit()
            loop.run_until_complete(source.get(args.sceneName))

    # mediasource
    elif args.object == "mediasource":
        if args.operator == "get":
            loop.run_until_complete(mediasource.get())
        elif args.operator == "time":
            if not args.sourceName:
                logger.error("No enough options: --sourceName")
                sys.exit()
            loop.run_until_complete(mediasource.time(args.sourceName))

    # switcher
    elif args.object == "switcher":
        if args.operator == "build":
            loop.run_until_complete(switcher.build(dreamkast, ws))

    else:
        print(f"undefined command: {args}")