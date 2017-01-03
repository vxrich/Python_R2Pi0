#todo: Evento obstacle detected

class DistanceAdapter:

	def __init__ (self, base_mc, near_threshold):
		self._base_mc = base_mc
		self._near_threshold = near_threshold
		self._distance = 50.0
		self._listeners = []

	def _distanceCheck (self, speed):
		if self._distance < self._near_threshold and speed > 0:
			return False
		else:
			return True

	def setDistance (self, new_dist):
		self._distance = new_dist
		if (not self._distanceCheck(self.getSpeed())):
			self.move(0)

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
		return self._base_mc._speed

	def getRotation (self):
		return self._base_mc._rotation
