import logging
logger = logging.getLogger(__name__)
import simpleobsws
import datetime

class MediaSource:

    def __init__(self, ws) -> None:
        self.ws = ws

    async def set(self):
        logger.debug("set_mediasource()")

    # cndctl mediasource time {source_name}
    async def time(self, source_name):
        logger.debug("get_mediasource_time(%s)", source_name)
        while True:
            request = simpleobsws.Request('GetMediaInputStatus', {'inputName': source_name})

            ret = await self.ws.call(request)
            if ret.ok():
                state = ret.responseData['mediaState']
                cursor = datetime.timedelta(milliseconds=ret.responseData['mediaCursor'])
                duration = datetime.timedelta(milliseconds=ret.responseData['mediaDuration'])
                cursor_parcent = (cursor / duration) * 100
                print("\r[{}]: {:.1f}% | {} / {}".format(state, cursor_parcent, cursor, duration), end="")
                # time.sleep(1)

    # cndctl mediasource get
    async def get(self):
        logger.debug("get_mediasource")