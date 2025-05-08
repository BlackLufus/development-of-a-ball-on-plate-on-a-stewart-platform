import argparse
import logging
import math
import time

import numpy as np

from stewart_platform.nunchuk import Nunchuk
from stewart_platform.servo_motor_handler import ServoMotorHandler
from stewart_platform.stewart_platform import StewartPlatform

class Manager:

    def __init__(self, log_level):
        self.log_level = log_level
        self.platform = StewartPlatform(86, [343, 17, 103, 137, 223, 257], 86, [347, 13, 107, 133, 227, 253])
        self.smh = ServoMotorHandler()

    def setup_logger(self):
        __log_level = self.log_level

        logger = logging.getLogger("StewartPlatform")
        logger.setLevel(__log_level)

        streamHandler = logging.StreamHandler()
        streamHandler.setLevel(__log_level)

        formatter = logging.Formatter('[%(asctime)s] %(name)s %(levelname)s: %(message)s', datefmt='%H:%M:%S')
        streamHandler.setFormatter(formatter)

        logger.addHandler(streamHandler)
        self.logger = logger

    def setAngle(self, x: float, y: float, z: float, alpha: float, beta: float, gamma: float):
        leg_length_list = self.platform.calculate(x, y, z, alpha, beta, gamma)
        if leg_length_list != None:
            for index, leg_length in enumerate(leg_length_list):
                self.logger.debug(f"Length of leg {index}: {leg_length}")

        angle_list = self.platform.getAngles(15, 65, leg_length_list)
        for index, angle in enumerate(angle_list):
            self.logger.debug(f"Angle of servo {index}: {angle}")
            self.smh.setRotationAngle(index, angle)
    
    def quickTest(self, radius=6.5, steps=100, period=0.01):
        self.setAngle(0, 0, 62, 0, 0, 0)
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
                self.setAngle(0, 0, 62, x_offset, y_offset, 0)
                time.sleep(period)
            
    def nunchukTest(self, radius=7.5, period=0.001):
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
                self.setAngle(0, 0, 62, x_offset, y_offset, 0)
            except:
                pass

            time.sleep(period)
            
def main(
        nunchuck: bool,
        quick_test: bool,
        ball_on_plate: bool,
        reinforcement_learning_mode: str,
        radius: float,
        steps: int,
        period: float,
) -> None:
    manager = Manager()

    if nunchuck:
        manager.nunchukTest(radius, period)
    elif quick_test:
        manager.quickTest(radius, steps, period)
    elif ball_on_plate:
        print("Ball-on-plate mode selected (not implemented yet).")
    else:
        print("No mode selected. Use --help to see available options.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='Stewart Platform',
        description='It is a programm to control a stewart platform',
        epilog='Test'
    )
    parser.add_argument(
        '-h',
        '--help',
        help='Shows all available arguments',
        required=False
    )
    parser.add_argument(
        '-m'
        '--mode',
        required=True,
        choices=['nunchuck', 'quick_test', 'ball_on_plate']
    )
    parser.add_argument(
        '-rfm',
        '--reinforcement_learning_mode',
        help='Execute the ball on plate example in virtual or real environment',
        required=False,
        type=str,
        default='virtual',
        choices=['virtual', 'real']
    )
    parser.add_argument(
        '-r',
        '--radius',
        help='Radius',
        required=False,
        type=float,
        default=6.5,
    ),
    parser.add_argument(
        '-s',
        '--steps',
        help='Steps',
        required=False,
        type=int,
        default=100,
    ),
    parser.add_argument(
        '-p',
        '--period',
        help='Period',
        required=False,
        type=float,
        default=0.05,
    ),

    args = parser.parse_args()

    main(
        args.nunchuck,
        args.quick_test,
        args.ball_on_plate,
        args.reinforcement_learning_mode,
        args.radius,
        args.steps,
        args.period
    )