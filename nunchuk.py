import smbus
import time
import math

class Nunchuk:

    _ADDRESS = 0x52
    _MEASUREMENT = 0x00
    _CALIBRATION = 0x20

    def __init__(self) -> None:
        self.bus = smbus.SMBus(1)
        self.bus.write_byte_data(self._ADDRESS,0x40,0x00)

    def write(self, data_type):
        self.bus.write_byte(self._ADDRESS, data_type)
        time.sleep(0.1)

    def read(self, data_type):
        self.write(data_type)
        data = self.bus.read_i2c_block_data(self._ADDRESS, data_type, 6 if data_type == self._MEASUREMENT else 16)
        return data

    def measure(self):
        data = self.read(self._MEASUREMENT)

        self.joy_x = data[0]
        self.joy_y = data[1]

        self.accel_x = (data[2] << 2) + ((data[5] >> 2) & 0x03)
        self.accel_y = (data[3] << 2) + ((data[5] >> 4) & 0x03)
        self.accel_z = (data[4] << 2) + ((data[5] >> 6) & 0x03)
        
        self.button_c = not (data[5] & 0x02)
        self.button_z = not (data[5] & 0x01)
    
    def calibation(self):
        data = self.read(self._CALIBRATION)

        x_axis_0G = (data[0] << 2) + ((data[3] >> 2) & 0x03)
        y_axis_0G = (data[1] << 2) + ((data[3] >> 2) & 0x03)
        z_axis_0G = (data[2] << 2) + ((data[3] >> 2) & 0x03)

        print('x_axis_0G: %s, y_axis_0G: %s, z_axis_0G: %s' % (x_axis_0G, y_axis_0G, z_axis_0G))

        x_axis_1G = (data[4] << 2) + ((data[7] >> 2) & 0x03)
        y_axis_1G = (data[5] << 2) + ((data[7] >> 2) & 0x03)
        z_axis_1G = (data[6] << 2) + ((data[7] >> 2) & 0x03)

        print('x_axis_1G: %s, y_axis_1G: %s, z_axis_1G: %s' % (x_axis_1G, y_axis_1G, z_axis_1G))

        joy_x_axis_max = data[8]
        joy_x_axis_min = data[9]
        joy_x_axis_center = data[10]

        print('joy_x_axis_max: %s, joy_x_axis_min: %s, joy_x_axis_center: %s' % (joy_x_axis_max, joy_x_axis_min, joy_x_axis_center))

        joy_y_axis_max = data[11]
        joy_y_axis_min = data[12]
        joy_y_axis_center = data[13]

        print('joy_y_axis_max: %s, joy_y_axis_min: %s, joy_y_axis_center: %s' % (joy_y_axis_max, joy_y_axis_min, joy_y_axis_center))

        checksum = (data[14] << 8) | data[15]
        
        print('checksum: %s' % (checksum))

if __name__ == '__main__':
    nc = Nunchuk()
    nc.calibation()

    