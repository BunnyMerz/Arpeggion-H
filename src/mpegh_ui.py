from subprocess import PIPE, Popen
from config import UI_MANAGER_PATH

import logging

from utils import Command

logger = logging.getLogger(__name__)


IIS_UIM_CMD_RESET = 0
IIS_UIM_CMD_DRC_SELECTED = 10
IIS_UIM_CMD_DRC_BOOST = 11
IIS_UIM_CMD_DRC_COMPRESS = 12
IIS_UIM_CMD_TARGET_LOUDNESS = 20
IIS_UIM_CMD_ALBUM_MODE = 21
IIS_UIM_CMD_PRESET_SELECTED = 30
IIS_UIM_CMD_ACCESSIBILITY_PREFERENCE = 31
IIS_UIM_CMD_AUDIO_ELEMENT_MUTING_CHANGED = 40
IIS_UIM_CMD_AUDIO_ELEMENT_PROMINENCE_LEVEL_CHANGED = 41
IIS_UIM_CMD_AUDIO_ELEMENT_AZIMUTH_CHANGED = 42
IIS_UIM_CMD_AUDIO_ELEMENT_ELEVATION_CHANGED = 43
IIS_UIM_CMD_AUDIO_ELEMENT_SWITCH_SELECTED = 60
IIS_UIM_CMD_AUDIO_ELEMENT_SWITCH_MUTING_CHANGED = 61
IIS_UIM_CMD_AUDIO_ELEMENT_SWITCH_PROMINENCE_LEVEL_CHANGED = 62
IIS_UIM_CMD_AUDIO_ELEMENT_SWITCH_AZIMUTH_CHANGED = 63
IIS_UIM_CMD_AUDIO_ELEMENT_SWITCH_ELEVATION_CHANGED = 64
IIS_UIM_CMD_AUDIO_LANGUAGE_SELECTED = 70
IIS_UIM_CMD_INTERFACE_LANGUAGE_SELECTED = 71
IIS_UIM_CMD_SET_GUID = 90

class EventAction:
    def __init__(
            self,
            uuid: str, action_type: int,
            param_int: int = None, param_float: float = None, param_text: str = None, param_bool: bool = None,
            version: str = "11.1",
        ) -> None:
        self.uuid = uuid
        self.version = version
        self.action_type = action_type
        self.param_int = param_int
        self.param_float = param_float
        self.param_text = param_text
        self.param_bool = param_bool

    def __str__(self) -> str:
        params = (
            ("uuid", self.uuid),
            ("version", self.version),
            ("actionType", self.action_type),
            ("paramInt", self.param_int),
            ("paramFloat", self.param_float),
            ("paramText", self.param_text),
            ("paramBool", self.param_bool),
        )
        params = str.join(" ", [f'{name}="{value}"' for name, value in params if value is not None])
        return f"<EventAction {params}/>"
    
    @classmethod
    def select_preset(cls, uuid: str, preset_id: int):
        return cls(
            uuid=uuid,
            action_type=IIS_UIM_CMD_PRESET_SELECTED,
            param_int=preset_id,
        )

class MPEGHUIManager:
    def __init__(self, input_file: str, output_file: str, script_path: str) -> None:
        self.input_file = input_file
        self.output_file = output_file
        self.script_path = script_path
        self.event_actions: list[EventAction] = []

    def add_event_action(self, event: EventAction):
        self.event_actions.append(event)

    def build_script(self):
        if self.script_path is not None:
            with open(self.script_path, "w+") as f:
                f.writelines(
                    [str(e)+"\n" for e in self.event_actions]
                )

    def apply_scene_state(self, scene_output: str = None):
        self.build_script()
        command = Command(UI_MANAGER_PATH)\
            ._if(self.input_file)\
            .script(self.script_path)\
            .of(self.output_file)\
            .xmlSceneState(scene_output)

        process = Popen(command, stdout=PIPE)
        _, error = process.communicate()

        if error is None:
            pass
