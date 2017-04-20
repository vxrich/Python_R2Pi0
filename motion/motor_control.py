# -*- coding: utf-8 -*-
#
#	Autori: Tosatto Davide, Riccardo Grespan
#
#	Modulo di controllo motori.
#	Lo scopo e' quello di poter muovere il robottino semplicemente dando
#	una velocita' e una rotazione.
#



import RPi.GPIO as GPIO
import time
import threading
import pinout
import RTTLPlayer as player
from motion_events import EVENT_WATCHDOG_TERMINATED_WITH_NO_ACTIONS

#Modalita' di spegnimento motore:
# MODE_SC: Short Circuit: pone i pin del motore in corto circuito
# MODE_FL: Floating: lascia il motore floatante: si ferma dopo
MODE_SC = 0
MODE_FL = 1

HIGH = 1
LOW = 0

DEFAULT_DUTY = 50

#La frequenza del pwm è mantenuta bassa in modo da avere l'impulso per
#partire già a duty cycle basso (altrimenti avrei impulsini troppo piccoli)
DEFAULT_FREQ = 30

def limit (value, min, max):
	if value < min:
		return min
	elif value > max:
		return max
	return value

class Motor:
	"""
		Classe che rappresenta il singolo motore.

		L'astrazione prevede di poter passare al motore semplicemente una velocità
		compresa tra -100 e 100
	"""

	_STOPPED = 0
	_FORWARD = 1
	_BACKWARD = 2


	def __init__ (self, forward_pin, backward_pin):
		self._forward_pin = forward_pin
		self._backward_pin = backward_pin
		self._state = self._STOPPED
		self._speed = 0
		self._pwm_forward = None
		self._pwm_backward = None

	def initialize (self, pwm_freq=DEFAULT_FREQ):

		print "%d %d" % (self._forward_pin, self._backward_pin)

		GPIO.setup(self._forward_pin, GPIO.OUT)
		GPIO.setup(self._backward_pin, GPIO.OUT)
		
		self._pwm_forward = GPIO.PWM(self._forward_pin, pwm_freq)
		self._pwm_backward = GPIO.PWM(self._backward_pin, pwm_freq)
		self._pwm_backward.start(0)
		self._pwm_forward.start(0)
		self.move(0)

	def _setHighImpedance ():

		GPIO.setup(self._forward_pin, GPIO.IN)
		GPIO.setup(self._backward_pin, GPIO.IN)

	def _setLowImpedance ():

		GPIO.setup(self._forward_pin, GPIO.OUT)
		GPIO.setup(self._backward_pin, GPIO.OUT)

	def _stopPwm (self, pwm):
		pwm.stop()
		time.sleep(0.01)

	def _setPwm (self, pwm, duty, state):
		if self._state!=state:
			#self.stop()
			#time.sleep(0.5)
			self.stop(MODE_FL)
			pwm.stop()
			pwm.start(duty)
		else:
			pwm.ChangeDutyCycle(duty)



	def forward (self, duty=DEFAULT_DUTY):
		#NOTA: Il motore è "spento" quando entrambi i PWM sono a 1
		#perciò lascio sempre a 1 il PWM forward, così avrò avanzamento quando l'altro va a 0

#		print "Forward %d" % duty
		self._pwm_forward.ChangeDutyCycle(100)

		self._pwm_backward.ChangeDutyCycle(100 - duty)

		self._state = self._FORWARD

	def backward (self, duty=DEFAULT_DUTY):
		#NOTA: vedi forward

#		print "Backward %d" % duty
		self._pwm_backward.ChangeDutyCycle(100)

		self._pwm_forward.ChangeDutyCycle(100 - duty)

		self._state = self._BACKWARD

	def move (self, speed):
		"""
			Imposta la velocità del motore.

			Input:
			 - speed: velocità compresa tra -100 e 100. Velocità positive
			   corrispondono ad avanzare, negative ad indietreggiare
		"""
		#print "Move %d" % speed


		if speed > 0:
			speed = limit(speed, 0, 100)
			self.forward(speed)
		elif speed < 0:
			speed = limit(-speed, 0, 100)
			self.backward(speed)
		else:
			self.stop(MODE_SC)

		self._speed = speed

	def move_delta (self, speed_delta):
		"""
			Applica un delta alla velocità

			Input:
			 - speed_delta: delta da applicare
		"""
		new_speed = self.getSpeed() + speed_delta
		self.move(new_speed)

	def stop (self, mode=MODE_SC):
		"""
			Ferma il motore (effetto simile a dare move(0))

			Input:
			 - mode: 	MODE_SC: il motore viene messo con i due terminali in corto: azione frenante
			 			MODE_FL: il motore viene lasciato floatante: non si genererà una corrispondente
								 di opposizione al moto e perciò il robot non si fermerà istantaneamente
		"""
#		print "Stopped"



		if mode==MODE_SC:
			self._pwm_forward.ChangeDutyCycle(100)
			self._pwm_backward.ChangeDutyCycle(100)

		else:
			self._pwm_forward.ChangeDutyCycle(0)
			self._pwm_backward.ChangeDutyCycle(0)

		#time.sleep(3/DEFAULT_FREQ)


		self._state = self._STOPPED

	def getState (self):
		return self._state

	def getSpeed (self):
		return self._speed

SX_FW = pinout.MOTOR_SX_FW
SX_BW = pinout.MOTOR_SX_BW

