import logging
logger = logging.getLogger(__name__)
import asyncio
import simpleobsws
import os
import sys
# cndctl get source {sceneName}
async def get(ws, sceneName):
    logger.debug("get_source({})".format(sceneName))
