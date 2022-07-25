import logging
import os
import sys
import json
import requests
import base64
import datetime
import jwt

def read_token(path):
    token_file = open(path, "r")
    token = token_file.read()
    token_file.close()

    return token

# cndctl dk update
def update(dkAuth0Url, dkClientId, dkClientSecrets):
    logging.debug("dreamkast_update()")
    env_file_path = ".dk.env"

    if os.path.isfile(env_file_path):
        token = read_token(env_file_path)
        
        token_payload = jwt.decode(token, options={"verify_signature": False})
        token_expire = datetime.datetime.fromtimestamp(token_payload['exp'])

        if datetime.datetime.now() < token_expire:
            print("token not expired")
            sys.exit()

    req_url = "https://" + dkAuth0Url + "/oauth/token"
    headers = {
        "content-type": "application/json"
    }
    data = {
        "client_id":"",
        "client_secret":"",
        "audience":"https://event.cloudnativedays.jp/",
        "grant_type":"client_credentials"
    }
    data['client_id'] = dkClientId
    data['client_secret'] = dkClientSecrets

    res = requests.post(req_url, headers=headers, data=json.dumps(data))
    res_payload = res.json()
    print("token update successfully ({})".format(res_payload))

    token_file = open(".dk.env", "w")
    token_file.write(res_payload['access_token'])
    token_file.close()

def talks():
    logging.debug("dreamkast_update()")

    # res = requests.put 

def onair():
    logging.debug("dreamkast_onair()")