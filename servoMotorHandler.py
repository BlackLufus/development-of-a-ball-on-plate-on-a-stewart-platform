from PCA9685 import PCA9685

class ServoMotorHandler:
    def __init__(self) -> None:
        self.pwm = PCA9685()
        self.pwm.setPWMFreq(50)

    # Standard deviation for each angle so that the r-axis is horizontal
    # servo: angle deviation
    deviation = {
        0: 8,  # Rechts
        1: 5,  # Links
        2: 6,  # Rechts
        3: 8,  # Links
        4: 7, # Rechts
        5: 2   # Links
    }

    # Set the rotation angle for the Steward Plattform (between: -45 and 45)
    def setRotationAngle(self, servo, angle):
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
            print("Angle out of range")