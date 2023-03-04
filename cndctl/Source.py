import logging

logger = logging.getLogger(__name__)
import asyncio
import os
import sys

import simpleobsws


class Source:
    def __init__(self) -> None:
        pass

    # cndctl get source {sceneName}
    async def get(ws, sceneName):
        logger.debug("get_source({})".format(sceneName))
