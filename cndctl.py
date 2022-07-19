import scene
import scenecollection
import source
import mediasource
import streaming
import recording
import text

import logging
logging.basicConfig(level=logging.ERROR, format='%(levelname)s: %(message)s')
import asyncio
import simpleobsws
import sys
import os
import json
import argparse

parser = argparse.ArgumentParser(description="obs remote controll cli tool")
parser.add_argument("object")
parser.add_argument("operator")
parser.add_argument("--secret")
parser.add_argument("--obs-host")
parser.add_argument("--obs-port")
parser.add_argument("--obs-password")
parser.add_argument("--dk-url")
parser.add_argument("--dk-client-id")
parser.add_argument("--dk-client-secrets")
parser.add_argument("--sceneName")
parser.add_argument("--sourceName")

args = parser.parse_args()

# envirouments
if "WSHOST" in os.environ:
    HOST = os.environ["WSHOST"]
if "WSPORT" in os.environ:
    PORT = os.environ["WSPORT"]
if "WSPASS" in os.environ:
    PASS = os.environ["WSPASS"]
if "DK_URL" in os.environ:
    dkUrl = os.environ["DK_URL"]
if "DK_CLIENT_ID" in os.environ:
    dkClientId = os.environ["DK_CLIENT_ID"]
if "DK_CLIENT_SECRET" in os.environ:
    dkClientSecrets = os.environ["DK_CLIENT_SECRET"]

# json
secretFilePath = args.secret
with open(secretFilePath) as f:
    secret = json.loads(f.read())

if "obs" in secret:
    obs = secret['obs']
    logging.debug(obs)

    if secret['obs']['host']:
        HOST = secret['obs']['host']
    if secret['obs']['port']:
        PORT = secret['obs']['port']
    if secret['obs']['password']:
        PASS = secret['obs']['password']

if "dreamkast" in secret:
    if secret['dreamkast']['url']:
        dkUrl = secret['dreamkast']['url']
    if secret['dreamkast']['client_id']:
        dkClientId = secret['dreamkast']['client_id']
    if secret['dreamkast']['client_secrets']:
        dkClientSecrets = secret['dreamkast']['client_secrets']

# command option 
if args.obs_host:
    HOST = args.obs_host
if args.obs_port:
    PORT = args.obs_port
if args.obs_password:
    PASS = args.obs_password
if args.dk_url:
    dkUrl = args.dk_url
if args.dk_client_id:
    dkClientId = args.dk_client_id
if args.dk_client_secrets:
    dkClientSecrets = args.dk_client_secrets

logging.info("{}:{}({})".format(HOST, PORT, PASS))

parameters = simpleobsws.IdentificationParameters(ignoreNonFatalRequestChecks = False)
ws = simpleobsws.WebSocketClient(url = f'ws://{HOST}:{PORT}', password = PASS, identification_parameters = parameters)

async def init():
    await ws.connect()
    await ws.wait_until_identified()

def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init())

    # scene
    if args.object == "scene":
        if args.operator == "get":
            loop.run_until_complete(scene.get(ws=ws))
        elif args.operator == "change":
            if not args.sceneName:
                logging.error("not found argment: --sceneName")
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
                logging.error("not found argment: --sceneName")
                sys.exit()
            loop.run_until_complete(source.get(ws=ws, sceneName=args.sceneName))

    # mediasource
    elif args.object == "mediasource":
        if args.operator == "get":
            loop.run_until_complete(mediasource.get(ws=ws))
        elif args.operator == "time":
            if not args.sourceName:
                logging.error("not found argment: --sourceName")
                sys.exit()
            loop.run_until_complete(mediasource.time(ws=ws, sourceName=args.sourceName))

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