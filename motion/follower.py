# -*- coding: utf-8 -*-
#
#	Autori: Tosatto Davide, Riccardo Grespan
#
#	Modulo che si occupa di eseguire il controllo necessario a mantenere una certa
#	distanza da un oggetto
#
#	Si è deciso di utilizzare un controllore proporzionale in quanto:
#		- non ci interessa che l'errore all'infinito tenda a zero
#		- se anche ci interessasse, il sensore non sarebbe abbastanza preciso
#		- vogliamo mantenere il codice semplice, un integratore lo rendeva più complesso
#

import threading
import time


TIME_BETWEEN_TWO_COMMANDS = 0.09
CONTROL_CONSTANT = 500

class Follower:

	def __init__ (self, ctrl, sensor, refDistance, tolerance):
		self._speed_to_apply = 0
		self._ref_dist = refDistance
		self._tolerance = tolerance
		sensor.addEventListener(self._distanceChanged)
		self._ctrl = ctrl
		self._thread = threading.Thread(target=self._cycle)
		self._sem = threading.BoundedSemaphore()
		self._sem.acquire()
		self._stop = False
		self._thread.start()
		self._started = False;

	def _distanceChanged (self, evt, newDist):
		diff = newDist - self._ref_dist

		#Applico un movimento solo se sono fuori dalla tolleranza, altrimenti sto fermo.
		#Serve per evitare fastidiosi "scattini"
		if (abs(diff) > self._tolerance):
			self._speed_to_apply = CONTROL_CONSTANT *(diff)
			#print "newDist %f, speed %f" % (newDist, self._speed_to_apply)
		else:
			self._speed_to_apply = 0
			#print "In tolerance"

	def _cycle (self):
		while not self._stop:

			#Il semaforo serve per poter bloccare il controllore senza uscire dal
			#thread
			self._sem.acquire()
			if not self._stop:
				self._ctrl.move(self._speed_to_apply)
			self._sem.release()

			time.sleep(TIME_BETWEEN_TWO_COMMANDS)

	def start (self):
		if not self._started:
			print "FOLLOW STARTED"
			self._sem.release()
			self._started = True

	def pause (self):
		if self._started:
			print "FOLLOW PAUSED"
			self._sem.acquire()
			self._started = False 

	def toggle (self):
		if self._started:
			self.pause()
		else:
			self.start()

	def stop (self):
		self._stop = True
		self.start()
		self._thread.join()
		self._started = False

	def started(self):
		return self._started
