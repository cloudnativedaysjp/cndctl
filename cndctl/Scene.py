import logging

logger = logging.getLogger(__name__)
import sys

import simpleobsws

from .Cli import Cli


class Scene:
    def __init__(self, ws) -> None:
        self.ws = ws
        self.cli = Cli()

    # cndctl scene get
    async def get(self):
        request = simpleobsws.Request("GetSceneList")

        ret = await self.ws.call(request)
        if not ret.ok():
            logger.error("Request error. Request:%s Response:%s", request, ret)
            sys.exit()
        scenes = ret.responseData["scenes"]
        logger.info(ret)

        for scene in reversed(scenes):
            logger.info("scene[%s]: %s", scene["sceneIndex"], scene["sceneName"])
            print(scene["sceneName"])

    # cndctl scene next
    async def next(self):
        logger.debug("set_next()")

        request = simpleobsws.Request("GetSceneList")

        ret = await self.ws.call(request)
        if not ret.ok():
            logger.error("Request error. Request:%s Response:%s", request, ret)
            sys.exit()
        scenes = ret.responseData["scenes"]
        logger.info(scenes)

        current_program_scene_index = [
            scene["sceneIndex"]
            for scene in scenes
            if scene["sceneName"] == ret.responseData["currentProgramSceneName"]
        ][0]
        current_program_scene_name = ret.responseData["currentProgramSceneName"]
        print(current_program_scene_name)
        logger.info(
            "current: [%s]%s", current_program_scene_index, current_program_scene_name
        )

        next_scene_index = current_program_scene_index - 1
        if next_scene_index < 0:
            logger.info("current scene is the last scene.")
        else:
            logger.info("nextScene: [%s]%s", next_scene_index, scenes[next_scene_index])

        if not self.cli.accept_continue(
            f"Change scene to '{scenes[next_scene_index]['sceneName']}'"
        ):
            sys.exit()

        request = simpleobsws.Request(
            "SetCurrentProgramScene",
            {"sceneName": scenes[next_scene_index]["sceneName"]},
        )

        ret = await self.ws.call(request)
        if not ret.ok():
            logger.error("Request error. Request:%s Response:%s", request, ret)
            sys.exit()

        if next_scene_index == 0:
            logger.info("no more next scene to preview.")
        else:
            next_scene_index -= 1
            logger.info(
                "nextScene to preview: [%s]%s",
                next_scene_index,
                scenes[next_scene_index],
            )

        request = simpleobsws.Request(
            "SetCurrentPreviewScene",
            {"sceneName": scenes[next_scene_index]["sceneName"]},
        )

        ret = await self.ws.call(request)
        if not ret.ok():
            logger.error("Request error. Request:%s Response:%s", request, ret)
            sys.exit()

        if next_scene_index == 0:
            logger.info("no more next scene to preview.")
        else:
            next_scene_index -= 1
            logger.info(
                "nextScene to preview: [%s]%s",
                next_scene_index,
                scenes[next_scene_index],
            )

        request = simpleobsws.Request(
            "SetCurrentPreviewScene",
            {"sceneName": scenes[next_scene_index]["sceneName"]},
        )

        ret = await self.ws.call(request)
        if not ret.ok():
            logger.error("Request error. Request:%s Response:%s", request, ret)
            sys.exit()

        # logger.info("scene changed: {}".format(sceneName))

    # cndctl scene set {sceneName}
    async def change(self, sceneName):
        logger.debug("set_scene(%s)", sceneName)

        request = simpleobsws.Request("GetSceneList")

        ret = await self.ws.call(request)
        if not ret.ok():
            logger.error("Request error. Request:%s Response:%s", request, ret)
            sys.exit()
        scenes = ret.responseData["scenes"]

        if not [True for scene in scenes if scene["sceneName"] == sceneName]:
            logger.info("Not found scene: %s", sceneName)
            sys.exit()

        if not self.cli.accept_continue(f"Change scene to '{sceneName}'"):
            sys.exit()

        request = simpleobsws.Request(
            "SetCurrentProgramScene", {"sceneName": sceneName}
        )

        ret = await self.ws.call(request)
        if not ret.ok():
            logger.error("Request error. Request:%s Response:%s", request, ret)
            sys.exit()

        logger.info("scene changed: %s", sceneName)
