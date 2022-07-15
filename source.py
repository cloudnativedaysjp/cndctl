import logging
import asyncio
import simpleobsws
import os
import sys
# cndctl get source {sceneName}
async def get(ws, sceneName):
    logging.debug("get_source({})".format(sceneName))
