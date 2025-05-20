import argparse
from asyncio import Event
import logging
import math
import time

import numpy as np

class Set:
    """
    Set the Stewart platform.
    """

    def __init__(self, base_radius: int, base_angle: list, platform_radius: int, platform_angle: list):
        self.base_radius = base_radius
        self.base_angle = base_angle
        self.platform_radius = platform_radius
        self.platform_angle = platform_angle

    def parser(self, parser=None):
        parser = argparse.ArgumentParser(
            parents=[parser] if parser else [],
            prog='Set',
            usage='%(prog)s [options]',
            description='Set the Stewart platform.',
            epilog='Example: %(prog)s --x 0.5 --y 0.5 --z 0.5 --roll 0.1 --pitch 0.2 --yaw 0.3',
        )
        parser.add_argument(
            '-x',
            help='Set the x position of the Stewart platform',
            required=True,
            type=float
        )
        parser.add_argument(
            '-y',
            help='Set the y position of the Stewart platform',
            required=True,
            type=float
        )
        parser.add_argument(
            '-z',
            help='Set the z position of the Stewart platform',
            required=True,
            type=float
        )
        parser.add_argument(
            '-roll',
            help='Set the roll angle of the Stewart platform',
            required=True,
            type=float
        )
        parser.add_argument(
            '-pitch',
            help='Set the pitch angle of the Stewart platform',
            required=True,
            type=float
        )
        parser.add_argument(
            '-yaw',
            help='Set the yaw angle of the Stewart platform',
            required=True,
            type=float
        )

        self.args, _ = parser.parse_known_args()
        self.x = self.args.x
        self.y = self.args.y
        self.z = self.args.z
        self.roll = self.args.roll
        self.pitch = self.args.pitch
        self.yaw = self.args.yaw
    
    def manual(self, x, y, z, roll, pitch, yaw):
        self.x = x
        self.y = y
        self.z = z
        self.roll = roll
        self.pitch = pitch
        self.yaw = yaw

    def run(self, logger):
        from src.stewart_platform.stewart_platform import StewartPlatform
        from src.stewart_platform.servo_motor_handler import ServoMotorHandler

        # Initialize the stewart platform
        platform = StewartPlatform(self.base_radius, self.base_angle, self.platform_radius, self.platform_angle)

        # Initialize the servo motor handler
        smh = ServoMotorHandler(logger)

        # Get or set the logger
        logger = logger or logging.getLogger("StewartPlatform.Set")

        # Set the values for the Stewart platform
        print(self.x)
        print(self.y)
        print(self.z)
        smh.set(
            platform,
            self.x,
            self.y,
            self.z,
            self.roll,
            self.pitch,
            self.yaw
        )

