# -*- coding: utf-8 -*-
#
#	Autori: Tosatto Davide, Riccardo Grespan
#
#	Modulo per la gestione dei led
#
import RPi.GPIO as GPIO
import pinout
import time
import random as rnd
import threading

DEFAULT_BRIGTHNESS = 0
PWM_FREQ = 100

class Led:

    def __init__(self, pin):
        self._pin = pin
        self._pwm = None

    def initialize (self, brigthness=DEFAULT_BRIGTHNESS):
        GPIO.setup(self._pin, GPIO.OUT)
        self._pwm = GPIO.PWM(self._pin, PWM_FREQ)
        self._pwm.start(brigthness)

    def setBrigthness (self, brigthness):

        if brigthness < 0:
            brigthness = 0
        elif brigthness > 100:
            brigthness = 100

        self._pwm.ChangeDutyCycle(brigthness)


class RGBLed:

    def __init__(self, pinr, ping, pinb):
        self._ledr = Led(pinr)
        self._ledg = Led(ping)
        self._ledb = Led(pinb)

    def initialize (self, r=DEFAULT_BRIGTHNESS, g=DEFAULT_BRIGTHNESS, b=DEFAULT_BRIGTHNESS):
        self._ledr.initialize(r)
        self._ledg.initialize(g)
        self._ledb.initialize(b)

    def setColor (self, r, g, b):
        self._ledr.setBrigthness(r)
        self._ledg.setBrigthness(g)
        self._ledb.setBrigthness(b)


class LedEye:

    def _to100 (self, prob):
        return 100 - prob*100

    def __init__(self, led, rprob=0.2, rtimemin=0.1, rtimemax=1.5, bprob=0.1, btimemin=0.05, btimemax=0.1, timestep=0.05):
        self._led = led
        self._stop = False

        self._rp = self._to100(rprob)
        self._bp = self._to100(bprob)

        self._rtmin = rtimemin
        self._rtmax = rtimemax

        self._btmin = btimemin
        self._btmax = btimemax

        self._ts = timestep

        self._thread = threading.Thread(target=self._cycle)

    def start (self):
        self._thread.start()

    def stop (self):
        self._stop = True

    def _cycle (self):

        rand = rnd.Random()

        ron = False
        rstop = 0

        bon = False
        bstop = 0

        r = 0
        b = 0

        while not self._stop:
            if (ron == False and rand.randint(1,100)>self._rp):
                ron = True
                rstop = time.time() + rand.uniform(self._rtmin, self._rtmax)
                r = 100

            if (bon == False and rand.randint(1,100)>self._bp):
                bon = True
                bstop = time.time() + rand.uniform(self._btmin, self._btmax)
                b = 100

            if (ron == True and time.time() > rstop):
                ron = False
                r = 0

            if (bon == True and time.time() > bstop):
                bon = False
                b = 0

            self._led.setColor(r, 0, b)

            time.sleep(self._ts)

if __name__ == "__main__":

    GPIO.setmode(GPIO.BOARD)

    ld = RGBLed(7, 3, 5)

    ld.initialize()

    ledeye = LedEye(ld)
    ledeye.start()

    raw_input("Press Enter to exit...")

    ledeye.stop()



    GPIO.cleanup()
