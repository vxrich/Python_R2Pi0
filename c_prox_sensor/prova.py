import proxsensor

proxsensor.initialize(20,21)

proxsensor.startReading()

while not proxsensor.readingDone():
    pass

print proxsensor.getDistance()
