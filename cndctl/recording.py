import logging
logger = logging.getLogger(__name__)
import asyncio
import simpleobsws
import os
import sys

# cndctl start recording
async def start(ws):
    logger.debug("start_recording()")

# cndctl stop recording
async def stop(ws):
    logger.debug("stop_recording()")