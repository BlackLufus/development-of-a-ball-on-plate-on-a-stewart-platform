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
    1: 5,  # Links
    2: 3,  # Rechts
    3: 8,  # Links
    4: 7, # Rechts
    5: 2   # Links
}

# Set the rotation angle for the Steward Plattform (between: -45 and 45)
def setRotationAngle(servo, angle):
    # min = 921
    # max = 1780
    # mean = max - (min / 2)
    # step = mean / 90
    if angle >= -90 and angle <= 90 and servo in deviation:
        temp = (angle if servo % 2 == 0 else -angle)
        temp += (deviation[servo] if servo % 2 == 0 else -deviation[servo]) # Add angle deviation
        temp += 90 # Transform to normal angle
        # print(temp)
        pwm.setRotationAngle(servo, temp)
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

def setAngle(x: float, y: float, z: float, alpha: float, beta: float, gamma: float):
    stewart = StewartPlattform(100, [340, 20, 100, 140, 240, 280], 100, [350, 10, 110, 130, 250, 270])
    leg_length_list = stewart.calculate(x, y, z, alpha, beta, gamma)
    # if leg_length_list != None:
        # for index, leg_length in enumerate(leg_length_list):
        #     print("length of leg ", index, ": ", leg_length)

    angle_list = stewart.getAngles(40, 100, leg_length_list)
    for index, angle in enumerate(angle_list):
        # print("angle of servo ", index, ": ", angle)
        setRotationAngle(index, angle)

def angleServoTest():
    setAngle(0, 0, 94, -15, 15, 0)

def longAngleServoTest():
    setAngle(0, 0, 94, 0, 0, 0)
    time.sleep(2)
    steps = 0.1
    period = 0
    while True:
        # setAngle(0, 0, 94, 15, 0, 0)
        print("Step 1")
        for i in np.arange(-15, 0, steps):
            setAngle(0, 0, 94, 15, i, 0)
            time.sleep(period)

        # setAngle(0, 0, 94, 15, 15, 0)
        print("Step 2")
        for i in np.arange(0, 15, steps):
            setAngle(0, 0, 94, 15, i, 0)
            time.sleep(period)

        # setAngle(0, 0, 94, 0, 15, 0)
        print("Step 3")
        for i in np.arange(15, 0, -steps):
            setAngle(0, 0, 94, i, 15, 0)
            time.sleep(period)

        # setAngle(0, 0, 94, -15, 15, 0)
        print("Step 4")
        for i in np.arange(0, -15, -steps):
            setAngle(0, 0, 94, i, 15, 0)
            time.sleep(period)

        # setAngle(0, 0, 94, -15, 0, 0)
        print("Step 5")
        for i in np.arange(15, 0, -steps):
            setAngle(0, 0, 94, -15, i, 0)
            time.sleep(period)

        # setAngle(0, 0, 94, -15, -15, 0)
        print("Step 6")
        for i in np.arange(0, -15, -steps):
            setAngle(0, 0, 94, -15, i, 0)
            time.sleep(period)

        # setAngle(0, 0, 94, 0, -15, 0)
        print("Step 7")
        for i in np.arange(-15, 0, steps):
            setAngle(0, 0, 94, i, -15, 0)
            time.sleep(period)

        # setAngle(0, 0, 94, 15, -15, 0)
        print("Step 8")
        for i in np.arange(0, 15, steps):
            setAngle(0, 0, 94, i, -15, 0)
            time.sleep(period)

if __name__ == '__main__':
    # try:
    #print "This is an PCA9685 routine"
    pwm = PCA9685()
    pwm.setPWMFreq(50)

    # for servo in range(6):
    #     setRotationAngle(servo, 0)

    # Makes the platform dance
    longAngleServoTest()

    # Reset the platform to zero
    # quickServoTest(0)

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