import logging
import asyncio
import simpleobsws
import os
import sys

# cndctl start recording
async def start(ws):
    logging.debug("start_recording()")

# cndctl stop recording
async def stop(ws):
    logging.debug("stop_recording()")