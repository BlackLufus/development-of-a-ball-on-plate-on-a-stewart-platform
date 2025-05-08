import argparse
import logging
import math
import time

import numpy as np

# from stewart_platform.nunchuk import Nunchuk
# from stewart_platform.servo_motor_handler import ServoMotorHandler
from stewart_platform.stewart_platform import StewartPlatform
from stewart_platform.reinforcement_learning.ball_on_plate.v0_ball_on_plate_train import run_sb3

class Manager:

    def __init__(self, log_level):
        self.log_level = log_level
        self.platform = StewartPlatform(86, [343, 17, 103, 137, 223, 257], 86, [347, 13, 107, 133, 227, 253])
        # self.smh = ServoMotorHandler()

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
        exit()
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
    
    def ballOnPlateTest(self, virtual=True):
        env_id = 'BallOnPlate-v0'
        dir = "bop/0_8"
        model_name = "best_model.zip"
        run_sb3(env_id, dir, model_name, model="PPO")

            
def main(
        mode: str,
        reinforcement_learning_virtual: bool,
        radius: float,
        steps: int,
        period: float,
        log_level: int
) -> None:
    manager = Manager(log_level)

    if mode == 'nunchuck':
        manager.nunchukTest(radius, period)
    elif mode == 'quick_test':
        manager.quickTest(radius, steps, period)
    elif mode == 'ball_on_plate':
        if not reinforcement_learning_virtual:
            print("Ball-on-plate mode selected (not implemented yet).")
        else:
            manager.ballOnPlateTest()
    else:
        print("No mode selected. Use --help to see available options.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='Stewart Platform Controller',
        description='A program to control a Stewart platform for various test modes and experiments.',
        epilog='For more information, refer to the documentation or contact the developer.'
    )
    parser.add_argument(
        '---help',
        help='Displays all available arguments and their descriptions.',
        action='help'
    )
    parser.add_argument(
        '-m',
        '--mode',
        required=True,
        choices=['nunchuck', 'quick_test', 'ball_on_plate'],
        help='Specifies the mode of operation for the Stewart platform. '
             'Options are: '
             '"nunchuck" to control the platform using a Nunchuk controller, '
             '"quick_test" to perform a quick circular motion test, '
             'or "ball_on_plate" to execute the ball-on-plate experiment.'
    )
    parser.add_argument(
        '-rfm',
        '--reinforcement_learning_mode',
        help='Defines the environment for the ball-on-plate experiment. '
             'Choose "virtual" to run the simulation in a virtual environment, '
             'or "real" to execute it on the physical platform.',
        required=False,
        type=str,
        default='virtual',
        choices=['virtual', 'real']
    )
    parser.add_argument(
        '-r',
        '--radius',
        help='Specifies the radius of the circular motion or offset range for the tests. '
             'This value determines the extent of movement in the x and y directions.',
        required=False,
        type=float,
        default=6.5,
    )
    parser.add_argument(
        '-s',
        '--steps',
        help='Defines the number of steps for the circular motion in the quick test mode. '
             'A higher number results in smoother motion.',
        required=False,
        type=int,
        default=100,
    )
    parser.add_argument(
        '-p',
        '--period',
        help='Specifies the time interval (in seconds) between each step of the motion. '
             'A smaller value results in faster motion.',
        required=False,
        type=float,
        default=0.05,
    )
    parser.add_argument(
        '-l',
        '--log_level',
        help='Specifies the logging level for the application. '
             'Options include DEBUG, INFO, WARNING, ERROR, and CRITICAL.',
        required=False,
        type=int,
        default=10,
        choices=[10, 20, 30, 40, 50],
    )

    args = parser.parse_args()

    main(
        args.mode,
        args.reinforcement_learning_mode,
        args.radius,
        args.steps,
        args.period,
        args.log_level
    )