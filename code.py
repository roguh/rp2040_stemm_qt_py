import random
import sys
import time

import adafruit_framebuf
import alarm
import digitalio
import microcontroller
import neopixel
import board
import rtc
from rainbowio import colorwheel

from epaper_2in13_b import EPD_2in13_B

MONTH_ABBRVS = "jan feb mar apr may jun jul aug sep oct nov dec".upper().split()

true_rtc = rtc.RTC()
# Sequence of time info:
# (tm_year, tm_mon, tm_mday, tm_hour, tm_min, tm_sec, tm_wday, tm_yday, tm_isdst)
true_rtc.datetime = time.struct_time(
    (
        2022,
        10,
        29,
        23,
        53,
        00,
        0,
        -1,
        -1,
    )
)


# Turn on the NeoPixel
pixel_power = digitalio.DigitalInOut(board.GP11)
pixel_power.direction = digitalio.Direction.OUTPUT
pixel_power.value = True

pixel = neopixel.NeoPixel(board.GP12, 1, pixel_order=neopixel.GRB)
pixel.brightness = 1

# This is the BOOT button
boot_pin = board.GP21
# boot_button = digitalio.DigitalInOut(boot_pin)
# boot_button.switch_to_input(pull=digitalio.Pull.UP)


def rainbow(delay, iterable=range(255)):
    for color_value in iterable:
        pixel[0] = colorwheel(color_value)
        time.sleep(delay)


def print_cpu_info(index):
    cpu = microcontroller.cpus[index]
    print(
        "CPU",
        index,
        "info",
        cpu.temperature,
        "degrees C",
        cpu.voltage,
        "volts",
        cpu.frequency / 1e6,
        "Mhz",
        cpu.reset_reason,
    )


def print_sys_info():
    print("Python", sys.version, sys.implementation, "platform =", sys.platform)


def print_info():
    print(time.monotonic())
    print_cpu_info(0)
    print_cpu_info(1)
    print_sys_info()
    # print("BOOT button", boot_button.value)


epd = EPD_2in13_B(init_display=False)

# Golden ratio something something
top = int(epd.height * (1 - 2 * 0.1545084971874737))

font_width = 5
font_height = 8

margin = font_height // 4


def centered(image, msg, y=0, size=1):
    # type: (adafruit_framebuf.FrameBuffer, str, int, int) -> None
    image.text(
        msg,
        int((epd.width - (len(msg) * size - 1) - len(msg) * font_width * size) / 2),
        y,
        color=0,
        size=size,
    )


def copy_img(image, source_bytes, start_y=0):
    # type: (adafruit_framebuf.FrameBuffer, bytes, int) -> None
    offset = start_y * image.width // 8
    for i, b in enumerate(source_bytes):
        image.buf[i + offset] = image.buf[i + offset] & b


with open("r.raw", "rb") as infile:
    red_petals = infile.read()
with open("b.raw", "rb") as infile:
    black_stem = infile.read()
with open("hugo_square-bw.raw", "rb") as infile:
    signature = infile.read()


def main():

    while True:
        start_time = time.monotonic()
        pixel[0] = (100, 100, 100)
        print("Initializing screen")
        epd.init()

        date = time.localtime()
        many_times_string = "%02d_%02d_%02d" % (
            date.tm_hour - 1,
            date.tm_hour + 2,
            (date.tm_hour + 8) % 24,
        )

        print("Drawing time", date)

        # Clear images
        epd.imageblack.fill(0xFF)
        epd.imagered.fill(0xFF)

        copy_img(epd.imagered, red_petals)
        copy_img(epd.imageblack, black_stem)
        copy_img(epd.imageblack, signature, start_y=epd.height // 2 - 10)

        # centered(epd.imagered, "HOWDY!", 10, size=2)
        centered(
            epd.imagered,
            "%d %s %02d"
            % (date.tm_mday, MONTH_ABBRVS[date.tm_mon - 1], date.tm_year % 1000),
            5,
            size=2,
        )
        centered(
            epd.imageblack,
            "%02d:%02d" % (date.tm_hour, date.tm_min),
            top + font_height * 2 + margin,
            size=3,
        )
        centered(
            epd.imagered, many_times_string, top + font_height * 5 + margin * 2, size=2
        )
        epd.display()
        epd.sleep()

        # print("Last awakening due to:", alarm.wake_alarm)
        print(time.monotonic(), "rainbow")
        print_info()

        for _ in range(1):
            rainbow(0.005)
            rainbow(0.005, range(255, -1, -1))

        print_info()

        # time_alarm = alarm.time.TimeAlarm(monotonic_time=time.monotonic() + 5)
        # # boot_button_alarm = alarm.pin.PinAlarm(boot_pin, value=False, pull=True)
        # alarm.light_sleep_until_alarms(time_alarm)
        # print("Last awakening due to:", alarm.wake_alarm)

        print(time.monotonic(), "random rainbow")
        print_info()

        rainbow(0.02, [random.randint(0, 255) for _ in range(100)])

        pixel[0] = (0, 0, 0)
        end_time = time.monotonic()
        loop_time = end_time - start_time
        print("loop duration:", loop_time)

        extra_wait = 5
        i = 0
        base = 50
        t = time.localtime()
        while t.tm_sec < min(10, 60 - (extra_wait + loop_time)):
            pixel[0] = (base * (i % 3), 0, base * (1 - i % 3))
            i += 1
            time.sleep(0.2)
            print("waiting", t.tm_sec, extra_wait + loop_time)
            t = time.localtime()

        # time_alarm = alarm.time.TimeAlarm(monotonic_time=time.monotonic() + 10)
        # NOT WORKING
        # alarm.light_sleep_until_alarms(time_alarm)
        # NOT WORKING
        # alarm.exit_and_deep_sleep_until_alarms(time_alarm)


try:
    main()
except Exception as exc:
    print("EXCEPTION ENCOUNTERED!!!", exc)
    epd.sleep()
