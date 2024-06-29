import subprocess
import wave
from config import AUDIO_OUTPUT_PATH, DECODER_PATH, AUDIO_FOLDER, Config
from utils import thread_it

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from player import Buffer

class MPEGHDecoder:
    @classmethod
    @thread_it
    def decode_sample(
        cls,
        config: Config, buffer: "Buffer",
        sample_number: int,
    ):
        try:
            output_path = AUDIO_OUTPUT_PATH / f"out-{(sample_number % buffer.buffer_size)+1}.wav"
            command = (
                # Binary
                DECODER_PATH,
                # input/output files
                "-if", AUDIO_FOLDER / f"{config.input_file}",
                "-of", output_path,
                # Configs
                "-y", f"{sample_number * config.sample_size}",
                "-z", f"{(sample_number * config.sample_size) + config.sample_size - 1}",
                "-tl", f"{config.target_layout}",
                "-db", f"{config.drc_boost_scale}"
            )

            process = subprocess.Popen(command, stdout=subprocess.PIPE)
            _, error = process.communicate()

            if error is None: # The MPEG-H binary might not return an error when things go wrong
                buffer.set_buffer(sample_number, wave.open(str(output_path),"rb"), config.config_version_counter)
                return True
            print("[ERROR] Error while decoding.")
            buffer.set_buffer(sample_number, b"", config.config_version_counter)
            return False
        except:
            buffer.set_buffer(sample_number, b"", config.config_version_counter)
            raise
