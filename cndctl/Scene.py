import logging
logger = logging.getLogger(__name__)
import asyncio
import simpleobsws
import os
import sys
from .cli import Cli

class Scene:
    
    def __init__(self) -> None:
        self.cli = Cli()
        pass

    # cndctl scene get
    async def get(self, ws):
        request = simpleobsws.Request('GetSceneList')

        ret = await ws.call(request)
        if not ret.ok():
            logger.error("Request error. Request:{} Response:{}".format(request, ret))
            sys.exit()
        scenes = ret.responseData['scenes']
        logger.info(ret)

        for scene in reversed(scenes):
            logger.info("scene[{}]: {}".format(scene['sceneIndex'], scene['sceneName']))
            print(scene['sceneName'])


    # cndctl scene next
    async def next(self, ws):
        logger.debug("set_next()")

        request = simpleobsws.Request('GetSceneList')

        ret = await ws.call(request)
        if not ret.ok():
            logger.error("Request error. Request:{} Response:{}".format(request, ret))
            sys.exit()
        scenes = ret.responseData['scenes']
        logger.info(scenes)

        currentProgramSceneIndex =  [scene['sceneIndex'] for scene in scenes if scene['sceneName'] == ret.responseData['currentProgramSceneName']][0]
        currentProgramSceneName = ret.responseData['currentProgramSceneName']
        print(currentProgramSceneName)
        logger.info("current: [{}]{}".format(currentProgramSceneIndex, currentProgramSceneName))

        nextSceneIndex = currentProgramSceneIndex - 1
        if nextSceneIndex < 0:
            logger.info("current scene is tha last scene.")
        else:
            logger.info("nextScene: [{}]{}".format(nextSceneIndex, scenes[nextSceneIndex]))

        if not self.cli.accept_continue("Change scene to '{}'".format(scenes[nextSceneIndex]['sceneName'])):
            sys.exit()

        request = simpleobsws.Request('SetCurrentProgramScene', {'sceneName': scenes[nextSceneIndex]['sceneName']})

        ret = await ws.call(request)
        if not ret.ok():
            logger.error("Request error. \n  Request:{} \n  Response:{}".format(request, ret))
            sys.exit()
        
        # logger.info("scene changed: {}".format(sceneName))


    # cndctl scene set {sceneName}
    async def change(self, ws, sceneName):
        logger.debug("set_scene({})".format(sceneName))

        request = simpleobsws.Request('GetSceneList')

        ret = await ws.call(request)
        if not ret.ok():
            logger.error("Request error. Request:{} Response:{}".format(request, ret))
            sys.exit()
        scenes = ret.responseData['scenes']
        
        if not [True for scene in scenes if scene['sceneName'] == sceneName]:
            logger.info("Not found scene: {}".format(sceneName))
            sys.exit()

        if not self.cli.accept_continue("Change scene to '{}'".format(sceneName)):
            sys.exit()

        request = simpleobsws.Request('SetCurrentProgramScene', {'sceneName': sceneName})

        ret = await ws.call(request)
        if not ret.ok():
            logger.error("Request error. \n  Request:{} \n  Response:{}".format(request, ret))
            sys.exit()
        
        logger.info("scene changed: {}".format(sceneName))