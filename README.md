# Introduction

Arpeggion-H is a MPEG-H player, that can work with MP4-MHM1 coded files trough third party implementations of the decoder. It allows the user to interact with the audio elements and its propreties trough an interface built on demand based on the incoming MP4 file.

## How to Setup

Build both "Mpeg-h ui manager" and "mpgeh decoder" from [Fraunhofer/MPEG-H Decoder](https://github.com/Fraunhofer-IIS/mpeghdec?tab=readme-ov-file) using their [How to build MPEG-H UI Manager](https://github.com/Fraunhofer-IIS/mpeghdec/wiki/MPEG-H-UI-manager-example#how-to-build) (it should build both binaries)

Move both binaries to "bin" and rename them to "mpegh_decoder" and "mpegh_ui_manager"

You can also find MP4 samples in their [test-repository](https://github.com/Fraunhofer-IIS/mpegh-test-content)

You must install, trough pip (all listed at `requirements.txt`):

- Tkinter (`pip install tk`)
- PyAudio (`pip install pyaudio`)

## How to run

You can run trough `make run`, or the src folder trough python as `python3 src [-file <file_name>]`, where `file_name` is the file containted inside the audio folder in this directory. If no file is given, the app will open empty. Click on `File > Open` and select your audio.mp4 file to be played.
