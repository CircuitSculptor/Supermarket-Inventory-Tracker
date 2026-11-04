# First attempt to rewrite Arduino code to Python
# This is the source file from the original GitHub repository for the Grove I2C Motor Driver v1.3
# https://github.com/Seeed-Studio/Grove_I2C_Motor_Driver_v1_3/blob/master/examples/dcmotor_test_withoutLibrary/dcmotor_test_withoutLibrary.ino

from smbus2 import SMBus

# I2C device address
DEVICE_ADDRESS = 0x0f

# Create an instance of the I2C bus
bus = SMBus(1)

def test_motor_driver():
    
    print("Testing Motor Driver...")
    # Direction header
    bus.write_byte(DEVICE_ADDRESS, 0xaa)
    bus.write_byte(DEVICE_ADDRESS, 0x0a)
    bus.write_byte(DEVICE_ADDRESS, 0x01)

    # Frequency setting 20224 Hz
    bus.write_byte(DEVICE_ADDRESS, 0x84)
    bus.write_byte(DEVICE_ADDRESS, 0x00)
    bus.write_byte(DEVICE_ADDRESS, 0x4f)

    # Motor speed setting 200
    bus.write_byte(DEVICE_ADDRESS, 0x82)
    bus.write_byte(DEVICE_ADDRESS, 200)

    delay = 5  # Delay in seconds

    # Close the bus
    bus.close()


if __name__ == "__main__":
    test_motor_driver()