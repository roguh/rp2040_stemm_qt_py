SERIAL_DEVICE=/dev/ttyACM0
PYFILE=code.py
PYFILE_COPY=.${PYFILE}.bak
COMPILED_PYFILE=compiled_code.mpy
BASE_DEST:=/run/media/$(shell whoami)
BOOT_DEST=${BASE_DEST}/RPI-RP2
DEST:=${BASE_DEST}/CIRCUITPY
MPY_CROSS_COMPILER=./deps/mpy-cross.static-amd64-linux-8.0.0-beta.3-29-ga0f389e28
# TODO use the circ... dep manager
LIBS=./deps/adafruit-circuitpython-bundle-8.x-mpy-20221029/lib/{adafruit_pixelbuf.mpy,neopixel.mpy} \
		 ./deps/adafruit-circuitpython-framebuf-8.x-mpy-1.4.14/lib/adafruit_framebuf.mpy

FONTS=./deps/adafruit-circuitpython-framebuf-8.x-mpy-1.4.14/examples/font5x8.bin

EPD=./epaper_2in13_b.py
COMPILED_EPD=./epaper_2in13_b.mpy

FIRMWARE=./deps/adafruit-circuitpython-waveshare_rp2040_zero-en_US-8.0.0-beta.3.uf2

cp:
	rm ${DEST}/*.py
	cp ${PYFILE} ${DEST}

cp-compile:
	${MPY_CROSS_COMPILER} ${PYFILE} -o ${COMPILED_PYFILE}
	rm ${DEST}/code.py ${DEST}/${COMPILED_PYFILE}
	cp main_for_compiled.py ${DEST}/code.py
	cp ${COMPILED_PYFILE} ${DEST}

compile-libraries:
	${MPY_CROSS_COMPILER} ${EPD} -o ${COMPILED_EPD}
	rm -f ${DEST}/${COMPILED_EPD}
	cp ${COMPILED_EPD} ${DEST}

dev:
	watch -n1 \
		'diff ${DEST}/${PYFILE} ${PYFILE} \
			&& echo No changes detected \
			|| make cp'

dev-compile:
	watch -n1 \
		'diff ${PYFILE_COPY} ${PYFILE} \
			&& echo No changes detected \
			|| make cp-compile \
			; cp ${PYFILE} ${PYFILE_COPY}'

open-serial-console:
	# Baud rate is 9600 bits per second
	screen ${SERIAL_DEVICE} 9600

install-python:
	@[ -d ${BOOT_DEST} ] \
		|| ( echo Directory ${BOOT_DEST} not found. Press the reset button twice && exit 1 )
	@echo Installing the CircuitPython firmware
	cp ${FIRMWARE} ${BASE_DEST}/RPI-RP2
	@echo Will loop until ${DEST} is mounted
	while [ ! -d ${DEST} ] ; do sleep 1 ; done
	make install-libraries

install-libraries: compile-libraries
	@echo Installing libraries
	cp ${FONTS} ${DEST}/
	cp ${COMPILED_EPD} ${DEST}/lib
	cp ${LIBS} ${DEST}/lib

download-deps:
	@echo Read the README to see what deps must be downloaded
	@echo TODO: Automate this

clean:
	${PYFILE_COPY}
	${COMPILED_PYFILE}
