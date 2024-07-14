from config import Config, TargetLayout, SYNC_SAMPLE_SIZE, AUDIO_FOLDER, AUDIO_OUTPUT_PATH, SCRIPT_PATH, CONFIG_PATH
from mpegh_lib.mpegh_ui import MPEGHUIManager
from player import Player
from scene.interface import Interface
from scene.scene_reader import AudioSceneConfig
from utils import PathPointer


def main(file_name: str):
    input_file = PathPointer(AUDIO_FOLDER / file_name)

    ui = MPEGHUIManager(input_file = input_file, output_file = str(AUDIO_OUTPUT_PATH / "input.mp4"), script_path = str(SCRIPT_PATH / "script.xml"))

    config = Config(
        input_file = ui.output_file,
        sample_size = 1 * SYNC_SAMPLE_SIZE,
        duration_in_seconds = 0,
        target_layout = TargetLayout.STEREO,
        drc_boost_scale=0,
    )

    player = Player(config=config, buffer_size=2)
    player.pause()
    player.play(thread_it=True) # type: ignore

    interface = Interface(None, player, ui, input_file, config)
    if file_name != "":
        interface.set_file(file_name)
    interface.build()
    interface.run()
