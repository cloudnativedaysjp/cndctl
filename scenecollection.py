import logging
logger = logging.getLogger(__name__)
import asyncio
import simpleobsws
import os
import sys

# cndctl get scenecollection
async def get(ws):
    logger.debug("get_scenecollection()")