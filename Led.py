# -*- coding: utf-8 -*-
#
#	Autori: Tosatto Davide, Riccardo Grespan
#
#	Modulo che racchiude i metodi per permettere
#   ai LED di lampeggiare in modo casuale
#

import RPi.GPIO as GPIO
import random
import threading

RANGE_A_ON = 0.8
RANGE_B_ON = 3
RANGE_A_OFF = 0.6
RANGE_B_OFF = 1.5

class Led:

    def __init__(self, pin):
        self._pin = pin

    def initialize(self):
        GPIO.setup(self._pin, GPIO.OUT)
        GPIO.output(self._pin, False)

    def blink(self):
        for i in range(randint(4,10)):
            GPIO.output(self._pin, True)
            delay(random.uniform(RANGE_A_ON, RANGE_B_ON))
            GPIO.output(self._pin, False)
            delay(random.uniform(RANGE_A_OFF, RANGE_B_OFF))
        delay(randint(2,10))

    def newThread(self):
        _thread = threading.Thread(target=blink, args=[])
        _thread.start()
