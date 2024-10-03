from pathlib import Path
from typing import Literal

SYNC_SAMPLE_SIZE = 48

BIN_FOLDER = Path("bin")
AUDIO_FOLDER = Path("audio")
TMP_FOLDER = Path("tmp")

DECODER_PATH = BIN_FOLDER / "mpegh_decoder"
UI_MANAGER_PATH = BIN_FOLDER / "mpegh_ui_manager"
AUDIO_OUTPUT_PATH = TMP_FOLDER / "audio"
CONFIG_PATH = TMP_FOLDER / "config"
SCRIPT_PATH = TMP_FOLDER / "script"

class TargetLayout:
    MONO = 1
    STEREO = 2
    FIVEPOINTONE = 6 # 5.1

class Config:
    def __init__(
            self, input_file: str, sample_size: int, duration_in_seconds: int,
            target_layout: int, drc_boost_scale: int, album_mode: bool = False,
            drc: int = 0, drc_target_loudness: int = 96, scale_factor: int = 0,
        ) -> None:
        self.sample_size = sample_size # 48 seems to be the amount of samples for the syncing of the decoder, which equates to 1 sec
        self.duration_in_seconds = duration_in_seconds
        self.input_file = input_file

        if drc_boost_scale < 0 or drc_boost_scale > 127:
            raise Exception("drc_boost_scale must be between 0 and 127")
        if drc_target_loudness < 40 or drc_target_loudness > 127:
            raise Exception("drc_target_loudness must be between 0 and 127")
        if scale_factor < 0 or scale_factor > 127:
            raise Exception("scale_factor must be between 0 and 127")

        self.target_layout = target_layout
        self.drc = drc
        self.drc_target_loudness = drc_target_loudness
        self.scale_factor = scale_factor
        self.album_mode = album_mode

        self.drc_boost_scale = drc_boost_scale
    
        self.config_version_counter: int = 0

    def alter_config(
            self,
            **values: str | int
        ):
        for key, value in values.items():
            self.__setattr__(key, value)
        self.config_version_counter += 1
