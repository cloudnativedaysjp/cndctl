import logging
import asyncio
import simpleobsws
import os
import sys
import json
import datetime
import time

async def get(ws):
    logging.debug("set_mediasource()")

# cndctl mediasource time {sourceName}
async def time(ws, sourceName):
    logging.debug("get_mediasource_time({})".format(sourceName))
    while True:
        request = simpleobsws.Request('GetMediaInputStatus', {'inputName': sourceName})

        ret = await ws.call(request)
        if ret.ok():
            state = ret.responseData['mediaState']
            cursor = datetime.timedelta(milliseconds=ret.responseData['mediaCursor'])
            duration = datetime.timedelta(milliseconds=ret.responseData['mediaDuration'])
            cursor_parcent = (cursor / duration) * 100
            print("\r[{}]: {:.1f}% | {} / {}".format(state, cursor_parcent, cursor, duration), end="")
            # time.sleep(1)

# cndctl mediasource get
async def get(ws):
    logging.debug("get_mediasource")