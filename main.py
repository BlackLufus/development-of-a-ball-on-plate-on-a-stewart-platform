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

def setAngle(platform: StewartPlatform, x: float, y: float, z: float, alpha: float, beta: float, gamma: float):
    leg_length_list = platform.calculate(x, y, z, alpha, beta, gamma)
    # if leg_length_list != None:
        # for index, leg_length in enumerate(leg_length_list):
        #     print("length of leg ", index, ": ", leg_length)

    angle_list = platform.getAngles(40, 100, leg_length_list)
    for index, angle in enumerate(angle_list):
        # print("angle of servo ", index, ": ", angle)
        smh.setRotationAngle(index, angle)

def longAngleServoTest():
    platform = StewartPlatform(100, [340, 20, 100, 140, 240, 280], 100, [350, 10, 110, 130, 250, 270])
    setAngle(platform, 0, 0, 94, 0, 0, 0)
    time.sleep(2)
    steps = 0.1
    period = 0
    while True:
        # setAngle(0, 0, 94, 15, 0, 0)
        print("Step 1")
        for i in np.arange(-15, 0, steps):
            setAngle(platform, 0, 0, 94, 15, i, 0)
            time.sleep(period)

        # setAngle(0, 0, 94, 15, 15, 0)
        print("Step 2")
        for i in np.arange(0, 15, steps):
            setAngle(platform, 0, 0, 94, 15, i, 0)
            time.sleep(period)

        # setAngle(0, 0, 94, 0, 15, 0)
        print("Step 3")
        for i in np.arange(15, 0, -steps):
            setAngle(platform, 0, 0, 94, i, 15, 0)
            time.sleep(period)

        # setAngle(0, 0, 94, -15, 15, 0)
        print("Step 4")
        for i in np.arange(0, -15, -steps):
            setAngle(platform, 0, 0, 94, i, 15, 0)
            time.sleep(period)

        # setAngle(0, 0, 94, -15, 0, 0)
        print("Step 5")
        for i in np.arange(15, 0, -steps):
            setAngle(platform, 0, 0, 94, -15, i, 0)
            time.sleep(period)

        # setAngle(0, 0, 94, -15, -15, 0)
        print("Step 6")
        for i in np.arange(0, -15, -steps):
            setAngle(platform, 0, 0, 94, -15, i, 0)
            time.sleep(period)

        # setAngle(0, 0, 94, 0, -15, 0)
        print("Step 7")
        for i in np.arange(-15, 0, steps):
            setAngle(platform, 0, 0, 94, i, -15, 0)
            time.sleep(period)

        # setAngle(0, 0, 94, 15, -15, 0)
        print("Step 8")
        for i in np.arange(0, 15, steps):
            setAngle(platform, 0, 0, 94, i, -15, 0)
            time.sleep(period)

def smoothCircleTest(radius=15, steps=100, period=0.01):
    platform = StewartPlatform(100, [340, 20, 100, 140, 240, 280], 100, [350, 10, 110, 130, 250, 270])
    setAngle(platform, 0, 0, 94, 0, 0, 0)
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
            setAngle(platform, 0, 0, 94, x_offset, y_offset, 0)
            time.sleep(period)

def nunchukTest(radius=15, period=0.001):
    platform = StewartPlatform(100, [340, 20, 100, 140, 240, 280], 100, [350, 10, 110, 130, 250, 270])
    nc = Nunchuk()

    while True:
        nc.measure()
        nc.dump()

        # print(nc.joy_x)
        # print(nc.joy_y)

        x_offset = radius / 128 * (nc.joy_x - 128)
        y_offset = -(radius / 128 * (nc.joy_y - 128))

        button_c = nc.button_c
        button_z = nc.button_z

        # print(x_offset)
        # print(y_offset)

        try:
            setAngle(platform, 0, 0, 90 if button_z else 100 if button_c else 94, x_offset, y_offset, 0)
        except:
            pass

        time.sleep(period)

def nunchukAccelerometerTest(radius=90, min_radius=-15, max_radius=15, period=0.01):
    platform = StewartPlatform(100, [340, 20, 100, 140, 240, 280], 100, [350, 10, 110, 130, 250, 270])
    nc = Nunchuk()

    while True:
        nc.measure()
        nc.dump()

        x_offset = radius / 512 * (nc.accel_x_mean - 512)
        if x_offset > max_radius:
            x_offset = max_radius
        elif x_offset < min_radius:
            x_offset = min_radius
        y_offset = -(radius / 512 * (nc.accel_y_mean - 512))
        if y_offset > max_radius:
            y_offset = max_radius
        elif y_offset < min_radius:
            y_offset = min_radius

        try:
            setAngle(platform, 0, 0, 94, x_offset, y_offset, 0)
        except:
            pass
        time.sleep(period)

if __name__ == '__main__':
    platform = StewartPlatform(100, [340, 20, 100, 140, 240, 280], 100, [350, 10, 110, 130, 250, 270])
    smh = ServoMotorHandler()

    # The platform will transform to a fix position
    # setAngle(platform, 0, 0, 100, 0, 0, 0)

    # Nnunchuck test
    nunchukTest()
    # nunchukAccelerometerTest()

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