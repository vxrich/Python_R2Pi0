#########################################################
#														#
#		Author: Riccardo Grespan						#
#				Davide Tosatto							#
#														#
#  		R2-Pi0, python remote controlled motorized 		#
#			robot with sound and light					#
#														#
#########################################################



from random import randint
import RPi.GPIO as GPIO
import time 
import thread
import pprint
from rtttl import parse_rtttl
from RTTLConverter import getter

buzzerPin = 12
dcBuzzer = 50
f = 50

#Inizializzazione GPIO e pin di motori e buzzer
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(buzzerPin, GPIO.OUT)
buzzer = GPIO.PWM(12, 50)

 #Riproduzione di un singolo suono con i parametri relativi alla nota
def buzz(frequenza, durata, inter):
	period = 1.0 / frequenza       				
	delay = period / 2
	buzzer.ChangeFrequency(frequenza)
	buzzer.start(50)
	time.sleep(durata)
	buzzer.stop()
	time.sleep(inter)

#Riproduzione di canzoni casuali
def playSong():
	canzone = getter('/media/serverhdd/Script/Python/R2-D2/RTTL/Imperial.txt')
	
	for i in range(len(canzone)):
		#buzz((canzone[i])[0],(canzone[i])[1],(canzone[i])[2])
		buzz((canzone[i])[0],(canzone[i])[1],0.1)
		
playSong()

	
	
	
