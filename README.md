# rp2040_stemm_qt_py

## See serial output

```
screen /dev/ttyACM0 9600
```

OR run:

```
make open-serial-console
```

Press Ctrl-C and then any key to enter the REPL. You will also see hot
reloading is enabled when the REPL is not running.

## Copy to the device

```
make cp
```

If you have a compatible version of mpy-cross installed, then run:

```
make cp-compile
```

## Firmware

CircuitPython 8.0.0 firmware is from

https://circuitpython.org/board/waveshare_rp2040_zero/

## Copy this into the lib/

Neopixel and framebuf

https://github.com/adafruit/Adafruit_CircuitPython_Bundle/releases/download/20221029/adafruit-circuitpython-bundle-8.x-mpy-20221029.zip
https://github.com/adafruit/Adafruit_CircuitPython_framebuf/releases/download/1.4.14/adafruit-circuitpython-framebuf-8.x-mpy-1.4.14.zip

More found in community bundle

https://github.com/adafruit/CircuitPython_Community_Bundle/releases/download/20221027/circuitpython-community-bundle-8.x-mpy-20221027.zip

## mpy-cross compiler

Find the latest compatible version in https://adafruit-circuit-python.s3.amazonaws.com/index.html?prefix=bin/mpy-cross/

I used
https://adafruit-circuit-python.s3.amazonaws.com/bin/mpy-cross/mpy-cross.static-amd64-linux-8.0.0-beta.3-29-ga0f389e28

Reference: https://learn.adafruit.com/creating-and-sharing-a-circuitpython-library?view=all#mpy-2982472-11

## Useful links

https://learn.adafruit.com/adafruit-qt-py-2040/troubleshooting

https://learn.adafruit.com/Memory-saving-tips-for-CircuitPython?view=all

https://github.com/todbot/circuitpython-tricks#inputs


## Future plans

Integration testing? https://github.com/adafruit/Adafruit_Blinka
