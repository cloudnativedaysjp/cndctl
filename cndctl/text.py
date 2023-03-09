import logging

logger = logging.getLogger(__name__)


# cndctl text edit
async def edit(ws, source_name):
    logger.debug("text_edit({})".format(source_name))


# cndctl text delete
async def delete(ws, source_name):
    logger.debug("text_delete({})".format(source_name))


# cndctl text on
async def on(ws, source_name):
    logger.debug("text_on({})".format(source_name))


# cndctl text off
async def off(ws, source_name):
    logger.debug("text_off({})".format(source_name))
