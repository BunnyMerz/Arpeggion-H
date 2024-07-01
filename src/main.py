from config import Config, TargetLayout, SYNC_SAMPLE_SIZE, AUDIO_FOLDER, AUDIO_OUTPUT_PATH, SCRIPT_PATH, CONFIG_PATH
from mpegh_lib.mpegh_ui import MPEGHUIManager
from player import Player
from scene.interface import Interface
from scene.scene_reader import AudioSceneConfig
from utils import PathPointer


def main():
    input_file = PathPointer(AUDIO_FOLDER / "Sample1.mp4")

    ui = MPEGHUIManager(input_file = input_file, output_file = str(AUDIO_OUTPUT_PATH / "input.mp4"), script_path = str(SCRIPT_PATH / "script.xml"))
    duration = ui.apply_scene_state(str(CONFIG_PATH / "scene_state.xml"))

    config = Config(
        input_file = ui.output_file,
        sample_size = 1 * SYNC_SAMPLE_SIZE,
        duration_in_seconds = duration, # 1 minute video
        target_layout = TargetLayout.STEREO,
        drc_boost_scale=0,
    )

    player = Player(config=config, buffer_size=2)
    player.play(thread_it=True) # type: ignore

    
    scene = AudioSceneConfig.start_parsing("tmp/config/scene_state.xml")
    interface = Interface(scene, player, ui, input_file)
    interface.run()
