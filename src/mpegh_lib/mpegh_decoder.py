import subprocess
import wave
from config import AUDIO_OUTPUT_PATH, DECODER_PATH, Config
from utils import thread_it
import logging

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from player import Buffer

logger = logging.getLogger(__name__)

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
                "-if", f"{config.input_file}",
                "-of", output_path,
                # Configs
                "-y", f"{sample_number * config.sample_size}",
                "-z", f"{(sample_number * config.sample_size) + config.sample_size - 1}",
                "-tl", f"{config.target_layout}",
                "-db", f"{config.drc_boost_scale}"
            )

            logger.info(" - Starting to decode Frame %s", sample_number)
            process = subprocess.Popen(command, stdout=subprocess.PIPE)
            _, error = process.communicate()
            logger.info(" - Done with Frame %s", sample_number)

            if error is None: # The MPEG-H binary might not return an error when things go wrong
                logger.info(" - Setting buffer for %s", sample_number)
                buffer.set_buffer(sample_number, wave.open(str(output_path),"rb"), config.config_version_counter)
                return True
            logger.critical("[ERROR] Error while decoding Frame %s", sample_number)
            buffer.set_buffer(sample_number, None, config.config_version_counter)
            return False
        except:
            buffer.set_buffer(sample_number, None, config.config_version_counter)
            logger.exception("[ERROR] Error while decoding Frame %s", sample_number)
            raise
