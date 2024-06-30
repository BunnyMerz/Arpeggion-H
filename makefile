PYTHON := python3

run:
	$(PYTHON) src

clean:
	rm ./tmp/audio/*.wav
	rm ./tmp/audio/*.mp4
	rm ./tmp/config/*.xml
	rm ./tmp/script/*.xml

