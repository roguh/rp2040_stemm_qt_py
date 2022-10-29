SERIAL_DEVICE=/dev/ttyACM0
PYFILE=code.py
COMPILED_PYFILE=compiled_code.mpy
BASE_DEST:=/run/media/$(shell whoami)
BOOT_DEST=${BASE_DEST}/RPI-RP2
DEST:=${BASE_DEST}/CIRCUITPY
MPY_CROSS_COMPILER=./deps/mpy-cross.static-amd64-linux-8.0.0-beta.3-29-ga0f389e28
# TODO use the circ... dep manager
LIBS=./adafruit-circuitpython-bundle-8.x-mpy-20221029/lib/{adafruit_pixelbuf.mpy,neopixel.mpy} \
		 ./adafruit-circuitpython-framebuf-8.x-mpy-1.4.14/lib/adafruit_framebuf.mpy

FIRMWARE=./adafruit-circuitpython-waveshare_rp2040_zero-en_US-8.0.0-beta.3.uf2

cp:
	rm ${DEST}
	cp ${PYFILE} ${DEST}

cp-compile:
	${MPY_CROSS_COMPILER} ${PYFILE} -o ${COMPILED_PYFILE}
	rm ${DEST}/code.py ${DEST}/${COMPILED_PYFILE}
	cp main_for_compiled.py ${DEST}/code.py
	cp ${COMPILED_PYFILE} ${DEST}

dev:
	watch -n1 \
		'diff ${DEST}/${PYFILE} ${PYFILE} \
			&& echo No changes detected \
			|| make cp'

dev-compile:
	watch -n1 \
		'diff ${DEST}/${COMPILED_PYFILE} ${COMPILED_PYFILE} \
			&& echo No changes detected \
			|| make cp-compile'

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

install-libraries:
	@echo Installing libraries
	cp ${LIBS} ${DEST}/lib
