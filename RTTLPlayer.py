# -*- coding: utf-8 -*-
#
#	Autori: Tosatto Davide, Riccardo Grespan
#
#	Modulo che si occupa di riprodurre suoni in formato RTTL precedentemente
#	analizzati da RTTLConverter
#

import pinout
import RPi.GPIO as GPIO
import time
import Queue
import threading
import RTTLConverter as conv

_songQ = Queue.Queue()
_player_thread = None
_stop = False
_shut_up = False

def initialize ():

	GPIO.setup(pinout.BUZZER, GPIO.OUT)

	global _player_thread

	_player_thread = threading.Thread(target=playerCycle)
	_player_thread.start()

	print _player_thread

#Aggiunge una canzone alla coda
def play (songPath):

	sng = conv.getter(songPath)
	_songQ.put(sng)
	print "Added song %s" % songPath

def stop ():

	global _stop

	_stop = True

	print _player_thread

	_player_thread.join()

#Riproduzione di un singolo suono con i parametri relativi alla nota
def _buzz(frequenza, durata, durataCompl):
	"""
		Riproduce una singola nota.
		Input:
			- frequenza: frequenza della nota
			- durata: durata del suono
			- durataCompl: durate della pausa successiva al suono
	"""
	if not _shut_up:
		global _buzzer

		freq = (int(frequenza))

		if freq==0:
			freq = 1

		_fake_pwm(50, frequenza, durata)
		time.sleep(durataCompl)
		#print "BUZZ %d %f" % (freq, durata)

def _fake_pwm(dc, freq, duration):
	"""
		Esegue un pwm 'virtuale'.

		NOTA: Necessario perchè, a quanto pare, i pwm forniti da GPIO (comunque virtuali)
		danno dei problemi quando si tratta di cambiare più volte la frequenza.
		In particolare, dopo 300 cambi di frequenza smettono di funzionare.
		Questo bug è segnalato agli sviluppatori della libreria, che ne confermano
		la presenza, ma non hanno ancora risolto: https://sourceforge.net/p/raspberry-gpio-python/tickets/94/

		Probabilmente si può fare qualcosa bypassando la libreria GPIO ed usando il pwm
		hardware presente sulla scheda, ma si rende necessario passare dal C

		Input:
			- dc: duty cycle
			- freq: frequenza
			- duration: durata del suono
	"""

	period = 1.0/freq
	period_H = period * dc/100.0
	period_L = period - period_H

	if period > duration:
		time.sleep(duration)
		return

	tm = 0

	# print "Fake pwm dc: %f, f: %f, durata: %f, period: %f" % (dc, freq, duration, period)

	while tm < duration:
		GPIO.output(pinout.BUZZER, GPIO.HIGH)
		time.sleep(period_H)
		GPIO.output(pinout.BUZZER, GPIO.LOW)
		time.sleep(period_L)
		tm += period


#Riproduce una singola canzone
def _play (song):

	#print "Playing a song"

	for i in range(len(song)):
		_buzz((song[i])[0],(song[i])[1],0.02)
		#print "Playing a note %d" % i


def playerCycle ():
	while not _stop:
		try:
			#Blocca per al massimo 500 mS
			#Se la lasciassi bloccante all'infinito questo thread non potrebbe
			#essere stoppato
			song = _songQ.get(True, 0.5)
			_play(song)

		except Queue.Empty:
			pass

	print "Stopped"

def silence ():
	global _shut_up

	_shut_up = True

def unsilence ():
	global _shut_up

	_shut_up = False

def silenced ():
	return _shut_up

def toggleSilence ():
	if silenced():
		unsilence()
	else:
		silence()

if __name__ == "__main__":

	GPIO.setmode(GPIO.BCM)



	initialize()

	print  "Starting song"

	sng = conv.getter("RTTL/Sad.txt")


	for i in range(20):
		print "PLAYING %d" % i
		play("RTTL/Sad.txt")

	raw_input("Press Enter...")

	stop()

	GPIO.cleanup()
