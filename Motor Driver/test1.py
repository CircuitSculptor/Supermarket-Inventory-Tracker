from smbus2 import SMBus

# I2C device address
DEVICE_ADDRESS = 0x0f

# Create an instance of the I2C bus
bus = SMBus(1)

# Write a byte to the device
bus.write_byte(DEVICE_ADDRESS, 0x01)

# Read a byte from the device
data = bus.read_byte(DEVICE_ADDRESS)
print(f"Data read: {data}")

# Close the bus
bus.close()