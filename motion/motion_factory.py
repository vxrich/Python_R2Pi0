
import motor_control
import motion_adapters

def getBaseController ():
	return motor_control.MovementController()

def getObstacleAvoidController(obstacle_distance):
	return motion_adapters.DistanceAdapter(getBaseController(), obstacle_distance)
