from config import Config, TargetLayout, SYNC_SAMPLE_SIZE, AUDIO_FOLDER, AUDIO_OUTPUT_PATH, SCRIPT_PATH, CONFIG_PATH
from mpegh_ui import ActionEvent, MPEGHUIManager
from player import Player


def main():
    input_file = AUDIO_FOLDER / "Sample1.mp4"

    ui = MPEGHUIManager(input_file = input_file, output_file = AUDIO_OUTPUT_PATH / "input.mp4", script_path = SCRIPT_PATH / "script.xml")
    ui.apply_scene_state(CONFIG_PATH / "scene_state.xml")

    config = Config(
        input_file = ui.output_file,
        sample_size = 1 * SYNC_SAMPLE_SIZE,
        duration_in_seconds = 60, # 1 minute video
        target_layout = TargetLayout.STEREO,
        drc_boost_scale=0,
    )

    player = Player(config=config, buffer_size=2)
    player.skip_to(3)
    player.play(thread_it=True)

    while(1):
        i = input("Input: ")
        try:
            pre_id = int(i)
            ui.add_event_action(ActionEvent.select_preset("E97E0000-0000-0000-0000-00002107BD59", pre_id))
            ui.apply_scene_state()
            player.re_fill_buffer()
        except:
            lang = i
            ui.add_event_action(ActionEvent.select_language(lang))
            ui.apply_scene_state()
            player.re_fill_buffer()
