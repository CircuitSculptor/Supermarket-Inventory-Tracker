import RPi.GPIO as GPIO
from hcsr04sensor import sensor
import time
from time import sleep

trig = 16
echo = 0

while True:
    try:
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        x = sensor.Measurement

        distance = x.basic_distance(trig, echo)
        print("The distance: {} cm's".format(distance))
        time.sleep(0.500)

    except KeyboardInterrupt:
        print("Measurement stopped by User")
    finally:
        GPIO.cleanup((trig, echo))