DX_FW = pinout.MOTOR_DX_FW
DX_BW = pinout.MOTOR_DX_BW

class MovementController:
	"""
		Classe che astrae la coppia di motori che fanno muovere il robot.

		L'astrazione prevede di decidere il movimento con una coppia velocità-rotazione

		La classe è dotata di watchdog: se non riceve comandi per più di self._watchdog_time
		stoppa il robot per sicurezza. Serve nel caso si esca fuori range bluetooth o se per
		ogni caso l'applicazione si blocca
	"""

	def __init__ (self, correction=0):
		self._MOTOR_DX = Motor(DX_FW, DX_BW)
		self._MOTOR_SX = Motor(SX_FW, SX_BW)
		self._correction = correction

		self._speed = 0
		self._rotation = 0

		#correzione in % sulla velocità (per farlo andare dritto)
		self._correction = correction

		#Dati del watchdog
		self._watchdog_thread = None
		self._watchdog_time = 0.2
		self._watchdog_value = False
		self._watchdog_stop = False

		self._listeners = []

	def _fireEvent (self, evt, param):
		for lst in self._listeners:
			lst(evt, param)

	def addEventListener (self, lst):
		self._listeners.append(lst)

	def removeEventListener(self, lst):
		self._listeners.remove(lst)

	def initialize(self):
		self._MOTOR_DX.initialize()
		self._MOTOR_SX.initialize()
		self.stop()

	def startWatchdog(self):
		if (self._watchdog_thread == None):
			self._watchdog_thread = threading.Thread(target=self._wdCycle)
			self._watchdog_thread.start()

	def stopWatchdog(self):

		if (self._watchdog_thread != None):
			self._watchdog_stop = True
			self._watchdog_thread.join()
			self._watchdog_thread = None

	def _wdCycle (self):
		while (not self._watchdog_stop):
			time.sleep(self._watchdog_time)
			if (not self._watchdog_value) and (self._rotation != 0 or self._speed != 0):
				print "WATCHDOG ENDED WITH NO ACTIONS. Stopping the robot for safety."
				self.stop()
				self._fireEvent(EVENT_WATCHDOG_TERMINATED_WITH_NO_ACTIONS, None)
			self._watchdog_value = False

	def stop (self):

		self._watchdog_value = True
		self._MOTOR_DX.move(0)
		self._MOTOR_SX.move(0)
		self._speed = 0
		self._rotation = 0

	def applyMovement (self, speed, rotation):
		"""
			Applica un movimento al robottino.

			Usa come velocita' base speed e somma/sottrae rotation da
			una parte e dall'altra in base alla direzione di rotazione

			Input:
				speed: velocita' di movimento (>0 -> avanti | <0 -> indietro)
				rotation: velocita' di rotazione (>0 -> orario | <0 -> antiorario)
		"""

		self._watchdog_value = True

		rotation += (self._correction*speed)/100

		dx_speed = speed
		sx_speed = speed

		#Orario
		if rotation > 0:

			rotation_abs = limit(rotation, 0, 100)

			#Meno spinta a dx
			dx_speed = speed - rotation_abs
			#Piu' spinta a sx
			sx_speed = speed + rotation_abs

		#Antiorario
		elif rotation < 0:

			rotation_abs = limit(-rotation, 0, 100)

			#Piu' spinta a dx
			dx_speed = speed + rotation_abs
			#Meno spinta a sx
			sx_speed = speed - rotation_abs

		#print "applyMovement SX:%d DX:%d" % (sx_speed, dx_speed)

		self._MOTOR_DX.move(dx_speed)
		self._MOTOR_SX.move(sx_speed)

		self._speed = speed
		self._rotation = rotation

	def rotate (self, rotation):

		self.applyMovement (self._speed, rotation)

	def move (self, speed):

		self.applyMovement (speed, self._rotation)

	def getSpeed (self):
		return self._speed

	def getRotation (self):
		return self._rotation


if __name__ == "__main__":
	#TEST
	import blue
	import bluetooth



	#Test Motor
	GPIO.setmode(GPIO.BCM)

	motor = Motor(23,24)
	motor.initialize()

	ctrl = MovementController()
	ctrl.initialize()

	#GPIO.setup(23, GPIO.OUT)
	#GPIO.output(23, 1)

	#time.sleep(100)

	#ctrl.rotate(10)

	# client_sock,address = blue.acceptConnection()
	# print "Accepted connection from ",address

	# data = ""

	# while data!="exit":
		# data = client_sock.recv(1024)
		# data = data.strip('\n')
		# print "received [%s]" % data

		# if(data.startswith("s ")):
			# speed = data.split(" ")[1]
			# ctrl.move(int(speed))

		# client_sock.send("ok")

	# client_sock.close()

	# for i in reversed(range(-100, 0, 5)):
			# ctrl.move(i)
			# time.sleep(0.1)

	# for i in range(10):

		# for i in range(-100, 0, 5):
			# ctrl.move(i)
			# time.sleep(0.1)


		# for i in range(0, 100, 5):
			# ctrl.move(i)
			# time.sleep(0.1)

		# for i in reversed(range(-100, 100, 5)):
			# ctrl.move(i)
			# time.sleep(0.1)

	ctrl.move(70)
	time.sleep(3)

	ctrl.stop()
	time.sleep(1)

	ctrl.move(-70)
	time.sleep(3)

	GPIO.cleanup()
