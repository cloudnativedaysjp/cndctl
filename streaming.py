import logging
import asyncio
import simpleobsws
import os
import sys

# cndctl start streaming
async def start(ws):
    logging.debug("start_streaming()")

# cndctl stop streaming
async def stop(ws):
    logging.debug("stop_streaming()")