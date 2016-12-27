import server
import time
import motor_control
import RPi.GPIO as GPIO
import RTTLPlayer as player


def lst (evt, param):
	if evt == motor_control.EVENT_WATCHDOG_TERMINATED_WITH_NO_ACTIONS:
		player.play("RTTL/Sad.txt")

def end ():
	player.stop()
	mainsrv.stop()
	GPIO.cleanup()
	ctrl.stopWatchdog()
	

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
	
	t = threading.Thread(target=end)
	t.start()
	
	print "Exited"
	
	
		
GPIO.setmode(GPIO.BCM)

player.initialize()
player.play("RTTL/Beeping1.txt")



ctrl = motor_control.MovementController()
ctrl.initialize()
ctrl.startWatchdog()
ctrl.addEventListener(lst)





cmd = {"s": s, "r": r, "exit": exit}

mainsrv = server.Server(cmd)
mainsrv.start()

raw_input("Press Enter to exit...")

end()