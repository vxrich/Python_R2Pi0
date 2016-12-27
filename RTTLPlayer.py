import pinout
import RPi.GPIO as GPIO 
import time
import Queue
import threading
import RTTLConverter as conv

_songQ = Queue.Queue()
_player_thread = None
_stop = False

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
	
def stop ():

	global _stop

	_stop = True
	
	print _player_thread
	
	_player_thread.join()
	
#Riproduzione di un singolo suono con i parametri relativi alla nota
def _buzz(frequenza, durata, durataCompl):
	buzzer =  GPIO.PWM(pinout.BUZZER, frequenza)
	buzzer.start(50)
	time.sleep(durata)
	buzzer.stop()
	time.sleep(durataCompl)
	
#Riproduce una singola canzone
def _play (song):
	for i in range(len(song)):
		_buzz((song[i])[0],(song[i])[1],0.02)
	
def playerCycle ():
	while not _stop:
		try:
			#Blocca per al massimo 500 mS
			song = _songQ.get(True, 0.5)
			_play(song)
			
		except Queue.Empty:
			pass
			
	print "Stopped"

if __name__ == "__main__":

	GPIO.setmode(GPIO.BCM)


	
	initialize()
	
	print  "Starting song"
	
	play("RTTL/Eureka.txt")
	
	time.sleep(3)
	
	stop()
	
	GPIO.cleanup()