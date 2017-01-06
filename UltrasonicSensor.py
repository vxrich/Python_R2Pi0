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

TIME_OUT = 50
SIGNAL_DELAY = 0.00001
SOUND_CONST = 1715.0
WAIT_TIME = 0.05

#TODO: La classe nel complesso sembra ok, ma chiaramente non è stata testata perchè
#      così certamente non parte, ci sono errori di sintassi
class Sensor:

	def __init__(self, pin_in, pin_out):
		self._pin_in = pin_in
		self._pin_out = pin_out
		self._distance = None
		self._pulse_start = None
		self._pulse_end = None
		self._pulse_duration = None

	#TODO: manca self
	def initialize():
		GPIO.setup(self._pin_in, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
		GPIO.setup(self._pin_out, GPIO.OUT)
		GPIO.output(self._pin_out, False)

	def _xchangeSignal(self):
		GPIO.output(self._pin_out, True)
		time.sleep(SIGNAL_DELAY)
		GPIO.output(self._pin_out, False)

		while GPIO.input(ECHO)==0:
			_pulse_start = time.time()

		while GPIO.input(ECHO)==1:
			_pulse_end = time.time()

		self._pulse_duration = self._pulse_end - self._pulse_start

		self._distance = self._pulse_duration*SOUND_CONST
		self._distance = round(self._distance,2)

	#TODO: il nome getter è troppo generico, sarebbe meglio una cosa tipo getDistance
	#TODO: manca self
	def _getter():
		print "Distance:",self._distance,"m"
		return self._distance

	#TODO: manca self
	def startCheck():
		self._xchangeSignal()

#        while 1:
#            self._xchangeSignal()
#            self._getter()
#            time.sleep(WAIT_TIME)

#L'ECHO sarebbe il pin dove il sensore ritorna il valore mentre
#il TRIG sarebbe il pin dove riceve il segnale dalla raspberry

#TODO: Ok, ma nel file pinout non ci sono, come hai fatto a testarla?

SENSOR_ECHO = pinout.SENSOR_ECHO
SENSOR_TRIG = pinout.SENSOR_TRIG

MIN_DIST = 0.50

OBSTACLE = 1
NOTOBSTACLE = 0

class SensorController:

	#TODO: manca self
	def __init__():
		self._SENSOR = Sensor(SENSOR_TRIG, SENSOR_ECHO)

		self._sensorctrl_thread = None

		self._listeners = []

	def _fireEvent (self, evt, param):
		for lst in self._listeners:
			lst(evt, param)

	def addEventListener (self, lst):
		self._listeners.append(lst)

	def removeEventListener(self, lst):
		self._listeners.remove(lst)

	def initialize(self):
		self._SENSOR.initialize()

	def startSensorCtrl(self):
		if (self._sensorctrl_thread == None):
			self._sensorctrl_thread = threading.Thread(target=self._sensorCtrl())
			self._sensorctrl_thread.start()

	def _sensorCtrl(self):
		#Bisogna aggiungere qualche riga per fare in modo che
		#non continui a dire che e' troppo vicino ma lasci il tempo
		#di muoversi

		#TODO: Più che altro bisogna aggiungere la possibilità di fermare il thread

		while 1:
			self._SENSOR.startCheck();
			if self._SENSOR.getter() <= 0.50:
				print "POSSIBLE COLLISION"
				self._fireEvent(OBSTACLE, None) #TODO: Qua NON va bene, bisogna inviare la distanza IN METRI aI listener
												#questo serve più che altro per la funzione follow in cui avere la distanza in
												#metri potrebbe essere utile, inoltre qua abbiamo fissato di default la distanza
												#dell'ostacolo a 0.5 metri, brutta idea. Basta mandare la distanza in metri,
												#si occupa di definire la distanza dell'ostacolo direttamente la classe che ho
												#scritto apposta
			time.sleep(WAIT_TIME)
