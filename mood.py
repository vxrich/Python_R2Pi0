# -*- coding: utf-8 -*-
#
#	Autori: Tosatto Davide, Riccardo Grespan
#
#	Modulo per la gestione dell'umore del robot
#	NOTA: Benchè questo modulo contenga 5 emozioni, per ora solo 2 sono
#	realmente usate: noia e fatica
#
#	Le altre saranno forse utilizzate in sviluppi futuri
#
import time
import threading

MIN_LEVEL=0
MAX_LEVEL=100

SADNESS_MOOD = 0
RAGE_MOOD = 1
HAPPINESS_MOOD = 2
BOREDOM_MOOD = 3
FATIGUE_MOOD = 4

EVENT_MOOD_CHANGED = 0

class Mood:
	"""
		Classe che si occupa di gestire le 5 emozioni del robot.
	"""

	def __init__ (self, sadness=0, rage=0, happiness=0, boredom=0, fatigue=0):
		self._mood = {}
		self._mood[SADNESS_MOOD] = sadness
		self._mood[RAGE_MOOD] = rage
		self._mood[HAPPINESS_MOOD] = happiness
		self._mood[BOREDOM_MOOD] = boredom
		self._mood[FATIGUE_MOOD] = fatigue
		self._listeners = []

	def getMood (self, mood):
		return self._mood[mood]

	def setMood (self, mood, value):
		if (value > MAX_LEVEL):
			value = MAX_LEVEL

		if (value < MIN_LEVEL):
			value = MIN_LEVEL

		self._mood[mood] = value

		self._fireEvent(EVENT_MOOD_CHANGED, self)

	def applyDelta (self, mood, delta):
		self.setMood(mood, self.getMood(mood) + delta)

	def addListener (self, lst):
		self._listeners.append(lst)

	def removeListener (self, lst):
		self._listeners.remove(lst)

	def _fireEvent (self, evt, param):
		for lst in self._listeners:
			lst(evt, param)

FATIGUE_FACTOR=5
BOREDOM_FACTOR=0.5

class TimeMoodManager:
	"""
		Classe che si occupa di gestire la variazione delle emozioni con il
		passare del tempo
	"""

	def __init__ (self, mood, checkDelay):
		self._mood = mood
		self._checkDelay = checkDelay
		self._stop = False
		self._checkThread = None

		#Lista che serve per inibire la variazione temporale delle emozioni in modo selettivo
		self._disabled = [(False,0),(False,0),(False,0),(False,0),(False,0)] #lista di coppie disabled, disabled end

	def start (self):
		self._checkThread = threading.Thread(target=self._checkCycle)
		self._checkThread.start()

	def stop (self):
		if self._checkThread != None:
			self._stop = True
			self._checkThread.join()

	def disable (self, mood, period=1):
		self._disabled[mood] = (True, time.time() + period)

	def _reenableCheck (self):
		"""
			Controlla se ci sono emozioni da riabilitare, ossia se si è raggiunto
			il loro tempo di fine disabilitazione
		"""
		for i in range(len(self._disabled)):
			(dis, end) = self._disabled[i]

			if (dis and time.time() > end):
				self._disabled[i] = (False, 0)

	def _checkCycle (self):

		"""
			Ciclo principale che aggiorna le emozioni
		"""

		while not self._stop:

			self._reenableCheck()

			if not self._disabled[FATIGUE_MOOD][0]:
				self._mood.applyDelta(FATIGUE_MOOD, -FATIGUE_FACTOR*self._checkDelay)

			if not self._disabled[BOREDOM_MOOD][0]:
				self._mood.applyDelta(BOREDOM_MOOD, BOREDOM_FACTOR*self._checkDelay)

			time.sleep(self._checkDelay)

if __name__=="__main__":
	import mood

	def moodCallback (evt, param):
		print "Moods: Sadness:%s Rage:%s Happiness:%s Boredom:%s Fatigue:%s" % (param.getMood(mood.SADNESS_MOOD), param.getMood(mood.RAGE_MOOD), param.getMood(mood.HAPPINESS_MOOD), param.getMood(mood.BOREDOM_MOOD), param.getMood(mood.FATIGUE_MOOD))

	moodCtrl = mood.Mood(fatigue = 10)
	moodCtrl.addListener(moodCallback)
	moodTimeCtrl = mood.TimeMoodManager(moodCtrl, 1);
	moodTimeCtrl.start()

	time.sleep(1)

	moodTimeCtrl.disable(1)

	time.sleep(5)

	moodTimeCtrl.stop()
