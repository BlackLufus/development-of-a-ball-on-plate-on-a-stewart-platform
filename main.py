#!/usr/bin/python
import time
#import RPi.GPIO as GPIO
from PCA9685 import PCA9685

import numpy as np
from StewartPlattform import StewartPlattform

# Standard deviation for each angle so that the r-axis is horizontal
# servo: angle deviation
deviation = {
    0: 7,  # Rechts
    1: 6,  # Links
    2: 4,  # Rechts
    3: 3,  # Links
    4: -7, # Rechts
    5: 0   # Links
}

# Set the rotation angle for the Steward Plattform (between: -45 and 45)
def setRotationAngle(servo, angle):
    if angle >= -90 and angle <= 90 and servo in deviation:
        temp = (angle if servo % 2 == 0 else -angle)
        temp += (deviation[servo] if servo % 2 == 0 else -deviation[servo]) # Add angle deviation
        temp += 90 # Transform to normal angle
        pwm.setRotationAngle(servo, temp)
    else:
        print("Angle out of range")

def servoTest():
    while True:
        print("Move Up!")

        for angle in range(-45, 45, 1):
            if angle == 0:
                print("zero point")
            for channel in range(6):
                setRotationAngle(channel, angle)
            time.sleep(0.1)

        print("Move Down!")
        
        for angle in range(45, -45, -1):
            if angle == 0:
                print("zero point")
            for channel in range(6):
                setRotationAngle(channel, angle)
            time.sleep(0.1)

def quickServoTest(angle):
    for channel in range(6):
        setRotationAngle(channel, angle)

def differentAngleServoTest(angleDict):
    for channel in range(6):
        setRotationAngle(channel, angleDict[channel])

def angleServoTest():
    stewart = StewartPlattform(100, [340, 20, 100, 140, 240, 280], 80, [350, 10, 110, 130, 250, 270], 40, 100)
    leg_length_list = stewart.calculate(0, 0, 110, 25, 0, 0)
    if leg_length_list != None:
        for index, leg_length in enumerate(leg_length_list):
            print("length of leg ", index, ": ", leg_length)

    angle_list = stewart.getAngles(leg_length_list)
    for index, angle in enumerate(angle_list):
        print("angle of servo ", index, ": ", angle)
        setRotationAngle(index, angle)

if __name__ == '__main__':
    # try:
    #print "This is an PCA9685 routine"
    pwm = PCA9685()
    pwm.setPWMFreq(50)

    # Debugging: Ausgabe der base_points und plattform_points einzeln
    # print("Base Points:", swp.base_points)
    # print("Plattform Points:", swp.plattform_points)

    # differentAngleServoTest({
    #     0: 24,
    #     1: -38,
    #     2: 9,
    #     3: 39,
    #     4: -5,
    #     5: -45
    # })

    # time.sleep(1)

    # quickServoTest(20)

    # time.sleep(1)

    # quickServoTest(45)

    # time.sleep(1)

    # quickServoTest(-10)

    # time.sleep(1)

    # servoTest()
