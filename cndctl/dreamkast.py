from email import header
import logging
logger = logging.getLogger(__name__)
import os
import sys
import json
import requests
import base64
import datetime
import jwt

from . import cli

class dreamkast:
    
    def __init__(self) -> None:
        pass

    def __read_token(self, env_file_path):
        token_file = open(env_file_path, "r")
        token = token_file.read()
        token_file.close()

        return token

    def __check_dk_env(self, env_file_path):
        if os.path.isfile(env_file_path):
            token = self.__read_token(env_file_path=env_file_path)
        else:
            print("The '{}' not found. Please, generate token using 'cndctl dk update'".format(env_file_path))
            return False
        
        if not token:
            print("token '{}' is empty".format(env_file_path))
            return False
        
        token_payload = jwt.decode(token, options={"verify_signature": False})
        token_expire = datetime.datetime.fromtimestamp(token_payload['exp'])

        if datetime.datetime.now() < token_expire:
            return True
        else:
            print("The token is expired. Please update using `cndctl dk update`")
            return False

    # cndctl dk update
    def update(self, DK_AUTH0_URL, DK_CLIENT_ID, DK_CLIENT_SECRETS):
        logger.debug("dreamkast_update()")
        env_file_path = ".dk.env"

        if self.__check_dk_env(env_file_path=env_file_path):
            print("token not expired")
            sys.exit()

        if not cli.accept_continue("Dk token update ok?"):
            sys.exit()

        req_url = "https://" + DK_AUTH0_URL + "/oauth/token"
        headers = {
            "content-type": "application/json"
        }
        data = {
            "client_id":"",
            "client_secret":"",
            "audience":"https://event.cloudnativedays.jp/",
            "grant_type":"client_credentials"
        }
        data['client_id'] = DK_CLIENT_ID
        data['client_secret'] = DK_CLIENT_SECRETS

        res = requests.post(req_url, headers=headers, data=json.dumps(data))
        res_payload = res.json()
        print("token update successfully ({})".format(res_payload))

        token_file = open(".dk.env", "w")
        token_file.write(res_payload['access_token'])
        token_file.close()

    def talks(self):
        logger.debug("dreamkast_update()")

    def onair(self, DK_URL, DK_TALK_ID):
        logger.debug("dreamkast_onair()")

        if self.__check_dk_env(env_file_path=".dk.env"):
            token = self.__read_token(env_file_path=".dk.env")
            req_url = "https://" + DK_URL + "/api/v1/talks/{}".format(DK_TALK_ID)
            headers = {
                'Authorization': 'Bearer {}'.format(token)
            }
            data = {
                "on_air": True
            }
            logger.debug("request\nurl   : {}\nheader: {}\ndata  : {}".format(req_url, headers, data))
            res = requests.put(req_url, headers=headers, data=json.dumps(data))
            res_payload = res.json()
            print(res_payload)