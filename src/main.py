from config import Config, TargetLayout, SYNC_SAMPLE_SIZE
from player import Player


def main():
    config = Config(
        input_file = "AltSample1.mp4",
        sample_size = 1 * SYNC_SAMPLE_SIZE,
        duration_in_seconds = 60, # 1 minute video
        target_layout = TargetLayout.MONO,
        drc_boost_scale=0,
    )
    player = Player(config=config, buffer_size=3)
    player.play()


