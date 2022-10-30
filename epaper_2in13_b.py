# *****************************************************************************
# * | File        :	  epaper_2in13_b.py
# * | Author      :   Waveshare team and Hugo O. Rivera
# * | Function    :   Electronic paper driver
# * | Info        :
# *----------------
# * | This version:   V0.1
# * | Date        :   2022
# # | Info        :   python library and demo
# -----------------------------------------------------------------------------
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documnetation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to  whom the Software is
# furished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS OR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

import time

import adafruit_framebuf
import board
from adafruit_framebuf import FrameBuffer
from busio import SPI
from digitalio import DigitalInOut, Direction, Pull

EPD_WIDTH = 104
EPD_HEIGHT = 212

# Either MHMSB or MVLSB
PIXEL_FORMAT = adafruit_framebuf.MHMSB

# Pico Zero: MOSI aka GPIO3 aka TX0 (transmit) for SPI protocol
# Waveshare: DIN aka MOSI pin of SPI interface, data transmitted from Master to Slave.
SPI_MOSI_PIN = board.GP3

# Pico Zero: MISO aka GPIO4 aka RX0 (receive) for SPI protocol
# Waveshare: DC aka Data/Command control pin (High: Data; Low: Command)
# CircuitPython tutorial: MISO = main output, secondary input\u2019
SPI_MISO_PIN = board.GP4

# Pico Zero: RX aka GPIO5 aka CSn0 (chip select) for SPI protocol
# Waveshare: CS aka Chip select pin of SPI interface, Low active
# CircuitPython tutorial: most chips have a CS, or chip select, wire which is toggled to tell the chip that it should listen and respond to requests on the SPI bus. Each device requires its own unique CS line.
SPI_CHIP_SELECT_PIN = board.GP5

# Pico Zero: SCK aka GPIO6 aka SCK0 (SPI clock) for SPI protocol
# Waveshare: CLK aka SCK pin of SPI interface, clock input
# CircuitPython tutorial: most chips have a CS, or chip select, wire which is toggled to tell the chip that it should listen and respond to requests on the SPI bus. Each device requires its own unique CS line.
SPI_CLOCK_PIN = board.GP6

# Do the RST and BUSY pins just function as GPIO pins or is it part of the SPI protocol?

# Pico Zero: SDA aka GPIO24 aka RXn1 (receive) for SPI protocol ??
# Waveshare: RST aka Reset pin, low active
EPAPER_RESET_PIN = board.GP24

# Pico Zero: SCL aka GPIO25 aka CSn1 (clock select) for SPI protocol ??
# Waveshare: BUSY aka Busy pin
EPAPER_BUSY_PIN = board.GP25


