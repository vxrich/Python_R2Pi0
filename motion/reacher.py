# -*- coding: utf-8 -*-
#
#	Autori: Tosatto Davide, Riccardo Grespan
#
#	Modulo di controllo per il raggiungimento di un oggetto
#

import threading
import time

TIME_BETWEEN_TWO_COMMANDS = 0.09

class Reacher:

	def __init__ (self, ctrl):
		self._ctrl = ctrl
		self._thread = threading.Thread(target=self._cycle)
		self._sem = threading.BoundedSemaphore()
		self._sem.acquire()
		self._stop = False
		self._thread.start()
		self._started = False;

	def _cycle (self):
		while not self._stop:

			self._sem.acquire()
			if not self._stop:
				self._ctrl.move(70)
			self._sem.release()

			time.sleep(TIME_BETWEEN_TWO_COMMANDS)

	def reach (self):
		if not self._started:
			print "REACH STARTED"
			self._sem.release()
			self._started = True

	def obstacle (self):
		# Ostacolo vicino rilevato: raggiungimento effettuato
		# va richiamata dall'esterno
		if self._started:
			self._sem.acquire()
			self._started = False

	def stop (self):
		self._stop = True
		self.reach()
		self._thread.join()
