import logging
from stewart_platform.PCA9685.PCA9685 import PCA9685
from stewart_platform.stewart_platform import StewartPlatform

class ServoMotorHandler:
    def __init__(self, logger=None) -> None:
        self.logger = logger or logging.getLogger("ServoMotorHandler")
        self.pwm = PCA9685()
        self.pwm.setPWMFreq(50)

    # Standard deviation for each angle so that the r-axis is horizontal
    # servo: angle deviation
    deviation = {
        0: 8,  # Rechts
        1: 5,  # Links
        2: 6,  # Rechts
        3: 8,  # Links
        4: 10, # Rechts
        5: 2   # Links
    }

    def set(self, platform: StewartPlatform, x: float, y: float, z: float, alpha: float, beta: float, gamma: float):
            leg_length_list = platform.calculate(x, y, z, alpha, beta, gamma)
            if leg_length_list != None:
                for index, leg_length in enumerate(leg_length_list):
                    self.logger.debug("length of leg ", index, ": ", leg_length)

            angle_list = platform.getAngles(15, 65, leg_length_list)
            for index, angle in enumerate(angle_list):
                self.logger.debug("angle of servo ", index, ": ", angle)
                self.setRotationAngle(index, angle)

    # Set the rotation angle for the Steward Plattform (between: -45 and 45)
    def setRotationAngle(self, servo, angle, logger=None):
        # min = 921
        # max = 1780
        # mean = max - (min / 2)
        # step = mean / 90
        if angle >= -90 and angle <= 90 and servo in self.deviation:
            temp = (angle if servo % 2 == 0 else -angle)
            temp += (self.deviation[servo] if servo % 2 == 0 else -self.deviation[servo]) # Add angle deviation
            temp += 90 # Transform to normal angle
            # print(temp)
            self.pwm.setRotationAngle(servo, temp)
        else:
            self.logger.error("Angle out of range")