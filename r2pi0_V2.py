import server
import time
import motor_control
import motion_adapters
import RPi.GPIO as GPIO
import RTTLPlayer as player
import threading

def srv_lst (evt, param):
	if evt == server.EVENT_CLIENT_CONNECTED:
		player.play("RTTL/Eureka.txt")

def lst (evt, param):
	if evt == motor_control.EVENT_WATCHDOG_TERMINATED_WITH_NO_ACTIONS:
		player.play("RTTL/Sad.txt")

def end ():
	player.stop()
	mainsrv.stop()
	GPIO.cleanup()
	ctrl.stopWatchdog()

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

def exit (cmd, srv):
	srv.send("ok")

	player.play("RTTL/Beeping2.txt")

	time.sleep(2)

	t = threading.Thread(target=end)
	t.start()

	print "Exited"



GPIO.setmode(GPIO.BCM)

player.initialize()
player.play("RTTL/Beeping1.txt")



ctrl = motion_adapters.DistanceAdapter(motor_control.MovementController(), 0.2)
ctrl.setDistance(0.1)
ctrl.initialize()
ctrl.startWatchdog()
ctrl.addEventListener(lst)






cmd = {"s": s, "r": r, "sound": sound, "exit": exit}

mainsrv = server.Server(cmd)
mainsrv.start()
mainsrv.addListener(srv_lst)

raw_input("Press Enter to exit...")

end()
