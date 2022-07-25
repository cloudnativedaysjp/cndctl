import scene
import scenecollection
import source
import mediasource
import streaming
import recording
import text
import dreamkast

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
parser.add_argument("--dk-auth0-url")
parser.add_argument("--dk-client-id")
parser.add_argument("--dk-client-secrets")
parser.add_argument("--sceneName")
parser.add_argument("--sourceName")

args = parser.parse_args()

obsHost = ""
obsPort = ""
obsPass = ""
dkUrl = ""
dkAuth0Url = ""
dkClientId = ""
dkClientSecrets = ""

# envirouments
if "WSHOST" in os.environ:
    obsHost= os.environ["WSHOST"]
if "WSPORT" in os.environ:
    obsPort= os.environ["WSPORT"]
if "WSPASS" in os.environ:
    obsPass= os.environ["WSPASS"]
if "DK_URL" in os.environ:
    dkUrl = os.environ["DK_URL"]
if "DK_AUTH0_URL" in os.environ:
    dkAuth0Url = os.environ["DK_AUTH0_URL"]
if "DK_CLIENT_ID" in os.environ:
    dkClientId = os.environ["DK_CLIENT_ID"]
if "DK_CLIENT_SECRET" in os.environ:
    dkClientSecrets = os.environ["DK_CLIENT_SECRET"]

# json

if args.secret:
    with open(args.secret) as f:
        secret = json.loads(f.read())

    if "obs" in secret:
        obs = secret['obs']
        logging.debug(obs)

        if "host" in secret['obs'] and secret['obs']['host']:
            obsHost= secret['obs']['host']
        if "port" in secret['obs'] and secret['obs']['port']:
            obsPort= secret['obs']['port']
        if "password" in secret['obs'] and secret['obs']['password']:
            obsPass= secret['obs']['password']

    if "dreamkast" in secret:
        if "url" in secret['dreamkast'] and secret['dreamkast']['url']:
            dkUrl = secret['dreamkast']['url']
        if "auth0_url" in secret['dreamkast'] and secret['dreamkast']['auth0_url']:
            dkAuth0Url = secret['dreamkast']['auth0_url']
        if "client_id" in secret['dreamkast'] and secret['dreamkast']['client_id']:
            dkClientId = secret['dreamkast']['client_id']
        if "client_secrets" in secret['dreamkast'] and secret['dreamkast']['client_secrets']:
            dkClientSecrets = secret['dreamkast']['client_secrets']

# command option
if args.obs_host:
    obsHost= args.obs_host
if args.obs_port:
    obsPort= args.obs_port
if args.obs_password:
    obsPass= args.obs_password
if args.dk_url:
    dkUrl = args.dk_url
if args.dk_client_id:
    dkClientId = args.dk_client_id
if args.dk_client_secrets:
    dkClientSecrets = args.dk_client_secrets

logging.info("{}:{}({})".format(obsHost, obsPort, obsPass))

parameters = simpleobsws.IdentificationParameters(ignoreNonFatalRequestChecks = False)
ws = simpleobsws.WebSocketClient(url = f'ws://{obsHost}:{obsPort}', password = obsPass, identification_parameters = parameters)

async def obsinit():
    await ws.connect()
    await ws.wait_until_identified()

def main():

    if args.object == "dk":
        if args.operator == "update":
            if not dkAuth0Url:
                print("No enough options: --dk-auth0-url")
                sys.exit()
            if not dkClientId:
                print("No enough options: --dk-client-id")
                sys.exit()
            if not dkClientSecrets:
                print("No enough options: --dk-client-secrets")
                sys.exit()
            dreamkast.update(dkAuth0Url=dkAuth0Url, dkClientId=dkClientId, dkClientSecrets=dkClientSecrets)

        loop = asyncio.get_event_loop()
        loop.run_until_complete(obsinit())

    # scene
    if args.object == "scene":
        if args.operator == "get":
            loop.run_until_complete(scene.get(ws=ws))
        elif args.operator == "change":
            if not args.sceneName:
                logging.error("No enough options: --sceneName")
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
                logging.error("No enough options: --sceneName")
                sys.exit()
            loop.run_until_complete(source.get(ws=ws, sceneName=args.sceneName))

    # mediasource
    elif args.object == "mediasource":
        if args.operator == "get":
            loop.run_until_complete(mediasource.get(ws=ws))
        elif args.operator == "time":
            if not args.sourceName:
                logging.error("No enough options: --sourceName")
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