import errno
import time,sys
from smbus2 import SMBus
from gpiozero import OutputDevice
from time import sleep
import termios
import tty
import select

bus = SMBus(1)
reset = OutputDevice(17, initial_value=False)

leftMotorSpeed = 200
rightMotorSpeed = 200

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
    print("Stop\n")
    m.MotorSpeedSetAB(0, 0)
    time.sleep(1)


def main():

    fd = sys.stdin.fileno()
    # Save terminal state
    terminal_state = termios.tcgetattr(fd)

    timeout = 0.5
    moving = False

    print("Hold W/A/S/D to drive robot. Press B to brake (stop motors). Q to Exit", flush=True)
    try:
        # Make the terminal not require pressing Enter for each input
        tty.setcbreak(fd)
        while True:
            ready, _, _ = select.select([sys.stdin], [], [], timeout)

            if not ready:
                if moving:
                    stop_motors()
                    moving = False
                continue

            key = sys.stdin.read(1).lower()

            if key == "q":
                break
            if key in "wasdb":
                #print(f"Pressed: {key}", flush=True)
                match key:
                    case "w":
                        move_forward()
                        moving = True
                    case "a":
                        move_left()
                        moving = True
                    case "s":
                        move_backwards()
                        moving = True
                    case "d":
                        move_right()
                        moving = True
                    case "b":
                        stop_motors()
                    case "r":
                        reset_motor_driver()
                    case _:
                        print("Invalid Input. Hold W/A/S/D to drive robot. Press B to brake (stop motors). Q to Exit", flush=True)

    except Exception as e:
        print("Error: {}".format(e))
        sys.exit(1)

    except KeyboardInterrupt:
        print("Keyboard Interrupt")
        stop_motors()
        sys.exit(0)

    # Restore terminal settings on Keyboard Interrput or crash
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, terminal_state)

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