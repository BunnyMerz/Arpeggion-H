from pathlib import Path
from threading import Event, Thread
import wave
import pyaudio
import subprocess


class TargetLayout:
    MONO = 1
    STEREO = 2
    FIVEPOINTONE = 6 # 5.1

BIN_FOLDER = Path("bin")
AUDIO_FOLDER = Path("audio")
TMP_FOLDER = Path("tmp")

DECODER_PATH = BIN_FOLDER / "mpegh_decoder"
UI_MANAGER_PATH = BIN_FOLDER / "mpegh_ui_manager"
AUDIO_OUTPUT_PATH = TMP_FOLDER / "audio"
CONFIG_PATH = TMP_FOLDER / "config"
SCRIPT_PATH = TMP_FOLDER / "script"

class DecodeMPEGH:
    @classmethod
    def _decode_part(
        cls,
        input_file: str,
        start_sample: int, sample_amount: int, sample_number: int,
        output_list: list[bytes], files_state: list[Event],
        streams_config: list[int | None], config_version: int,
        target_layout: int = 1, drc_boost_scale: int = 0,
    ):
        streams_config[sample_number] = config_version
        output_path = AUDIO_OUTPUT_PATH / f"out-{sample_number+1}.wav"
        command = (
            # Binary
            DECODER_PATH,
            # input/output files
            "-if", AUDIO_FOLDER / f"{input_file}",
            "-of", output_path,
            "-script", SCRIPT_PATH / "script.xml",
            # Configs
            "-y", f"{start_sample}",
            "-z", f"{start_sample + sample_amount - 1}",
            "-tl", f"{target_layout}",
            "-db", f"{drc_boost_scale}"
        )

        process = subprocess.Popen(command, stdout=subprocess.PIPE)
        _, error = process.communicate()

        if error is None:
            output_list[sample_number] = wave.open(str(output_path),"rb")
            files_state[sample_number].set()
            return True
        print("[ERROR] Error while decoding.")
        output_list[sample_number] = b""
        files_state[sample_number].set()
        return False
    
    @classmethod
    def decode_parallel(cls, **kw):
        t = Thread(
            target=cls._decode_part,
            kwargs=kw,
            daemon=True
        )
        t.start()
        return t

def main():
    # Decoding params
    size = 1 * 48
    amount = 60
    input_file = "Sample1.mp4"
    target_layout = TargetLayout.MONO

    # Decoding -> Playback
    buffer_ahead: int = 2 # must be >= 2
    files: list[None | bytes] = [None] * buffer_ahead
    files_state: list[Event] = [Event() for _ in range(buffer_ahead)]
    last_config_version: int = 0
    current_config_version: int = -1
    streams_config: list[int | None] = [None] * buffer_ahead

    # Playback
    chunk = size

    # Fill buffer
    for x in range(buffer_ahead):
        DecodeMPEGH._decode_part(
            input_file=input_file,
            start_sample=x*size, sample_amount=size, sample_number=x % buffer_ahead,
            output_list = files, files_state=files_state,
            streams_config=streams_config, config_version=last_config_version,
            target_layout=target_layout
        )

    p = pyaudio.PyAudio()

    probe = files[0] # Using the first decode to Probe for information
    stream = p.open(
        format = p.get_format_from_width(probe.getsampwidth()),
        channels = probe.getnchannels(),
        rate = probe.getframerate(),
        output = True
    )
    current_config_version = streams_config[0]

    current_frame = 0
    while current_frame < amount:
        # Simualte skipping audio trough an interface
        if current_frame == 4:
            current_frame = 8
            for next_frames in range(current_frame, current_frame + buffer_ahead):
                DecodeMPEGH._decode_part(
                    input_file=input_file,
                    start_sample=next_frames*size, sample_amount=size, sample_number=next_frames % buffer_ahead,
                    output_list = files, files_state=files_state,
                    streams_config=streams_config, config_version=last_config_version,
                    target_layout=target_layout
                )

        if files_state[current_frame % buffer_ahead].is_set() is False:
            print("[ERROR] Buffer is not long enough! Try Increasing it")
        files_state[current_frame % buffer_ahead].wait()

        f = files[current_frame % buffer_ahead]
        if current_config_version != streams_config[current_frame % buffer_ahead]:
            print("Opening new stream, config version", streams_config[current_frame % buffer_ahead])
            stream.stop_stream()
            stream.close()
            stream = p.open(
                format = p.get_format_from_width(f.getsampwidth()),
                channels = f.getnchannels(),
                rate = f.getframerate(),
                output = True
            )
            current_config_version = streams_config[current_frame % buffer_ahead]

        data = f.readframes(chunk)
        while data:
            stream.write(data)
            data = f.readframes(chunk)

        files[current_frame % buffer_ahead] = None
        files_state[current_frame % buffer_ahead].clear()
        streams_config[current_frame % buffer_ahead] = None

        # Re-build buffer
        y = current_frame + buffer_ahead
        if y < amount:
            # if (y % 2) == 0:
            #     target_layout = TargetLayout.MONO
            #     last_config_version += 1
            # elif (y % 2) == 1:
            #     target_layout = TargetLayout.STEREO
            #     last_config_version += 1

            DecodeMPEGH.decode_parallel(
                input_file=input_file,
                start_sample=y*size, sample_amount=size, sample_number=y % buffer_ahead,
                output_list=files, files_state=files_state,
                streams_config=streams_config, config_version=last_config_version,
                target_layout=target_layout,
            )
        current_frame += 1

    # End
    stream.stop_stream()
    stream.close()
    p.terminate()
