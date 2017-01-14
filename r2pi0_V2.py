import server
import time
import motion.motor_control as motor_control
import motion.motion_adapters as motion_adapters
import motion.motion_events as me
import motion.motion_factory as mf
import RPi.GPIO as GPIO
import RTTLPlayer as player
import threading
import mood

OBSTACLE_THRESHOLD = 0.2

ctrl = None
distCtrl = None
moodTimeCtrl = None
mainsrv = None

def srv_lst (evt, param):
	if evt == server.EVENT_CLIENT_CONNECTED:
		player.play("RTTL/Eureka.txt")

def lst (evt, param):
	if evt == me.EVENT_WATCHDOG_TERMINATED_WITH_NO_ACTIONS:
		player.play("RTTL/Sad.txt")
	elif evt == me.EVENT_OBSTACLE_DETECTED:
		player.play("RTTL/Sad.txt")

def end ():
	player.stop()
	mainsrv.stop()
	GPIO.cleanup()
	ctrl.stopWatchdog()
	moodTimeCtrl.stop()

i = 0

def sound (cmd, srv):

	global i

	songs = ["imperial2", "Sad", "Eureka", "Processing"]

	player.play("RTTL/%s.txt" % songs[i])

	i = (i+1)%4

def s (cmd, srv):

	try:
		ctrl.move(float(cmd[1]))
		srv.send("ok")
	except ValueError:
		srv.send("ko")
	print "Speed to %s" % cmd[1]

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

def exit (cmd, srv):
	srv.send("ok")

	player.play("RTTL/Beeping2.txt")

	time.sleep(2)

	t = threading.Thread(target=end)
	t.start()

	print "Exited"

def moodCallback (evt, param):
	print "Moods: Sadness:%s Rage:%s Happiness:%s Boredom:%s Fatigue:%s" % (param.getMood(mood.SADNESS_MOOD), param.getMood(mood.RAGE_MOOD), param.getMood(mood.HAPPINESS_MOOD), param.getMood(mood.BOREDOM_MOOD), param.getMood(mood.FATIGUE_MOOD))

	

try:

	GPIO.setmode(GPIO.BCM)

	player.initialize()
	player.play("RTTL/Beeping1.txt")

	moodCtrl = mood.Mood()
	moodCtrl.addListener(moodCallback)
	moodTimeCtrl = mood.TimeMoodManager(moodCtrl, 1);
	moodTimeCtrl.start()

	distCtrl = mf.getObstacleAvoidController(0.2)

	ctrl = motion_adapters.MoodedAdapter(distCtrl, moodCtrl, moodTimeCtrl, fatigue_factor=10)

	ctrl.initialize()
	ctrl.startWatchdog()
	ctrl.addEventListener(lst)



	cmd = {"s": s, "r": r, "sound": sound, "set_mode": set_mode, "exit": exit}

	mainsrv = server.Server(cmd)
	mainsrv.start()
	mainsrv.addListener(srv_lst)

	raw_input("Press Enter to set obstacle...")
	distCtrl.setDistance(0.1)
	raw_input("Press Enter to remove obstacle...")
	distCtrl.setDistance(6)
	raw_input("Press Enter to set obstacle back...")
	distCtrl.setDistance(0.1)
	raw_input("Press Enter to exit...")
except Exception as e:
	print e
finally:
	end()
