import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.WARNING, format='%(asctime)s [%(levelname)s] [%(name)s] %(message)s')

import dreamkast
import mediasource
import recording
import scene
import scenecollection
import source
import streaming

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
parser.add_argument("--sceneName")
parser.add_argument("--sourceName")

args = parser.parse_args()

OBS_HOST = ""
OBS_PORT = ""
OBS_PASS = ""
DK_URL = ""
DK_CLIENT_ID = ""
DK_CLIENT_SECRETS = ""
DK_AUTH0_URL = ""
DK_TALK_ID = ""

# envirouments
if "WSHOST" in os.environ:
    OBS_HOST= os.environ["WSHOST"]
if "WSPORT" in os.environ:
    OBS_PORT= os.environ["WSPORT"]
if "WSPASS" in os.environ:
    OBS_PASS= os.environ["WSPASS"]
if "DK_URL" in os.environ:
    DK_URL = os.environ["DK_URL"]
if "DK_AUTH0_URL" in os.environ:
    DK_URL = os.environ["DK_AUTH0_URL"]
if "DK_CLIENT_ID" in os.environ:
    DK_CLIENT_ID = os.environ["DK_CLIENT_ID"]
if "DK_CLIENT_SECRET" in os.environ:
    DK_CLIENT_SECRETS = os.environ["DK_CLIENT_SECRET"]

# json

if args.secret:
    with open(args.secret) as f:
        secret = json.loads(f.read())

    if "obs" in secret:
        obs = secret['obs']
        logger.debug(obs)

        if "host" in secret['obs'] and secret['obs']['host']:
            OBS_HOST= secret['obs']['host']
        if "port" in secret['obs'] and secret['obs']['port']:
            OBS_PORT= secret['obs']['port']
        if "password" in secret['obs'] and secret['obs']['password']:
            OBS_PASS= secret['obs']['password']

    if "dreamkast" in secret:
        if "url" in secret['dreamkast'] and secret['dreamkast']['url']:
            DK_URL = secret['dreamkast']['url']
        if "auth0_url" in secret['dreamkast'] and secret['dreamkast']['auth0_url']:
            DK_AUTH0_URL = secret['dreamkast']['auth0_url']
        if "client_id" in secret['dreamkast'] and secret['dreamkast']['client_id']:
            DK_CLIENT_ID = secret['dreamkast']['client_id']
        if "client_secrets" in secret['dreamkast'] and secret['dreamkast']['client_secrets']:
            DK_CLIENT_SECRETS = secret['dreamkast']['client_secrets']

# command option
if args.obs_host:
    OBS_HOST= args.obs_host
if args.obs_port:
    OBS_PORT= args.obs_port
if args.obs_password:
    OBS_PASS= args.obs_password
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

logger.info("{}:{}({})".format(OBS_HOST, OBS_PORT, OBS_PASS))

parameters = simpleobsws.IdentificationParameters(ignoreNonFatalRequestChecks = False)
ws = simpleobsws.WebSocketClient(url = f'ws://{OBS_HOST}:{OBS_PORT}', password = OBS_PASS, identification_parameters = parameters)

async def obsinit():
    await ws.connect()
    await ws.wait_until_identified()

def main():

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
            dreamkast.update(DK_AUTH0_URL=DK_AUTH0_URL, DK_CLIENT_ID=DK_CLIENT_ID, DK_CLIENT_SECRETS=DK_CLIENT_SECRETS)
        elif args.operator == "onair":
            if not DK_TALK_ID:
                print("No enough options: --dk-talk-id")
                sys.exit()
            dreamkast.onair(DK_URL=DK_URL, DK_TALK_ID=DK_TALK_ID)

        sys.exit()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(obsinit())

    # scene
    if args.object == "scene":
        if args.operator == "get":
            loop.run_until_complete(scene.get(ws=ws))
        elif args.operator == "change":
            if not args.sceneName:
                logger.error("No enough options: --sceneName")
                sys.exit()
            loop.run_until_complete(scene.change(ws=ws, sceneName=args.sceneName))
        elif args.operator == "next":
            loop.run_until_complete(scene.next(ws=ws))

    # scenecollection
    elif args.object == "scenecollection":
        if args.operator == "get":
            loop.run_until_complete(scenecollection.get(ws=ws))

    # source
    elif args.object == "source":
        if args.operator == "get":
            if not args.sceneName:
                logger.error("No enough options: --sceneName")
                sys.exit()
            loop.run_until_complete(source.get(ws=ws, sceneName=args.sceneName))

    # mediasource
    elif args.object == "mediasource":
        if args.operator == "get":
            loop.run_until_complete(mediasource.get(ws=ws))
        elif args.operator == "time":
            if not args.sourceName:
                logger.error("No enough options: --sourceName")
                sys.exit()
            loop.run_until_complete(mediasource.time(ws=ws, source_name=args.sourceName))

    # streaming
    elif args.object == "streaming":
        if args.operator == "start":
            loop.run_until_complete(streaming.start(ws=ws))
        elif args.operator == "stop":
            loop.run_until_complete(streaming.stop(ws=ws))

    # recording
    elif args.object == "recording":
        if args.operator == "start":
            loop.run_until_complete(recording.start(ws=ws))
        elif args.operator == "stop":
            loop.run_until_complete(recording.stop(ws=ws))
    else:
        print("undefined command: {}".format(args))

if __name__ == "__main__":
    main()
