from typing import Dict

import RPi.GPIO as GPIO

from .utils import *

# This will be a full HAL for the drv8833 driver circuit by texas instruments for rpis
# specifically the pcb made by adafruit although others would probably work

# Terminology:
# Speed = Duty Cycle
# Torque ~= Frequency
# lower freq == more torque for standard dc motors
from .utils import Pins


# noinspection PyPep8Naming
class DRV8833:
    def __init__(self, pinmode, pinmap: Dict[Pins, int], freqmap: Dict[Pins, int]):

        self.AIN1 = None  # These are instances of GPIO.PWM
        self.AIN2 = None
        self.BIN1 = None
        self.BIN2 = None

        self.__SLP_PINNUM = None  # these are not real pins, they just represent which pins
        self.__FLT_PINNUM = None  # are used if any

        # None value indicates unconnected pin
        # assertions/sanity checks
        self.verify_map(pinmap)
        self.verify_map(freqmap)
        self.verify_pinmode(pinmode)

        self.pinmap = pinmap
        self.freqmap = freqmap
        self.is_setup = False
        self.pinmode = pinmode
        self.setup()

    @staticmethod
    def verify_map(map: Dict[Pins, int]):
        # these pins are required
        assert map.get(Pins.AIN1) is not None
        assert map.get(Pins.AIN2) is not None
        assert map.get(Pins.BIN1) is not None
        assert map.get(Pins.BIN2) is not None

        # even if these pins are not set, its ok
        map.setdefault(Pins.SLP, None)
        map.setdefault(Pins.FLT, None)

    @staticmethod
    def verify_pinmode(pinmode):
        assert pinmode == GPIO.BCM or pinmode == GPIO.BOARD

    @staticmethod
    def verify_speed(speed: float):
        assert 0.0 <= speed <= 100.0

    @staticmethod
    def verify_freq(freq):
        assert freq >= 0

    @property
    def SLP(self):
        if not self.is_setup:
            return

        if not self.__SLP_PINNUM:
            return

        return GPIO.input(self.__SLP_PINNUM)

    @property
    def FLT(self):
        if not self.is_setup:
            return

        if not self.__FLT_PINNUM:
            return

        return GPIO.input(self.__FLT_PINNUM)

    def setup(self):
        if self.is_setup:
            print('DRV8833 has already been setup')
            return

        # reduce verbosity of code
        pinmap = self.pinmap
        freqmap = self.freqmap

        GPIO.setwarnings(False)
        GPIO.setmode(self.pinmode)
        GPIO.setup(pinmap.get(Pins.AIN1), GPIO.OUT)
        GPIO.setup(pinmap.get(Pins.AIN2), GPIO.OUT)
        GPIO.setup(pinmap.get(Pins.BIN1), GPIO.OUT)
        GPIO.setup(pinmap.get(Pins.BIN2), GPIO.OUT)

        # all pin objects correspond to the names in the `Pins` enum
        self.AIN1 = GPIO.PWM(pinmap.get(Pins.AIN1), freqmap.get(Pins.AIN1))
        self.AIN2 = GPIO.PWM(pinmap.get(Pins.AIN2), freqmap.get(Pins.AIN2))
        self.BIN1 = GPIO.PWM(pinmap.get(Pins.BIN1), freqmap.get(Pins.BIN1))
        self.BIN2 = GPIO.PWM(pinmap.get(Pins.BIN2), freqmap.get(Pins.BIN2))

        # set duty cycle to 0
        # duty cycle must be 0.0 <= x <= 100.0
        self.AIN1.start(0)
        self.AIN2.start(0)
        self.BIN1.start(0)
        self.BIN2.start(0)

        # handle the inputs (sleep and fault pins)
        self.__SLP_PINNUM = pinmap.get(Pins.SLP)
        self.__FLT_PINNUM = pinmap.get(Pins.FLT)

        if self.__SLP_PINNUM is not None:
            GPIO.setup(self.__SLP_PINNUM, GPIO.IN)

        if self.__FLT_PINNUM is not None:
            GPIO.setup(self.__FLT_PINNUM, GPIO.IN)

        self.is_setup = True

    @staticmethod
    def cleanup():
        GPIO.cleanup()

    def stop_all(self):
        self.stop_motor_a()
        self.stop_motor_b()

    def stop_motor_a(self):
        stop(self.AIN1)
        stop(self.AIN2)

    def stop_motor_b(self):
        stop(self.BIN1)
        stop(self.BIN2)

    def set_motor(self, speed, direction, motor: Motor):
        self.verify_speed(speed)

        if direction is Direction.FORWARD:
            motor.pin1.ChangeDutyCycle(speed)
            motor.pin2.ChangeDutyCycle(0)

        elif direction is Direction.BACKWARD:
            motor.pin1.ChangeDutyCycle(0)
            motor.pin2.ChangeDutyCycle(speed)

        else:
            raise RuntimeError("Invalid Direction %s Provided" % direction)

    def set_motor_a(self, speed, direction: Direction):
        self.set_motor(speed, direction, Motor(self.AIN1, self.AIN2))

    def set_motor_b(self, speed: float, direction: Direction):
        self.set_motor(speed, direction, Motor(self.BIN1, self.BIN2))

    def change_frequency(self, newFreq: float, motor: Motor):
        self.verify_freq(newFreq)

        motor.pin1.ChangeFrequency(newFreq)
        motor.pin2.ChangeFrequency(newFreq)

    def change_frequency_a(self, newFreq: float):
        self.change_frequency(newFreq, Motor(self.AIN1, self.AIN2))

    def change_frequency_b(self, newFreq: float):
        self.change_frequency(newFreq, Motor(self.BIN1, self.BIN2))
