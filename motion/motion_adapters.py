import motion_events as me
import time
import mood
import threading

INITIAL_DISTANCE = 50.0

class DistanceAdapter:

	def __init__ (self, base_mc, near_threshold):
		self._base_mc = base_mc
		self._near_threshold = near_threshold
		self._distance = INITIAL_DISTANCE
		self._listeners = []
		self._obstacle_found = False

	def _distanceCheck (self, speed):
		if self._distance < self._near_threshold and speed > 0:
			return False
		else:
			return True

	def setDistance (self, new_dist):
		self._distance = new_dist
		if (not self._distanceCheck(self.getSpeed())):

			self.move(0)

		if self._distance < self._near_threshold and self._obstacle_found == False:
				self._fireEvent(me.EVENT_OBSTACLE_DETECTED, self._distance)
				self._obstacle_found = True
		else:
			self._obstacle_found = False

	def _fireEvent (self, evt, param):
		for lst in self._listeners:
			lst(evt, param)

	def addEventListener (self, lst):
		self._listeners.append(lst)
		self._base_mc.addEventListener(lst)

	def removeEventListener(self, lst):
		self._listeners.remove(lst)
		self._base_mc.removeEventListener(lst)

	def initialize(self):
		self._base_mc.initialize()

	def startWatchdog(self):
		self._base_mc.startWatchdog()

	def stopWatchdog(self):
		self._base_mc.stopWatchdog()

	def stop (self):
		self._base_mc.stop()

	def applyMovement (self, speed, rotation):
		if (self._distanceCheck(speed)):
			self._base_mc.applyMovement(speed, rotation)
		else:
			self._base_mc.applyMovement(0, rotation)

	def rotate (self, rotation):
		self._base_mc.rotate(rotation)

	def move (self, speed):
		if (self._distanceCheck(speed)):
			self._base_mc.move(speed)
		else:
			self._base_mc.move(0)

	def getSpeed (self):
		return self._base_mc.getSpeed()

	def getRotation (self):
		return self._base_mc.getRotation()

NO_DEFATIGUE_DISABLE_LIMIT=50
BORED_MOVEMENT_UPPER_LIMIT = 90

class MoodedAdapter:

	def __init__ (self, base_mc, mood_ctrl, mood_time_ctrl, fatigue_speed_reduction=0.5, fatigue_factor=0.5, boredom_factor=5):
		self._base_mc = base_mc
		self._mood_ctrl = mood_ctrl
		self._mood_time_ctrl = mood_time_ctrl
		self._fatigue_speed_reduction = fatigue_speed_reduction
		self._fatigue_factor = fatigue_factor
		self._boredom_factor = boredom_factor
		self._last_movement_time = None
		self._listeners = []
		self._bored_movement = None

		mood_ctrl.addListener(self._mood_changed)

	def _mood_changed (self, evt, param):
		if self._mood_ctrl.getMood(mood.BOREDOM_MOOD) > BORED_MOVEMENT_UPPER_LIMIT:
			if self._bored_movement == None or self._bored_movement.stopped() == True:
				self._bored_movement = BoredMovementController(self._internalApplyMovement, self._mood_ctrl)
				self._bored_movement.start()

	def _fireEvent (self, evt, param):
		for lst in self._listeners:
			lst(evt, param)

	def addEventListener (self, lst):
		self._listeners.append(lst)
		self._base_mc.addEventListener(lst)

	def removeEventListener(self, lst):
		self._listeners.remove(lst)
		self._base_mc.removeEventListener(lst)

	def initialize(self):
		self._base_mc.initialize()

	def startWatchdog(self):
		self._base_mc.startWatchdog()

	def stopWatchdog(self):
		self._base_mc.stopWatchdog()

	def stop (self):
		self._base_mc.stop()

	def getDiffFromLastTime (self, last):
		if last == None:
			return 0.0
		return time.time() - last

	def limitAbs (self, value, limit):
		if value > limit:
			return limit
		elif value < -limit:
			return -limit
		else:
			return value

	def applyMovement (self, speed, rotation):
		if self._bored_movement != None and self._bored_movement.stopped() == False:
			self._bored_movement.stop()

		print "AAAAAAAAAAAAAAAAAAAAAAAA"

		self._internalApplyMovement(speed, rotation)

	def _internalApplyMovement (self, speed, rotation):
		timeDiff = self.getDiffFromLastTime(self._last_movement_time)

		deltaFatigue = ((abs(self.getSpeed())+abs(self.getRotation()))/200.0)*timeDiff*self._fatigue_factor
		deltaBoredom = ((abs(self.getSpeed())+abs(self.getRotation()))/200.0)*timeDiff*self._boredom_factor

		print "Diff:%f DeltaBor:%f Factor:%f" % (timeDiff, deltaBoredom, self._boredom_factor)

		self._mood_ctrl.applyDelta(mood.FATIGUE_MOOD, deltaFatigue)
		self._mood_ctrl.applyDelta(mood.BOREDOM_MOOD, -deltaBoredom)

		limit = 100 - self._mood_ctrl.getMood(mood.FATIGUE_MOOD) * self._fatigue_speed_reduction

		speed = self.limitAbs(speed, limit)
		rotation = self.limitAbs(rotation, limit)

		self._base_mc.applyMovement(speed, rotation)

		self._last_movement_time = time.time()

		self._mood_time_ctrl.disable(mood.BOREDOM_MOOD, 5)
		if abs(self.getSpeed()) > NO_DEFATIGUE_DISABLE_LIMIT:
			self._mood_time_ctrl.disable(mood.FATIGUE_MOOD, 5)

	def rotate (self, rotation):
		self.applyMovement(self._base_mc.getSpeed(), rotation)

	def move (self, speed):
		self.applyMovement(speed, self._base_mc.getRotation())

	def getSpeed (self):
		return self._base_mc.getSpeed()

	def getRotation (self):
		return self._base_mc.getRotation()

TURN_TIME_SEC = 5
TURN_COMMAND_TIMEOUT = 0.1
TURN_RANGE = TURN_TIME_SEC/TURN_COMMAND_TIMEOUT
TURN_SPEED = 50

TURN_BOREDOM_LOWER_LIMIT = 10

class BoredMovementController:

	def __init__ (self, applyMovementFunc, moodCtrl):
		self._moodCtrl = moodCtrl
		self._applyMovement = applyMovementFunc
		self._lock = threading.RLock()
		self._mc = moodCtrl
		self._stop = False
		self._thread = threading.Thread(target=self._cycle)

	def _cycle (self):

		sign = 1

		while not self._stop:

			for i in range(int(TURN_RANGE)):
				self._applyMovement(0, sign*TURN_SPEED)
				time.sleep(TURN_COMMAND_TIMEOUT)

				if self._stop:
					return

			if self._mc.getMood(mood.BOREDOM_MOOD)<TURN_BOREDOM_LOWER_LIMIT and sign == -1:
				self._stop = True
				self._applyMovement(0,0)

			if sign == 1:
				sign = -1
			else:
				sign = 1



	def start (self):
		self._thread.start()

	def stop (self):
		self._stop = True
		self._thread.join()

	def stopped (self):
		return self._stop
