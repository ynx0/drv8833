from collections import namedtuple
from enum import Enum, auto
from typing import NamedTuple

import RPi.GPIO as GPIO


class Pins(Enum):
    AIN1 = auto()  # ain1 and ain2 are the way to control motor a
    AIN2 = auto()
    BIN1 = auto()  # same as ain1 and ain2 for motor b respectively
    BIN2 = auto()
    # optional pins...
    SLP = auto()
    FLT = auto()  # gets driven low if circuit is shutdown for any reason


class Direction(Enum):
    FORWARD = auto()
    BACKWARD = auto()


# simple typedef kinda thing
# from https://stackoverflow.com/a/42002613, use backwards compat syntax until python3.5+ is avail on pi
# class Motor(NamedTuple):
#     pin1: GPIO.PWM
#     pin2: GPIO.PWM

Motor = NamedTuple('Motor', [('pin1', GPIO.PWM), ('pin2', GPIO.PWM)])


def stop(pwm: GPIO.PWM):
    pwm.ChangeDutyCycle(0)


def clamp(value, maximum, minimum):
    # min(...) ensures that the value is not greater than the maximum
    # max(...) ensures that the value is not less than the minimum
    # combining these two allows you to set bounds
    return max(min(value, maximum), minimum)
