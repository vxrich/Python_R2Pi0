# -*- coding: utf-8 -*-
#
#	Autori: Tosatto Davide, Riccardo Grespan
#
#	Funzioni di utilità per costruire controllori di movimento
#

import motor_control
import motion_adapters

def getBaseController ():
	return motor_control.MovementController()

def getObstacleAvoidController(obstacle_distance):
	return motion_adapters.DistanceAdapter(getBaseController(), obstacle_distance)
