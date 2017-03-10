# -*- coding: utf-8 -*-

import server
import time
import motion.motor_control as motor_control
import motion.motion_adapters as motion_adapters
import motion.motion_events as me
import motion.motion_factory as mf
import motion.reacher as reacher
import motion.follower as follower
import RPi.GPIO as GPIO
import RTTLPlayer as player
import threading
import mood
import UltrasonicSensor

OBSTACLE_THRESHOLD = 0.2

#Controllore di movimento
ctrl = None
#Controllore di movimento con distanza
distCtrl = None
#Controllore di modifica delle emozioni nel tempo
moodTimeCtrl = None
#Server di comunicazione con il telefono
mainsrv = None
#Controllore di raggiungimento dell'obiettivo
rch = None
#Controllore di inseguimento dell'obiettivo
flw = None
#Controllore del sensore di prossimità
sensorCtrl = None

#Listener degli eventi provenienti dal rever
def srv_lst (evt, param):
	if evt == server.EVENT_CLIENT_CONNECTED:
		player.play("RTTL/Eureka.txt")

#Listener degli eventi provenienti dal controllore di movimento
def lst (evt, param):
	if evt == me.EVENT_WATCHDOG_TERMINATED_WITH_NO_ACTIONS:
		player.play("RTTL/Sad.txt")
	elif evt == me.EVENT_OBSTACLE_DETECTED:
		player.play("RTTL/Sad.txt")
		rch.obstacle()

#Funzione chiamata al termine delle attività per chiudere tutti i processi in background
def end ():
	sensorCtrl.stopSensorCtrl()
	player.stop()
	mainsrv.stop()
	GPIO.cleanup()
	ctrl.stopWatchdog()
	moodTimeCtrl.stop()
	rch.stop()
	flw.stop()

#Contatore per il suono da riprodurre
i = 0

#Riproduce un suono. EFFETTO COLLATERALE: Modifica la varibile globale i
def sound (cmd, srv):

	global i

	songs = ["imperial2", "Sad", "Eureka", "Processing"]

	player.play("RTTL/%s.txt" % songs[i])

	i = (i+1)%4

#Callback per il comando s del server
def s (cmd, srv):

	try:
		ctrl.move(float(cmd[1]))
		srv.send("ok")
	except ValueError:
		srv.send("ko")
	print "Speed to %s" % cmd[1]

#Callback per il comando r del server
def r (cmd, srv):
	try:
		ctrl.rotate(float(cmd[1]))
		srv.send("ok")
	except ValueError:
		srv.send("ko")
	print "Rotation speed to %s" % cmd[1]

#TODO: testare se funziona
def set_mode (cmd, srv):
	try:
		global ctrl
		mode = cmd[1]
		if mode == "free":
			ctrl = mf.getBaseController()
		elif mode == "avoid_obstacles":
			ctrl = mf.getObstacleAvoidController(OBSTACLE_THRESHOLD)
		srv.send("ok")
	except ValueError:
		srv.send("ko")
	print "Mode setr to %s" % cmd[1]

#Callback per il comando shutup del server
def shutup (cmd, srv):
	player.toggleSilence()

#Callback per il comando reach del server
def reach (cmd, srv):
	rch.reach()
	srv.send("ok");

#Callback per il comando follow del server
def follow (cmd, srv):
	flw.toggle()

#Callback per il comando exit del server
def exit (cmd, srv):
	srv.send("ok")

	player.play("RTTL/Beeping2.txt")

	time.sleep(2)

	t = threading.Thread(target=end)
	t.start()

	sensorCtrl.stopSensorCtrl()

	print "Exited"

#Listener per l'evento che notifica la modifica dei mood
def moodCallback (evt, param):
	#print "Moods: Sadness:%s Rage:%s Happiness:%s Boredom:%s Fatigue:%s" % (param.getMood(mood.SADNESS_MOOD), param.getMood(mood.RAGE_MOOD), param.getMood(mood.HAPPINESS_MOOD), param.getMood(mood.BOREDOM_MOOD), param.getMood(mood.FATIGUE_MOOD))
	pass

#Listener dell'evento che notifica il valore dell'ultima distanza rilevata
def distance (evt, param):
	distCtrl.setDistance(param)
	#print "Distance: ", param


#Corpo del programma principale
try:

	GPIO.setmode(GPIO.BCM)

	player.initialize()
	player.play("RTTL/Beeping1.txt")

	moodCtrl = mood.Mood()
	moodCtrl.addListener(moodCallback)
	moodTimeCtrl = mood.TimeMoodManager(moodCtrl, 1);
	moodTimeCtrl.start()

	distCtrl = mf.getObstacleAvoidController(0.2)

	sensorCtrl = UltrasonicSensor.SensorController()

	sensorCtrl.addEventListener(distance)

	sensorCtrl.initialize()
	sensorCtrl.startSensorCtrl()



	ctrl = motion_adapters.MoodedAdapter(distCtrl, moodCtrl, moodTimeCtrl, fatigue_factor=10, boredom_factor=20)

	ctrl.initialize()
	ctrl.startWatchdog()
	ctrl.addEventListener(lst)

	rch = reacher.Reacher(ctrl)
	flw = follower.Follower(ctrl, sensorCtrl, 0.3, 0.05)



	#Array associativo che collega il nome dei comandi all'azione da eseguire
	cmd = {"s": s, "r": r, "sound": sound, "set_mode": set_mode, "exit": exit, "shutup": shutup, "reach": reach, "follow":follow}

	mainsrv = server.Server(cmd)
	mainsrv.start()
	mainsrv.addListener(srv_lst)

	#raw_input("Press Enter to set obstacle...")
	#distCtrl.setDistance(0.1)
	#raw_input("Press Enter to remove obstacle...")
	#distCtrl.setDistance(6)
	#raw_input("Press Enter to set obstacle back...")
	#distCtrl.setDistance(0.1)
	#raw_input("Press Enter to exit...")

	while(True):
		time.sleep(2)
except Exception as e:
	print e
finally:
	end()
