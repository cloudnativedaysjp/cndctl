import logging
import asyncio
import simpleobsws
import os
import sys

# cndctl text edit
async def edit(ws, sourceName):
    logging.debug("text_edit({})".format(sourceName))

# cndctl text delete
async def delete(ws, sourceName):
    logging.debug("text_delete({})".format(sourceName))

# cndctl text on
async def on(ws, sourceName):
    logging.debug("text_on({})".format(sourceName))

# cndctl text off
async def off(ws, sourceName):
    logging.debug("text_off({})".format(sourceName))