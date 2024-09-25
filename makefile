PYTHON := python3
PYINSTALLER := pyinstaller
EXE_NAME := arpeggion_h

run:
	$(PYTHON) src

clean:
	-rm ./tmp/audio/*.wav
	-rm ./tmp/audio/*.mp4
	-rm ./tmp/config/*.xml
	-rm ./tmp/script/*.xml

build:
	-rm ./dist/$(EXE_NAME)
	$(PYINSTALLER) src/__main__.py --name $(EXE_NAME) --onefile
	-rm -rf ./build