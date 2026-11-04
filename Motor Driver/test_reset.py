from gpiozero import OutputDevice
from time import sleep

reset = OutputDevice(17, initial_value=False)

def reset_motor_driver():
    reset.on()   
    sleep(0.1)
    reset.off()  
    sleep(1)            

try:
    reset_motor_driver()
    print("Motor driver reset")
finally:
    reset.off()
    reset.close()