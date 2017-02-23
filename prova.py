import proxsensor
import time

proxsensor.initialize(20,21)

while (True):

    if proxsensor.readingDone():
        print proxsensor.getDistance()
        proxsensor.startReading()

    time.sleep(0.1)
