from threading import Event
from tkinter import IntVar
from typing import Callable
from wave import Wave_read
from pyaudio import PyAudio, Stream

from config import Config
from mpegh_lib.mpegh_decoder import MPEGHDecoder

import logging

from utils import thread_it
logger = logging.getLogger(__name__)

class BufferSample:
    def __init__(self) -> None:
        self.buffer: None | Wave_read = None # Wave_read, basically bytes, to read from
        self.buffer_event: Event = Event() # Weather the bytes are ready
        self.buffer_config: None | int = None # Which config version the buffer used

    def write(self, buffer: Wave_read | None, config: int):
        self.buffer = buffer
        self.buffer_config = config
        self.buffer_event.set()
    def wait(self):
        self.buffer_event.wait()

    def __str__(self) -> str:
        return f"<BufferSample[{self.buffer is not None}]>"

class Buffer:
    def __init__(self, buffer_size: int = 2) -> None:
        self.buffer_size = buffer_size
        self.buffer_samples: list[BufferSample] = [BufferSample() for _ in range(self.buffer_size)]

    def reset_all_buffer(self, new_buffer_size: int | None = None):
        if new_buffer_size is None:
            new_buffer_size = self.buffer_size
        self.buffer_size = new_buffer_size
        self.buffer_samples = [BufferSample() for _ in range(self.buffer_size)]

    def unset_buffer(self, buffer: BufferSample):
        try:
            index = self.buffer_samples.index(buffer)
            self.buffer_samples[index] = BufferSample()
        except ValueError:
            pass
    def set_buffer(self, frame: int, buffer: Wave_read | None, version: int):
        index = frame % self.buffer_size
        self.buffer_samples[index].write(buffer, version)

    def read_buffer(self, frame: int):
        index = frame % self.buffer_size
        self.buffer_samples[index].wait()
        return self.buffer_samples[index]

class Player:
    def __init__(self, config: Config, buffer_size: int) -> None:
        self.pyaudio_lib = PyAudio()

        self.current_stream: Stream | None = None
        self.current_stream_config: int | None = None

        self._current_frame: int = 0
        self.frame_slider: IntVar | None = None
        self.current_buffer_frame: int = 0

        self.config = config
        self.buffer = Buffer(buffer_size)

        self.is_paused: bool = False
        self.pause_event = Event()
        self.pause_event.set()
        self.abort: bool = False

        self.queued_actions: list[tuple[Callable, tuple, dict, Callable]] = []
        self.new_queued_action: Event = Event()

    def queue_action(self, action: Callable, return_callback: Callable = lambda *_, **__: None, args: tuple = (), kwargs: dict = {}):
        self.queued_actions.append((action, args, kwargs, return_callback))
        self.new_queued_action.set()

    @property
    def chunk(self):
        return self.config.sample_size

    @property
    def current_frame(self):
        if self.frame_slider is not None and self.frame_slider.get() != self._current_frame:
            self.skip_to(self.frame_slider.get())
        return self._current_frame
    @current_frame.setter
    def current_frame(self, value: int):
        self._current_frame = value
        if self.frame_slider is not None:
            self.frame_slider.set(self._current_frame)

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

    def skip_to(self, seconds: int):
        self.current_frame = seconds
        self.current_buffer_frame = seconds
        self.buffer.reset_all_buffer()
        self.fill_buffer(thread_it=False)

    def fill_buffer(self, thread_it: bool):
        while self.current_frame + self.buffer.buffer_size > self.current_buffer_frame:
            logger.info(
                "%s to %s, at %s thread[%s]",
                self.current_frame, self.current_frame + self.buffer.buffer_size,
                self.current_buffer_frame, thread_it
                )
            MPEGHDecoder.decode_sample(
                config = self.config,
                buffer = self.buffer,
                sample_number = self.current_buffer_frame,
                thread_it = thread_it, # type: ignore
            )
            self.current_buffer_frame += 1

    def re_fill_buffer(self, thread_it: bool):
        self.buffer.reset_all_buffer()
        self.current_buffer_frame = self.current_frame
        self.fill_buffer(thread_it=thread_it)

    def play_audio(self, wave: Wave_read):
        logger.info("Reading wave")
        data = wave.readframes(self.chunk)
        while data:
            self.current_stream.write(data) # type: ignore
            data = wave.readframes(self.chunk)
        logger.info("Done playing wave")

    def resume(self):
        self.is_paused = False
        self.pause_event.set()
    def pause(self):
        self.is_paused = True
        self.pause_event.clear()
    def reset(self):
        self.pause()
        self.skip_to(0)

    def perform_queued_actions(self):
        self.new_queued_action.clear()
        while len(self.queued_actions) > 0:
            action, args, kwargs, return_callback = self.queued_actions.pop(0)
            return_callback(
                action(*args, **kwargs)
            )

    @thread_it
    def play(self):
        self.pause_event.wait()
        self.fill_buffer(thread_it=False)
        while not self.abort:
            self.perform_queued_actions()
            logger.info("")
            logger.info("---")
            if self.current_frame >= self.config.duration_in_seconds:
                logger.info("Done with audio. Reseting")
                self.reset()
                continue

            if not self.pause_event.isSet():
                logger.info("Pausing...")
                self.pause_event.wait()
                continue

            curr_frame = self.current_frame
            buffer: BufferSample = self.buffer.read_buffer(curr_frame)
            if buffer.buffer is None:
                logger.info("Empty sample")
                self.current_frame += 1
                continue

            if self.current_stream_config != buffer.buffer_config:
                logger.info("Opening new stream, config version %s", buffer.buffer_config)
                self.close_stream()
                self.set_stream(buffer.buffer)
                self.current_stream_config = buffer.buffer_config

            logger.info("Playing Frame %s", curr_frame)
            self.play_audio(buffer.buffer)
            self.buffer.unset_buffer(buffer)

            self.current_frame += 1

            logger.info("Filling buffer")
            self.fill_buffer(thread_it=True)
