#!/usr/bin/python
import time
#import RPi.GPIO as GPIO

import numpy as np
from stewartPlatform import StewartPlatform
from servoMotorHandler import ServoMotorHandler
from nunchuk import Nunchuk
import math

def servoTest():
    while True:
        print("Move Up!")

        for angle in range(0, 90, 1):
            if angle == 0:
                print("zero point")
            for channel in range(6):
                ServoMotorHandler.setRotationAngle(channel, angle)
            time.sleep(0.1)

        print("Move Down!")
        
        for angle in range(90, 0, -1):
            if angle == 0:
                print("zero point")
            for channel in range(6):
                smh.setRotationAngle(channel, angle)
            time.sleep(0.1)

def quickServoTest(angle):
    for channel in range(6):
        smh.setRotationAngle(channel, angle)

def differentAngleServoTest(angleDict):
    for channel in range(6):
        smh.setRotationAngle(channel, angleDict[channel])

def setAngle(x: float, y: float, z: float, alpha: float, beta: float, gamma: float):
    stewart = StewartPlatform(100, [340, 20, 100, 140, 240, 280], 100, [350, 10, 110, 130, 250, 270])
    leg_length_list = stewart.calculate(x, y, z, alpha, beta, gamma)
    # if leg_length_list != None:
        # for index, leg_length in enumerate(leg_length_list):
        #     print("length of leg ", index, ": ", leg_length)

    angle_list = stewart.getAngles(40, 100, leg_length_list)
    for index, angle in enumerate(angle_list):
        # print("angle of servo ", index, ": ", angle)
        smh.setRotationAngle(index, angle)

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

def smoothCircleTest(radius=15, steps=100, period=0.01):
    setAngle(0, 0, 94, 0, 0, 0)
    time.sleep(2)

    angles = np.linspace(0, 2 * math.pi, steps)

    print(angles)

    while True:
        for theta in angles:
            x_offset = radius * math.cos(theta)
            # x_offset = 0
            # x_offset = np.random.uniform(-10, 10)
            y_offset = radius * math.sin(theta)
            # y_offset = 0
            # y_offset = np.random.uniform(-10, 10)
            setAngle(0, 0, 94, x_offset, y_offset, 0)
            time.sleep(period)

def nunchukTest(radius=17, period=0.001):
    nc = Nunchuk()

    setAngle(0, 0, 94, 0, 0, 0)
    time.sleep(1)

    while True:
        nc.measure()

        # print(nc.joy_x)
        # print(nc.joy_y)

        x_offset = radius / 128 * (nc.joy_x - 128)
        y_offset = radius / 128 * (nc.joy_y - 128) * (-1)

        # print(x_offset)
        # print(y_offset)

        try:
            setAngle(0, 0, 94, x_offset, y_offset, 0)
        except:
            pass

        time.sleep(period)

if __name__ == '__main__':
    smh = ServoMotorHandler()

    # The platform will transform to a fix position
    # setAngle(0, 0, 100, 0, 0, 0)

    # Nnunchuck test
    nunchukTest()

    # Smooth circly test
    # smoothCircleTest(radius=15, steps=300, period=0.001)

    # Makes the platform dance
    # longAngleServoTest()

    # Reset the platform to zero
    # quickServoTest(0)

    # Manipulate each angle seperatly
    # differentAngleServoTest({
    #     0: 24,
    #     1: 83,
    #     2: -20,
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