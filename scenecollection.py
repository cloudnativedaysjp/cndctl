import logging
import asyncio
import simpleobsws
import os
import sys

# cndctl get scenecollection
async def get(ws):
    logging.debug("get_scenecollection()")