from config import Config, TargetLayout, SYNC_SAMPLE_SIZE, AUDIO_FOLDER, AUDIO_OUTPUT_PATH, SCRIPT_PATH, CONFIG_PATH
from mpegh_ui import DRC_DIALOG, DRC_GENERAL, DRC_LIMITED, DRC_LOWLEVEL, DRC_NIGHT, DRC_NOISY, DRC_NONE, ActionEvent, MPEGHUIManager
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
    player.play(thread_it=True)

    uuid = "7D130000-0000-0000-0000-0000DD78AA1B"
    while(1):
        action, *args = input("Input: ").split(" ")
        if action == "skip":
            time = args[0]
            player.skip_to(int(time))
        if action == "lang":
            lang = args[0]
            ui.add_event_action(ActionEvent.select_language(lang))
        elif action == "preset":
            preset_id = args[0]
            ui.add_event_action(ActionEvent.select_preset(uuid, preset_id))
        elif action == "switch":
            swtich_id, audio_id = args
            ui.add_event_action(ActionEvent.element_switch(uuid, swith_group_id=swtich_id, swith_audio_id=audio_id))
        elif action == "reset":
            ui.add_event_action(ActionEvent.reset(uuid))
        elif action == "drc":
            drc_type = args[0]
            drc = {
                "none": DRC_NONE,
                "night": DRC_NIGHT,
                "noisy": DRC_NOISY,
                "limited": DRC_LIMITED,
                "lowlevel": DRC_LOWLEVEL,
                "dialog": DRC_DIALOG,
                "general": DRC_GENERAL,
            }
            ui.add_event_action(ActionEvent.drc_select(drc[drc_type.lower()]))

        ui.apply_scene_state()
        player.re_fill_buffer()
