import random
import sys
import time

import alarm
import digitalio
import microcontroller
import neopixel
from rainbowio import colorwheel

# Turn on the NeoPixel
pixel_power = digitalio.DigitalInOut(microcontroller.pin.GPIO11)
pixel_power.direction = digitalio.Direction.OUTPUT
pixel_power.value = True

pixel = neopixel.NeoPixel(microcontroller.pin.GPIO12, 1, pixel_order=neopixel.GRB)
pixel.brightness = 1

# This is the BOOT button
boot_pin = microcontroller.pin.GPIO21
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


while True:
    print('Last awakening due to:', alarm.wake_alarm)
    print(time.monotonic(), "rainbow")
    print_info()

    for _ in range(3):
        rainbow(0.005)
        rainbow(0.005, range(255, -1, -1))

    print_info()

    time_alarm = alarm.time.TimeAlarm(monotonic_time=time.monotonic() + 10)
    boot_button_alarm = alarm.pin.PinAlarm(boot_pin, value=False, pull=True)
    alarm.light_sleep_until_alarms(time_alarm, boot_button_alarm)
    # TODO how to deep sleep until the BOOT button is pressed? may not be possible
    # alternative: press RESET

    print(time.monotonic(), "random rainbow")
    print('Last awakening due to:', alarm.wake_alarm)
    print_info()

    rainbow(0.05, [random.randint(0, 255) for _ in range(100)])

    time_alarm = alarm.time.TimeAlarm(monotonic_time=time.monotonic() + 5)
    alarm.exit_and_deep_sleep_until_alarms(time_alarm)
