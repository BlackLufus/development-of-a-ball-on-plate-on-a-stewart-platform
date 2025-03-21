# https://forums.raspberrypi.com/viewtopic.php?t=28231
# i2cdetect -y -r 1
import smbus
import time
import math


bus = smbus.SMBus(1)

test = 0b00011000
print(f"{test:02X}")
test << 2
print(f"{test:02X}")

bus.write_byte_data(0x52,0x40,0x00)
time.sleep(0.1)
while True:
  try:
    # Write Byte to get data
    bus.write_byte(0x52,0x00)
    time.sleep(0.1)
    # Read all 6 bytes at once
    data = bus.read_i2c_block_data(0x52, 0x00, 6)
    
    # Dump raw data
    print(f"Raw Data: {data[0]:02X} {data[1]:02X} {data[2]:02X} {data[3]:02X} {data[4]:02X} {data[5]:02X}")

    # Get Joy stick data
    joy_x = data[0]
    joy_y = data[1]

    # get acceloration data
    accel_x = (data[2] << 2) + ((data[5] >> 2) & 0x03)
    accel_y = (data[3] << 2) + ((data[5] >> 4) & 0x03)
    accel_z = (data[4] << 2) + ((data[5] >> 6) & 0x03)

    # Get Button data for c and z
    button_c = not (data[5] & 0x02)
    button_z = not (data[5] & 0x01)

    # Dump Output
    print('Jx: %s Jy: %s Ax: %s Ay: %s Az: %s Bc: %s Bz: %s' % (joy_x, joy_y, accel_x, accel_y, accel_z, button_c, button_z))
  except IOError as e:
    print(e)
