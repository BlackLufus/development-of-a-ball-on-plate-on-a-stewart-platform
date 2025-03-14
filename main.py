#!/usr/bin/python
import time
#import RPi.GPIO as GPIO
from PCA9685 import PCA9685

import numpy as np
from StewartPlattform import StewartPlattform

# Standard deviation for each angle so that the r-axis is horizontal
# servo: angle deviation
deviation = {
    0: 0,  # Rechts
    1: 10,  # Links
    2: -30,  # Rechts
    3: 0,  # Links
    4: 10, # Rechts
    5: -50   # Links
}

# Set the rotation angle for the Steward Plattform (between: -45 and 45)
def setRotationAngle(servo, angle):
    if angle >= 0 and angle <= 135 and servo in deviation:
        minAngle = 921
        maxAngle = 1780
        temp = 1780 - 921
        temp /= 90
        temp *= angle
        if servo % 2 == 0:
            pwm.setServoPulse(servo, minAngle + temp + deviation[servo])
        else:
            pwm.setServoPulse(servo, maxAngle - temp - deviation[servo])
    else:
        print("Angle out of range")

def servoTest():
    while True:
        print("Move Up!")

        for angle in range(0, 90, 1):
            if angle == 0:
                print("zero point")
            for channel in range(6):
                setRotationAngle(channel, angle)
            time.sleep(0.1)

        print("Move Down!")
        
        for angle in range(90, 0, -1):
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
    stewart = StewartPlattform(100, [340, 20, 100, 140, 240, 280], 80, [350, 10, 110, 130, 250, 270])
    leg_length_list = stewart.calculate(0, 0, 88, 25, 0, 0)
    if leg_length_list != None:
        for index, leg_length in enumerate(leg_length_list):
            print("length of leg ", index, ": ", leg_length)

    angle_list = stewart.getAngles(40, 100, leg_length_list)
    for index, angle in enumerate(angle_list):
        print("angle of servo ", index, ": ", angle)
        setRotationAngle(index, angle)

if __name__ == '__main__':
    # try:
    #print "This is an PCA9685 routine"
    pwm = PCA9685()
    pwm.setPWMFreq(50)

    angleServoTest()

    # differentAngleServoTest({
    #     0: 24,
    #     1: 83,
    #     2: 9,
    #     3: 84,
    #     4: 5,
    #     5: 90
    # })

    # time.sleep(1)

    # quickServoTest(80)

    # time.sleep(1)

    # quickServoTest(55)

    # time.sleep(1)

    # quickServoTest(10)

    # time.sleep(1)

    # servoTest()
