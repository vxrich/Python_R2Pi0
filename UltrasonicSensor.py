# -*- coding: utf-8 -*-
#
#	Autori: Tosatto Davide, Riccardo Grespan
#
#	Modulo per il controllo del sensore a ultrasuoni
#   Ritorna la distanza in metri e monitora
#   tramite un thread il variare della distanza
#

import RPi.GPIO as GPIO
import time
import threading
import pinout
import proxsensor

TIME_OUT = 50
SIGNAL_DELAY = 0.00001
SOUND_CONST = 171.50
WAIT_TIME = 0.05

#TODO: La classe nel complesso sembra ok, ma chiaramente non è stata testata perchè
#      così certamente non parte, ci sono errori di sintassi

#IMPORTANTE: il trigger e' input per il sensore ma out per la raspberry
# e l'echo e' output per il sensore ma input per la raspberry
# i nomi vengono considerati guardando dal lato raspberry
class Sensor:

	def __init__(self, pin_out, pin_in):
		self._trig = pin_out
		self._echo = pin_in
		self._distance = None
		self._pulse_start = None
		self._pulse_end = None
		self._pulse_duration = None

	def initialize(self):
		GPIO.setup(self._echo, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
		GPIO.setup(self._trig, GPIO.OUT)
		GPIO.output(self._trig, False)

	def _xchangeSignal(self):
		GPIO.output(self._trig, True)
		time.sleep(SIGNAL_DELAY)
		GPIO.output(self._trig, False)

		begin = time.time()

		while GPIO.input(self._echo)==0:
			self._pulse_start = time.time()
			if (begin - self._pulse_start) > 0.05:
				time.sleep(0.002)

		begin = time.time()

		while GPIO.input(self._echo)==1:
			self._pulse_end = time.time()
			if (begin - self._pulse_end) > 0.05:
				time.sleep(0.002)

		if self._pulse_end != None and self._pulse_start != None:
			self._pulse_duration = self._pulse_end - self._pulse_start

			self._distance = self._pulse_duration*SOUND_CONST
			self._distance = round(self._distance,2)

	def getDistance(self):

		return self._distance

	def startCheck(self):
		self._xchangeSignal()


#        while 1:
#            self._xchangeSignal()
#            self._getter()
#            time.sleep(WAIT_TIME)

#L'ECHO sarebbe il pin dove il sensore ritorna il valore mentre
#il TRIG sarebbe il pin dove riceve il segnale dalla raspberry

SENSOR_ECHO = pinout.SENSOR_ECHO
SENSOR_TRIG = pinout.SENSOR_TRIG

MIN_DIST = 0.50

OBSTACLE = 1
NOTOBSTACLE = 0

EVENT_DISTANCE = 0

class SensorController:

	def __init__(self):


		self._sensorctrl_thread = None
		self._sensorctrl_stop = None

		self._listeners = []

	def _fireEvent (self, evt, param):
		for lst in self._listeners:
			lst(evt, param)

	def addEventListener (self, lst):
		self._listeners.append(lst)

	def removeEventListener(self, lst):
		self._listeners.remove(lst)

	def initialize(self):
		proxsensor.initialize(SENSOR_ECHO, SENSOR_TRIG)

	def startSensorCtrl(self):
		if (self._sensorctrl_thread == None):
			self._sensorctrl_thread = threading.Thread(target=self._sensorCtrl)
			self._sensorctrl_thread.start()


	def stopSensorCtrl(self):
		if (self._sensorctrl_thread != None):
			self._sensorctrl_stop = True
			self._sensorctrl_thread.join()
			self._sensorctrl_thread = None

	def _sensorCtrl(self):

		while (not self._sensorctrl_stop):

			if proxsensor.readingDone():
				self._fireEvent(EVENT_DISTANCE, proxsensor.getDistance())
				proxsensor.startReading()

			time.sleep(WAIT_TIME)

#TEST
if __name__ == "__main__":


	sensorCtrl = SensorController()

	def prova (evt, param):
		print "Distance:",param,"m"

	sensorCtrl.addEventListener(prova)

	sensorCtrl.initialize()
	sensorCtrl.startSensorCtrl()

	time.sleep(10)

	sensorCtrl.stopSensorCtrl()
