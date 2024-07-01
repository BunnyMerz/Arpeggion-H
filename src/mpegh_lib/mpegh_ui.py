from subprocess import PIPE, Popen
from config import UI_MANAGER_PATH

import logging

from utils import Command

logger = logging.getLogger(__name__)

GLOBAL_UUID = "00000000-0000-0000-0000-000000000000"
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

DRC_NONE = 0
DRC_NIGHT = 1
DRC_NOISY = 2
DRC_LIMITED = 3
DRC_LOWLEVEL = 4
DRC_DIALOG = 5
DRC_GENERAL = 6

class ActionEvent:
    def __init__(
            self,
            uuid: str, action_type: int,
            param_int: int | None = None, param_float: float | None = None, param_text: str | None = None, param_bool: bool | None = None,
            version: str = "11.0",
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
            ("paramText", self.param_text),
            ("paramInt", self.param_int),
            ("paramFloat", self.param_float),
            ("paramBool", self.param_bool),
        )
        params = str.join(" ", [f'{name}="{value}"' for name, value in params if value is not None])
        return f"<ActionEvent {params} />"
    
    @classmethod
    def reset(cls, uuid: str):
        return ActionEvent(
            uuid=uuid,
            action_type=IIS_UIM_CMD_RESET,
        )
    
    @classmethod
    def drc_select(cls, drc_type: int):
        return ActionEvent(
            uuid=GLOBAL_UUID,
            action_type=IIS_UIM_CMD_DRC_SELECTED,
            param_int=drc_type,
        )

    @classmethod
    def select_preset(cls, uuid: str, preset_id: int):
        return ActionEvent(
            uuid=uuid,
            action_type=IIS_UIM_CMD_PRESET_SELECTED,
            param_int=preset_id,
        )
    
    @classmethod
    def select_language(cls, lang_name: str):
        return ActionEvent(
            uuid=GLOBAL_UUID,
            action_type=IIS_UIM_CMD_AUDIO_LANGUAGE_SELECTED,
            param_text=lang_name,
            param_int=0,
        )
    
    @classmethod
    def audio_muting_prop(cls, uuid: str, audio_id: int, is_muted: bool, is_switch: bool):
        return ActionEvent(
            uuid=uuid,
            action_type=[IIS_UIM_CMD_AUDIO_ELEMENT_MUTING_CHANGED, IIS_UIM_CMD_AUDIO_ELEMENT_SWITCH_MUTING_CHANGED][is_switch],
            param_int=audio_id,
            param_bool=is_muted,
        )
    @classmethod
    def audio_prominance_prop(cls, uuid: str, audio_id: int, value: float, is_switch: bool):
        return ActionEvent(
            uuid=uuid,
            action_type=[IIS_UIM_CMD_AUDIO_ELEMENT_PROMINENCE_LEVEL_CHANGED, IIS_UIM_CMD_AUDIO_ELEMENT_SWITCH_PROMINENCE_LEVEL_CHANGED][is_switch],
            param_int=audio_id,
            param_float=value,
        )
    @classmethod
    def audio_azimuth_prop(cls, uuid: str, audio_id: int, value: float, is_switch: bool):
        return ActionEvent(
            uuid=uuid,
            action_type=[IIS_UIM_CMD_AUDIO_ELEMENT_AZIMUTH_CHANGED, IIS_UIM_CMD_AUDIO_ELEMENT_SWITCH_AZIMUTH_CHANGED][is_switch],
            param_int=audio_id,
            param_float=value,
        )
    @classmethod
    def audio_elevation_prop(cls, uuid: str, audio_id: int, value: float, is_switch: bool):
        return ActionEvent(
            uuid=uuid,
            action_type=[IIS_UIM_CMD_AUDIO_ELEMENT_ELEVATION_CHANGED, IIS_UIM_CMD_AUDIO_ELEMENT_SWITCH_ELEVATION_CHANGED][is_switch],
            param_int=audio_id,
            param_float=value,
        )

    @classmethod
    def element_switch(cls, uuid: str, swith_group_id: int, swith_audio_id: int):
        return ActionEvent(
            uuid=uuid,
            action_type=IIS_UIM_CMD_AUDIO_ELEMENT_SWITCH_SELECTED,
            param_int=swith_group_id,
            param_float=swith_audio_id,
        )

class MPEGHUIManager:
    def __init__(self, input_file: str, output_file: str, script_path: str) -> None:
        self.input_file = input_file
        self.output_file = output_file
        self.script_path = script_path
        self.event_actions: list[ActionEvent] = []

    def add_event_action(self, event: ActionEvent):
        self.event_actions.append(event)

    def build_script(self):
        if self.script_path is not None:
            with open(self.script_path, "w+") as f:
                f.writelines(
                    [str(e)+"\n" for e in self.event_actions]
                )

    def apply_scene_state(self, scene_output: str | None = None):
        self.build_script()
        command = Command(str(UI_MANAGER_PATH))\
            ._if(self.input_file)\
            .script(self.script_path)\
            .of(self.output_file)\
            .xmlSceneState(scene_output)

        process = Popen(list(command), stdout=PIPE)
        output, _ = process.communicate()

        duration = None
        timescale = None
        for line in output.decode("utf-8").split("\n"):
            if "-- Duration" in line:
                duration = int(line.strip("-- Duration:\n"))
            if "-- Timescale" in line:
                timescale = int(line.strip("-- Timescale:\n"))

        if scene_output is not None:
            lines_to_write: list[str] = []
            lines: list[str] = []
            with open(scene_output, "r") as f:
                lines = f.readlines()
            for line in lines:
                if "<?xml" in line:
                    lines_to_write = []
                lines_to_write.append(line)

            with open(scene_output, "w") as f:
                f.writelines(lines_to_write)

        if duration is None or timescale is None:
            return -1
        return int(duration/timescale) - 1
