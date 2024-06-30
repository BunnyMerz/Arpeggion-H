from config import Config, TargetLayout, SYNC_SAMPLE_SIZE
from mpegh_ui import MPEGHUIManager
from player import Player


def main():
    config = Config(
        input_file = "AltSample1.mp4",
        sample_size = 1 * SYNC_SAMPLE_SIZE,
        duration_in_seconds = 60, # 1 minute video
        target_layout = TargetLayout.STEREO,
        drc_boost_scale=0,
    )

    # ui = MPEGHUIManager(input_file="audio/Sample1.mp4", output_file="tmp/audio/input.mp4", script_path="tmp/script/script.xml")
    # ui.build_script()
    # ui.apply_scene_state("tmp/config/scene_state.xml")

    player = Player(config=config, buffer_size=2)
    player.play()
