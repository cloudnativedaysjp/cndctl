import logging
logger = logging.getLogger(__name__)
import asyncio
import simpleobsws
import os
import sys

# cndctl start streaming
async def start(ws):
    logger.debug("start_streaming()")

# cndctl stop streaming
async def stop(ws):
    logger.debug("stop_streaming()")