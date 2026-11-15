import errno
import time,sys
from smbus2 import SMBus
from gpiozero import OutputDevice
import RPi.GPIO as GPIO
from hcsr04sensor import sensor
import time
from time import sleep
#import termios
#import tty
import select
#import os

bus = SMBus(1)
reset = OutputDevice(17, initial_value=False)

leftMotorSpeed = 100
rightMotorSpeed = 100

trig = 16
echo = 0

def reset_motor_driver():
    reset.on()   
    sleep(0.1)
    reset.off()  
    sleep(1)  

def move_forward():
    m = motor_driver()
    # FORWARD
    print("Forward")
    m.MotorSpeedSetAB(leftMotorSpeed, rightMotorSpeed)
    m.MotorDirectionSet(0b1010)
    #time.sleep(2)

def move_backwards():
    m = motor_driver()
    # BACK
    print("Back")
    m.MotorSpeedSetAB(leftMotorSpeed, rightMotorSpeed)
    m.MotorDirectionSet(0b0101)
    #time.sleep(2)

def move_left():
    m = motor_driver()
    # LEFT
    print("Left")
    m.MotorSpeedSetAB(leftMotorSpeed, rightMotorSpeed)
    m.MotorDirectionSet(0b1001)
    #time.sleep(2)

def move_right():
    m = motor_driver()
    # RIGHT
    print("Right")
    m.MotorSpeedSetAB(leftMotorSpeed, rightMotorSpeed)
    m.MotorDirectionSet(0b0110)
    #time.sleep(2)

def stop_motors():
    m = motor_driver()
    #print("Stop\n") # found that this print was anoying
    m.MotorSpeedSetAB(0, 0)
    time.sleep(1)


def main():

    OBSTACLE_CM = 30
    REVERSE_SECONDS = 0.5
    TURN_SECONDS = 0.5

    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    measurement = sensor.Measurement
    autonomous = False
    state = "forward"
    state_started = 0.0

    print("Enter s to start, q to stop, or press Ctrl+C to exit.")

    try:
        # start code from both motors stopped
        stop_motors()

        while True:
            # Check for input without waiting for it.
            if select.select([sys.stdin], [], [], 0)[0]:
                line = sys.stdin.readline()

                # stop if the terminal input closes.
                if line == "":
                    break

                key = line.strip().lower()

                # keyboard input
                if key == "s":
                    autonomous = True
                elif key == "q":
                    autonomous = False
                    print("Enter s to start, q to stop, or press Ctrl+C to exit.")
                else:
                    print("Invalid input. Enter s or q.")

            now = time.monotonic()

            # check if autonomous mode is off, stop if not
            if not autonomous:
                stop_motors()
                state = "forward"

            elif state == "forward":
                # Take a fresh reading before deciding to drive forward.
                distance = measurement.basic_distance(trig, echo)
                print(f"Distance: {distance} cm")

                if distance is None or distance <= 0:
                    raise ValueError("Invalid distance reading")

                if distance < OBSTACLE_CM:
                    stop_motors()
                    move_backwards()
                    state = "reversing"
                    state_started = time.monotonic()
                else:
                    move_forward()

            elif state == "reversing":
                if now - state_started >= REVERSE_SECONDS:
                    stop_motors()

                    # turn in a random direction to prevent the robot driving in circles
                    random_direction = time.time() % 2 # random function
                    if random_direction < 1:
                        move_left()
                    else:
                        move_right()

                    state = "turning"
                    state_started = time.monotonic()

            elif state == "turning":
                if now - state_started >= TURN_SECONDS:
                    stop_motors()
                    state = "forward"

            time.sleep(0.1)

    except Exception as e:
        print("Error: {}".format(e))
        sys.exit(1)

    except KeyboardInterrupt:
        print("Keyboard Interrupt")
        stop_motors()
        sys.exit(0)

    finally:
        GPIO.cleanup((trig, echo))
        
class motor_driver:

    MotorSpeedSet             = 0x82
    PWMFrequenceSet           = 0x84
    DirectionSet              = 0xaa
    MotorSetA                 = 0xa1
    MotorSetB                 = 0xa5
    Nothing                   = 0x01
    I2CMotorDriverAdd         = 0x0f  # Default (Alternate 0x0a)

    def __init__(self,address=0x0f):
        self.I2CMotorDriverAdd=address

    #Maps speed from 0-100 to 0-255
    def map_vals(self,value, leftMin, leftMax, rightMin, rightMax):
        #http://stackoverflow.com/questions/1969240/mapping-a-range-of-values-to-another
        # Figure out how 'wide' each range is
        leftSpan = leftMax - leftMin
        rightSpan = rightMax - rightMin

        # Convert the left range into a 0-1 range (float)
        valueScaled = float(value - leftMin) / float(leftSpan)

        # Convert the 0-1 range into a value in the right range.
        return int(rightMin + (valueScaled * rightSpan))

    #Set motor speed
    def MotorSpeedSetAB(self,MotorSpeedA,MotorSpeedB):
        MotorSpeedA=self.map_vals(MotorSpeedA,0,100,0,255)
        MotorSpeedB=self.map_vals(MotorSpeedB,0,100,0,255)
        bus.write_i2c_block_data(self.I2CMotorDriverAdd, self.MotorSpeedSet, [MotorSpeedA,MotorSpeedB])
        time.sleep(.02)

    #Set motor direction
    def MotorDirectionSet(self,Direction):
        bus.write_i2c_block_data(self.I2CMotorDriverAdd, self.DirectionSet, [Direction,0])
        time.sleep(.02)

if __name__ == "__main__":

    try:
        reset_motor_driver()
        print("Motor driver reset")
    finally:
        reset.off()
        reset.close()

    while True:
        try:
            main()

        except Exception as e:
            print("Power failure - Error: {}".format(e))
            try:
                time.sleep(5)
                reset = OutputDevice(17, initial_value=False)
                print("Motor driver reset")
                reset_motor_driver()
                reset.off()
                reset.close()

                time.sleep(2)
                main()

            except Exception as e:
                print("Check Power Source - Error: {}".format(e))
                sys.exit(1)

        except KeyboardInterrupt:
            print(" Keyboard Interrupt - Stop Motors")
            stop_motors()
            sys.exit(0)