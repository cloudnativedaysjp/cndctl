import logging
import asyncio
import simpleobsws
import os
import sys

# cndctl text edit
async def edit(ws, source_name):
    logging.debug("text_edit({})".format(source_name))

# cndctl text delete
async def delete(ws, source_name):
    logging.debug("text_delete({})".format(source_name))

# cndctl text on
async def on(ws, source_name):
    logging.debug("text_on({})".format(source_name))

# cndctl text off
async def off(ws, source_name):
    logging.debug("text_off({})".format(source_name))