buffer_black = bytearray(EPD_HEIGHT * EPD_WIDTH // 8)
imageblack = FrameBuffer(buffer_black, EPD_WIDTH, EPD_HEIGHT, PIXEL_FORMAT)
# import epaper_2in13_b as e


class EPD_2in13_B:
    def __init__(self, init_display=True):
        """If init_display is False, remember to call init() manually."""
        self.reset_pin = DigitalInOut(EPAPER_RESET_PIN)
        self.reset_pin.direction = Direction.OUTPUT

        self.busy_pin = DigitalInOut(EPAPER_BUSY_PIN)
        self.busy_pin.direction = Direction.INPUT
        self.busy_pin.pull = Pull.UP

        self.cs_pin = DigitalInOut(SPI_CHIP_SELECT_PIN)
        self.cs_pin.direction = Direction.OUTPUT

        self.dc_pin = DigitalInOut(SPI_MISO_PIN)
        self.dc_pin.direction = Direction.OUTPUT

        self.width = EPD_WIDTH
        self.height = EPD_HEIGHT

        self.spi = SPI(SPI_CLOCK_PIN, MOSI=SPI_MOSI_PIN)

        if not self.spi.try_lock():
            raise RuntimeError("SPI device is locked")
        self.spi.configure(baudrate=4_000_000)
        self.spi.unlock()

        self.buffer_black = bytearray(self.height * self.width // 8)
        self.buffer_red = bytearray(self.height * self.width // 8)
        self.imageblack = FrameBuffer(
            self.buffer_black, self.width, self.height, PIXEL_FORMAT
        )
        self.imagered = FrameBuffer(
            self.buffer_red, self.width, self.height, PIXEL_FORMAT
        )
        if init_display:
            self.init()

    def digital_write(self, pin, value):
        pin.value = value

    def digital_read(self, pin):
        return pin.value

    def delay_ms(self, delaytime):
        time.sleep(delaytime / 1000)

    def spi_writebyte(self, data):
        if not self.spi.try_lock():
            raise RuntimeError("SPI device is locked")
        self.spi.write(bytearray(data))
        self.spi.unlock()

    def module_exit(self):
        self.digital_write(self.reset_pin, 0)

    # Hardware reset
    def reset(self):
        print("resetting epd")
        self.digital_write(self.reset_pin, 1)
        self.delay_ms(50)
        self.digital_write(self.reset_pin, 0)
        self.delay_ms(2)
        self.digital_write(self.reset_pin, 1)
        self.delay_ms(50)

    def send_command(self, command):
        # print("sending command", command)
        self.digital_write(self.dc_pin, 0)
        self.digital_write(self.cs_pin, 0)
        self.spi_writebyte([command])
        self.digital_write(self.cs_pin, 1)

    def send_data(self, data):
        # print("sending data", data)
        self.digital_write(self.dc_pin, 1)
        self.digital_write(self.cs_pin, 0)
        self.spi_writebyte([data])
        self.digital_write(self.cs_pin, 1)

    def ReadBusy(self):
        start_time = time.monotonic()
        print("epd screen will be busy")
        self.send_command(0x71)
        while self.digital_read(self.busy_pin) == 0:
            self.send_command(0x71)
            self.delay_ms(10)
        print("epd screen was busy for", time.monotonic() - start_time, "seconds")

    def TurnOnDisplay(self):
        self.send_command(0x12)
        self.ReadBusy()

    def init(self):
        print("epd init")
        self.reset()
        self.send_command(0x04)
        self.ReadBusy()  # waiting for the electronic paper IC to release the idle signal

        self.send_command(0x00)  # panel setting
        self.send_data(0x0F)  # LUT from OTP,128x296
        self.send_data(
            0x89
        )  # Temperature sensor, boost and other related timing settings

        self.send_command(0x61)  # resolution setting
        self.send_data(0x68)
        self.send_data(0x00)
        self.send_data(0xD4)

        self.send_command(0x50)  # VCOM AND DATA INTERVAL SETTING
        self.send_data(0x77)  # WBmode:VBDF 17|D7 VBDW 97 VBDB 57
        # WBRmode:VBDF F7 VBDW 77 VBDB 37  VBDR B7
        return 0

    def display(self):
        self.send_command(0x10)
        for j in range(0, self.height):
            for i in range(0, int(self.width / 8)):
                self.send_data(self.buffer_black[i + j * int(self.width / 8)])
        self.send_command(0x13)
        for j in range(0, self.height):
            for i in range(0, int(self.width / 8)):
                self.send_data(self.buffer_red[i + j * int(self.width / 8)])

        self.TurnOnDisplay()

    def Clear(self, fillblack=False, fillred=False):
        if fillblack:
            colorblack = 0
        else:
            colorblack = 0xFF

        if fillred:
            colorred = 0
        else:
            colorred = 0xFF

        print("epd clearing")
        self.send_command(0x10)
        for j in range(0, self.height):
            for i in range(0, int(self.width / 8)):
                self.send_data(colorblack)
        self.send_command(0x13)
        for j in range(0, self.height):
            for i in range(0, int(self.width / 8)):
                self.send_data(colorred)

        self.TurnOnDisplay()

    def sleep(self):
        self.send_command(0x50)
        self.send_data(0xF7)
        self.send_command(0x02)
        self.ReadBusy()
        self.send_command(0x07)  # DEEP_SLEEP
        self.send_data(0xA5)  # check code

        self.delay_ms(2000)
        self.module_exit()


def main():
    print("DEMO Initializing and clearing screen")
    epd = EPD_2in13_B()
    epd.Clear(fillred=True)

    print("DEMO Drawing text")
    epd.imageblack.fill(0xFF)
    epd.imagered.fill(0xFF)
    epd.imageblack.text("Waveshare", 0, 10, 0x00)
    epd.imagered.text("ePaper-2.13", 0, 25, 0x00)
    epd.imageblack.text("RPi Pico Zero", 0, 40, 0x00)
    epd.imagered.text("Hello World", 0, 55, 0x00)
    epd.display()
    epd.delay_ms(2000)

    print("DEMO Drawing lines")
    epd.imagered.vline(10, 90, 40, 0x00)
    epd.imagered.vline(90, 90, 40, 0x00)
    epd.imageblack.hline(10, 90, 80, 0x00)
    epd.imageblack.hline(10, 130, 80, 0x00)
    epd.imagered.line(10, 90, 90, 130, 0x00)
    epd.imageblack.line(90, 90, 10, 130, 0x00)
    epd.display()
    epd.delay_ms(3000)

    epd.imageblack.rect(10, 150, 40, 40, 0x00)
    epd.imagered.fill_rect(60, 150, 40, 40, 0x00)
    epd.display()
    epd.delay_ms(2000)

    epd.Clear()
    epd.delay_ms(3000)

    print("DEMO putting screen into low-voltage sleep mode")
    print(
        "DEMO WARNING: If the screen is not in sleep mode or powered off, it will remain in a high voltage state for a long time, which will damage the e-Paper and cannot be repaired!"
    )
    epd.sleep()


if __name__ == "__main__":
    main()
