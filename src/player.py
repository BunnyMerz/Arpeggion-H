from threading import Event
from wave import Wave_read
from pyaudio import PyAudio

from config import Config
from mpegh import MPEGHDecoder

import logging
logger = logging.getLogger(__name__)

class BufferSample:
    def __init__(self) -> None:
        self.buffer: None | Wave_read = None # Wave_read, basically bytes, to read from
        self.buffer_event: Event = Event() # Weather the bytes are ready
        self.buffer_config: None | int = None # Which config version the buffer used

    def write(self, buffer: Wave_read, config: int):
        self.buffer = buffer
        self.buffer_config = config
        self.buffer_event.set()
    def wait(self):
        self.buffer_event.wait()

class Buffer:
    def __init__(self, buffer_size: int = 2) -> None:
        self.buffer_size = buffer_size
        self.buffer_samples: list[BufferSample] = [BufferSample() for _ in range(self.buffer_size)]

    def reset_all_buffer(self, new_buffer_size: int | None = None):
        if new_buffer_size is None:
            new_buffer_size = self.buffer_size
        self.buffer_size = new_buffer_size
        self.buffer_samples: list[BufferSample] = [BufferSample() for _ in range(self.buffer_size)]

    def unset_buffer(self, frame: int):
        index = frame % self.buffer_size
        self.buffer_samples[index] = BufferSample()
    def set_buffer(self, frame: int, buffer: Wave_read, version: int):
        index = frame % self.buffer_size
        self.buffer_samples[index].write(buffer, version)

    def read_buffer(self, frame: int):
        index = frame % self.buffer_size
        self.buffer_samples[index].wait()
        return self.buffer_samples[index]

class Player:
    def __init__(self, config: Config, buffer_size: int) -> None:
        self.pyaudio_lib = PyAudio()

        self.current_stream = None
        self.current_stream_config = None

        self.current_frame = 0
        self.current_buffer_frame = 0

        self.config = config
        self.buffer = Buffer(buffer_size)
        self.chunk = self.config.sample_size

        self.pause = Event()
        self.pause.set()
        self.abort = False

    def close_stream(self):
        if self.current_stream is None:
            return
        self.current_stream.stop_stream()
        self.current_stream.close()
        self.current_stream = None

    def set_stream(self, probe: Wave_read):
        self.current_stream = self.pyaudio_lib.open(
            format = self.pyaudio_lib.get_format_from_width(probe.getsampwidth()),
            channels = probe.getnchannels(),
            rate = probe.getframerate(),
            output = True
        )

    def fill_buffer(self, thread_it: bool):
        while self.current_frame + self.buffer.buffer_size > self.current_buffer_frame:
            MPEGHDecoder.decode_sample(
                config = self.config,
                buffer = self.buffer,
                sample_number = self.current_buffer_frame,
                thread_it = thread_it,
            )
            self.current_buffer_frame += 1

    def play_audio(self, wave: Wave_read):
        data = wave.readframes(self.chunk)
        while data:
            self.pause.wait()
            self.current_stream.write(data)
            data = wave.readframes(self.chunk)

    def play(self):
        self.fill_buffer(thread_it=False)
        while not self.abort:
            self.pause.wait()
            curr_frame = self.current_frame
            buffer: BufferSample = self.buffer.read_buffer(curr_frame)

            if self.current_stream_config != buffer.buffer_config:
                logger.info("Opening new stream, config version %s", buffer.buffer_config)
                self.close_stream()
                self.set_stream(buffer.buffer)
                self.current_stream_config = buffer.buffer_config

            logger.info("Playing Frame %s", curr_frame)
            self.play_audio(buffer.buffer)
            self.buffer.unset_buffer(curr_frame)

            if self.current_frame == curr_frame:
                self.current_frame += 1

            logger.info("Filling buffer")
            self.fill_buffer(thread_it=True)
