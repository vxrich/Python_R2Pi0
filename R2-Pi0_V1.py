#########################################################
#														#
#		Author: Riccardo Grespan						#
#				Davide Tosatto							#
#														#
#  		R2-Pi0, pyhton remote controlled motorized 		#
#			robot with sound and light					#
#														#
#########################################################



from random import randint
import RPi.GPIO as GPIO 					
import time 
#import lirc
import thread
import os
from RTTLConverter import getter
from RTTLConverter import loadData
import socket
import sys

#Riproduzione di un singolo suono con i parametri relativi alla nota
def buzz(frequenza, durata, durataCompl):
	buzzer.ChangeFrequency(frequenza)
	buzzer.start(50)
	time.sleep(durata)
	buzzer.stop()
	time.sleep(durataCompl)
	
#Riproduzione di canzoni casuali
def playSong():
	canzone = getter(canzoni[randint(0,  len(canzoni))])
	for i in range(len(canzone)):
		buzz((canzone[i])[0],(canzone[i])[1],0.2)

def blink(led):
	for i in range(len(led)):
		led.start(led[i])
		time.sleep(led[i][0])
		led.stop()
		time.sleep(led[i][1]/2)

def proiettore():
	print "I'm projecting, Master"
	GPIO.output(proiettorePin, TRUE)
	time.sleep(5)
	GPIO.output(proiettorePin, FALSE)

def eye():
	blink(blinkList[randint(0, 3)])

def avanti():
	print "Moving forward"
	motoreDX.start(dutycycle)
	motoreSX.start(dutycycle)
	
def stop():
	print "Stop"
	motoreDX.stop()
	motoreSx.stop()
	
def ruotaDx():
	print "I'm turning right"
	motoreSx.start(dutycycle)

def ruotaSx():
	print "I'm turning left"
	motoreDX.start(dutycycle)
	
def routine():
	print "Look at me now"
	avanti()
	time.sleep(2)
	ruotaDx()
	ruotaSx()
	stop()
	playSong()
	
def spegni():
	print "Goodbye Master"
	os.system("shutdown now -h")
	
def interazione():
	try:
#		comandi.get(lirc.nextcode())()
		
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.bind((TCP_IP, TCP_PORT))
		s.listen(1)
 
		print 'Connection address:', addr
		while 1:
			conn, addr = s.accept()
			data = conn.recv(BUFFER_SIZE)
			if not data: break
			comandi.get(data)()
			print "received data:", data
			conn.send(data)  # echo
			conn.close()
			
	except:
		buzz(errore, 1, 0.2)
	while 1:
		pass

TCP_IP = '0.0.0.0'
TCP_PORT = 5005
BUFFER_SIZE = 20  # Normally 1024, but we want fast response

# Create a LIRC socket
#sockid = lirc.init("myprogram")	    					

proiettorePin = 3
ledPin = 5;
buzzerPin = 18
motoreDxPin = 10
motoreSxPin = 11
dcMotore = 50
dcBuzzer = 50
f = 50

#Inizializzazione GPIO e pin di motori e buzzer
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD) 
GPIO.setup(ledPin, GPIO.OUT)
GPIO.setup(buzzerPin, GPIO.OUT)
GPIO.setup(motoreDxPin, GPIO.OUT)
GPIO.setup(motoreSxPin, GPIO.OUT)
led = GPIO.PWM(ledPin, f)						
buzzer = GPIO.PWM(buzzerPin, f)
motoreDX = GPIO.PWM(motoreDxPin, f)
motoreSX = GPIO.PWM(motoreSxPin, f)

discoveryServer = "java -jar DiscoveryServer.jar"

errore = 1
blinkList = [[], [], []]  #Lista di liste dei tempi del LED
comandi = {'a':avanti, 's':stop,'dx':ruotaDx,'sx':ruotaSx,'sound':playSong, 'spegni': spegni, 'routine': routine, 'proiettore': proiettore}
canzoni = {    'Eureka':loadData('RTTL/Eureka.txt'),
			   'Processing':loadData('RTTL/Processing.txt'),
			   'Beeping 1':loadData('RTTL/Beeping1.txt'),
			   'Beeping 2':loadData('RTTL/Beeping2.txt'),
			   'StarWars':loadData('RTTL/StarWars.txt'),
			   'Sad':loadData('RTTL/Sad.txt')
			   }
	
os.system(discoveryServer)	
	
try:
	
   thread.start_new_thread( interazione, () )				
   thread.start_new_thread( playSong, () )
   thread.start_new_thread( eye, () )		
except:
   print "Error: unable to start thread"
   file_log("Errore fatale nell'esecuzione del programma!")

while 1:
   pass
	
	
	
	
