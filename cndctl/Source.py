import logging

logger = logging.getLogger(__name__)


class Source:
    def __init__(self) -> None:
        pass

    # cndctl get source {sceneName}
    async def get(ws, sceneName):
        logger.debug("get_source({})".format(sceneName))
