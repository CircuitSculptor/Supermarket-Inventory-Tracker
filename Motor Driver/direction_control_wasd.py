import errno
import time,sys
from smbus2 import SMBus
from gpiozero import OutputDevice
from time import sleep

bus = SMBus(1)
reset = OutputDevice(17, initial_value=False)

def reset_motor_driver():
    reset.on()   
    sleep(0.1)
    reset.off()  
    sleep(1)  

def move_forward():
    m = motor_driver()
    # FORWARD
    print("Forward")
    m.MotorSpeedSetAB(100, 100)
    m.MotorDirectionSet(0b1010)
    #time.sleep(2)

def move_backwards():
    m = motor_driver()
    # BACK
    print("Back")
    m.MotorSpeedSetAB(200, 200)
    m.MotorDirectionSet(0b0101)
    #time.sleep(2)

def move_left():
    m = motor_driver()
    # LEFT
    print("Left")
    m.MotorSpeedSetAB(200, 200)
    m.MotorDirectionSet(0b1001)
    #time.sleep(2)

def move_right():
    m = motor_driver()
    # RIGHT
    print("Right")
    m.MotorSpeedSetAB(200, 200)
    m.MotorDirectionSet(0b0110)
    #time.sleep(2)

def stop_motors():
    m = motor_driver()
    print("Stop")
    m.MotorSpeedSetAB(0, 0)
    time.sleep(1)


def main():
    move_forward()
    time.sleep(3)
    move_backwards()
    time.sleep(3)
    move_left()
    time.sleep(3)
    move_right()
    time.sleep(3)
    stop_motors()

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