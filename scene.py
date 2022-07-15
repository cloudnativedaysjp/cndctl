import logging
import asyncio
import simpleobsws
import os
import sys

# cndctl scene get
async def get(ws):
    request = simpleobsws.Request('GetSceneList')

    ret = await ws.call(request)
    if not ret.ok():
        logging.error("Request error. Request:{} Response:{}".format(request, ret))
        sys.exit()
    scenes = ret.responseData['scenes']
    print(ret)

    for scene in reversed(scenes):
        logging.info("scene[{}]: {}".format(scene['sceneIndex'], scene['sceneName']))


# cndctl scene next
async def next(ws):
    logging.debug("set_next()")

    request = simpleobsws.Request('GetSceneList')

    ret = await ws.call(request)
    if not ret.ok():
        logging.error("Request error. Request:{} Response:{}".format(request, ret))
        sys.exit()
    scenes = ret.responseData['scenes']
    print(scenes)

    currentProgramSceneIndex =  [scene['sceneIndex'] for scene in scenes if scene['sceneName'] == ret.responseData['currentProgramSceneName']][0]
    currentProgramSceneName = ret.responseData['currentProgramSceneName']
    print(currentProgramSceneName)
    logging.info("current: [{}]{}".format(currentProgramSceneIndex, currentProgramSceneName))

    nextSceneIndex = currentProgramSceneIndex - 1
    if nextSceneIndex < 0:
        logging.info("current scene is tha last scene.")
    else:
        logging.info("nextScene: [{}]{}".format(nextSceneIndex, scenes[nextSceneIndex]))

    request = simpleobsws.Request('SetCurrentProgramScene', {'sceneName': scenes[nextSceneIndex]['sceneName']})

    ret = await ws.call(request)
    if not ret.ok():
        logging.error("Request error. \n  Request:{} \n  Response:{}".format(request, ret))
        sys.exit()
    
    # logging.info("scene changed: {}".format(sceneName))


# cndctl scene set {sceneName}
async def change(ws, sceneName):
    logging.debug("set_scene({})".format(sceneName))

    request = simpleobsws.Request('GetSceneList')

    ret = await ws.call(request)
    if not ret.ok():
        logging.error("Request error. Request:{} Response:{}".format(request, ret))
        sys.exit()
    scenes = ret.responseData['scenes']
    
    if not [True for scene in scenes if scene['sceneName'] == sceneName]:
        logging.info("Not found scene: {}".format(sceneName))
        sys.exit()

    request = simpleobsws.Request('SetCurrentProgramScene', {'sceneName': sceneName})

    ret = await ws.call(request)
    if not ret.ok():
        logging.error("Request error. \n  Request:{} \n  Response:{}".format(request, ret))
        sys.exit()
    
    logging.info("scene changed: {}".format(sceneName))