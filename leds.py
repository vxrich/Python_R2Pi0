# -*- coding: utf-8 -*-
#
#	Autori: Tosatto Davide, Riccardo Grespan
#
#	Modulo per la gestione dei led
#
import RPi.GPIO as GPIO
import pinout

DEFAULT_BRIGTHNESS = 0
PWM_FREQ = 1000

class Led:

    def __init__(self, pin):
        self._pin = pin
        self._pwm = None

    def initialize (self, brigthness=DEFAULT_BRIGTHNESS):
        GPIO.setup(self._pin, GPIO.OUT)
        self._pwm = GPIO.PWM(self._pin, PWM_FREQ)

    def setBrigthness (self, brigthness):

        if brigthness < 0:
            brigthness = 0
        elif brigthness > 100
            brigthness = 100

        self._pwm.ChangeDutyCycle(brigthness)






if __name__ == "__main__":

    GPIO.setmode(GPIO.BCM)

    ld = Led(2)

    ld.initialize(100)

    GPIO.cleanup()