class Circle:
    """
    Circle test for the Stewart platform.
    """

    def __init__(self, base_radius: int, base_angle: list, platform_radius: int, platform_angle: list):
        self.base_radius = base_radius
        self.base_angle = base_angle
        self.platform_radius = platform_radius
        self.platform_angle = platform_angle

    def parser(self, parser=None):
        parser = argparse.ArgumentParser(
            parents=[parser] if parser else [],
            prog='Circle',
            usage='%(prog)s [options]',
            description='Circle test for the Stewart platform.',
            epilog='Example: %(prog)s --x 0.5 --y 0.5 --z 0.5 --roll 0.1 --pitch 0.2 --yaw 0.3',
        )
        parser.add_argument(
            '-r',
            '--radius',
            help='Set the radius of the circle',
            required=False,
            type=float,
            default=5.8
        )
        parser.add_argument(
            '-s',
            '--steps',
            help='Set the steps of the circle',
            required=False,
            type=float,
            default=0.1
        )
        parser.add_argument(
            '-p',
            '--period',
            help='Set the period of the circle',
            required=False,
            type=float,
            default=0
        )
        
        parser.add_argument(
            '--smooth',
            help='Do smooth circle test',
            required=False,
            action='store_true',
            default=False,
        )

        self.args, _ = parser.parse_known_args()
        self.radius = self.args.radius
        self.steps = self.args.steps
        self.period = self.args.period
        self.smooth = self.args.smooth
    
    def manual(self, radius, steps, period, smooth):
        self.radius = radius
        self.steps = steps
        self.period = period
        self.smooth = smooth

    def run(self, logger, stop_event: Event=None):        
        from src.stewart_platform.stewart_platform import StewartPlatform
        from src.stewart_platform.servo_motor_handler import ServoMotorHandler

        # Initialize the Stewart platform
        platform = StewartPlatform(self.base_radius, self.base_angle, self.platform_radius, self.platform_angle)
        
        # Initialize the servo motor handler
        smh = ServoMotorHandler(logger)

        # Get the arguments
        radius = self.radius
        steps = self.steps
        period = self.period
        smooth = self.smooth
        logger = logger or logging.getLogger("StewartPlatform.Circle")

        # Set the initial position of the Stewart platform
        smh.set(platform, 0, 0, 62, 0, 0, 0)

        # Wait for 2 seconds
        time.sleep(2)

        # Set the angles for the circular motion test
        if smooth:

            # Start the circular motion test
            angles = np.linspace(0, 2 * math.pi, int(steps))

            # Set the radius of the circle
            while True:
                for theta in angles:
                    if stop_event and stop_event.is_set():
                        return
                    x_offset = radius * math.cos(theta)
                    # x_offset = 0
                    # x_offset = np.random.uniform(-10, 10)
                    y_offset = radius * math.sin(theta)
                    # y_offset = 0
                    # y_offset = np.random.uniform(-10, 10)
                    smh.set(platform, 0, 0, 62, x_offset, y_offset, 0)
                    time.sleep(period)

        # If smooth is not selected, use the old method
        else:

            # Start the circular motion test
            while True:
                # setAngle(0, 0, 62, 15, 0, 0)
                # print("Step 1")
                for i in np.arange(-radius, 0, steps):
                    if stop_event and stop_event.is_set():
                        return
                    smh.set(platform, 0, 0, 62, radius, i, 0)
                    time.sleep(period)

                # setAngle(0, 0, 62, 15, 15, 0)
                # print("Step 2")
                for i in np.arange(0, radius, steps):
                    if stop_event and stop_event.is_set():
                        return
                    smh.set(platform, 0, 0, 62, radius, i, 0)
                    time.sleep(period)

                # setAngle(0, 0, 62, 0, 15, 0)
                # print("Step 3")
                for i in np.arange(radius, 0, -steps):
                    if stop_event and stop_event.is_set():
                        return
                    smh.set(platform, 0, 0, 62, i, radius, 0)
                    time.sleep(period)

                # setAngle(0, 0, 62, -15, 15, 0)
                # print("Step 4")
                for i in np.arange(0, -radius, -steps):
                    if stop_event and stop_event.is_set():
                        return
                    smh.set(platform, 0, 0, 62, i, radius, 0)
                    time.sleep(period)

                # setAngle(0, 0, 62, -15, 0, 0)
                # print("Step 5")
                for i in np.arange(radius, 0, -steps):
                    if stop_event and stop_event.is_set():
                        return
                    smh.set(platform, 0, 0, 62, -radius, i, 0)
                    time.sleep(period)

                # setAngle(0, 0, 62, -15, -15, 0)
                # print("Step 6")
                for i in np.arange(0, -radius, -steps):
                    if stop_event and stop_event.is_set():
                        return
                    smh.set(platform, 0, 0, 62, -radius, i, 0)
                    time.sleep(period)

                # setAngle(0, 0, 62, 0, -15, 0)
                # print("Step 7")
                for i in np.arange(-radius, 0, steps):
                    if stop_event and stop_event.is_set():
                        return
                    smh.set(platform, 0, 0, 62, i, -radius, 0)
                    time.sleep(period)

                # setAngle(0, 0, 62, 15, -15, 0)
                # logger.debug("Step 8")
                for i in np.arange(0, radius, steps):
                    if stop_event and stop_event.is_set():
                        return
                    smh.set(platform, 0, 0, 62, i, -radius, 0)
                    time.sleep(period)
        