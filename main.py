import argparse
import atexit
from datetime import datetime
import logging
import math
import os
import time

import numpy as np

# from stewart_platform.nunchuk import Nunchuk
# from stewart_platform.servo_motor_handler import ServoMotorHandler
from stewart_platform.stewart_platform import StewartPlatform
from stewart_platform.reinforcement_learning.ball_on_plate.v0_ball_on_plate_train import run_sb3

class Manager:

    def __init__(self, log_level, log_dir_path='./log'):
        """
        Initializes the main class for the Stewart Platform program.

        Parameters:
            log_level (int): The logging level to be used for the logger.
            log_dir_path (str, optional): The directory path where log files will be stored. Defaults to './log'.

        Attributes:
            log_level (int): Stores the logging level for the application.
            log_dir_path (str): Path to the directory for storing log files.
            platform (StewartPlatform): Instance of the StewartPlatform class initialized with specific parameters.
            
        Methods:
            setup_logger: Configures the logger for the application.
            __cleanup__: Cleans up resources when the program exits.

        Notes:
            - The logger is set up during initialization, and initial log messages are recorded.
            - The `atexit.register` function ensures cleanup is performed when the program exits.
        """
        self.log_level = log_level
        self.log_dir_path = log_dir_path
        self.platform = StewartPlatform(86, [343, 17, 103, 137, 223, 257], 86, [347, 13, 107, 133, 227, 253])
        # self.smh = ServoMotorHandler()
        self.setup_logger()
        self.logger.info("========================================")
        self.logger.info("Start programm StewartPlatform.")
        self.logger.info("     -----     ")
        atexit.register(self.__cleanup__)

    def __cleanup__(self):
        """
        Perform cleanup operations for the StewartPlatform program.

        This method logs the termination of the program and outputs a separator
        line for clarity in the logs.

        Logs:
            - "Terminate programm StewartPlatform."
            - "========================================"
        """
        self.logger.info("Terminate programm StewartPlatform.")
        self.logger.info("========================================")


    def setup_logger(self):
        """
        Sets up the logger for the application.
        This method configures a logger for the "StewartPlatform" application. It sets the log level, 
        prevents duplicate handlers, and adds handlers for logging to both a file and the console. 
        The log messages are formatted with timestamps, logger names, and log levels.
        Attributes:
            self.log_level (int): The logging level (e.g., logging.DEBUG, logging.INFO).
            self.log_dir_path (str): The directory path where log files will be stored.
            self.logger (logging.Logger): The logger instance for the application.
        Behavior:
            - If `self.logger` is not already set, it initializes a new logger.
            - Creates a log file with a timestamped filename in the specified directory.
            - Adds a file handler and a console stream handler to the logger.
            - Formats log messages with a consistent structure.
        Raises:
            OSError: If the log directory does not exist or cannot be accessed.
        Returns:
            None
        """
        # Set log level
        __log_level = self.log_level

        # Setup logger
        logger = logging.getLogger("StewartPlatform") # Get logger by name
        logger.setLevel(__log_level) # Set log level

        # Prevent to add multiple handlers
        if not self.logger:

            # Logging formatter
            formatter = logging.Formatter(
                '[%(asctime)s] %(name)s %(levelname)s: %(message)s', 
                datefmt='%H:%M:%S'
            )

            # Logging to file
            log_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.log" # Generate file name
            log_filepath = os.path.join(self.log_dir_path, log_filename) # Get file path
            fileHandler = logging.FileHandler(log_filepath) # Create an file handler
            fileHandler.setLevel(__log_level) # Set log level
            fileHandler.setFormatter(formatter) # Set formatter
            logger.addHandler(fileHandler) # Add file handler to logger

            # Logging for console
            streamHandler = logging.StreamHandler() # Create an stream handler
            streamHandler.setLevel(__log_level) # Set log level
            streamHandler.setFormatter(formatter) # set formatter
            logger.addHandler(streamHandler) # Add stream handler to logger

        # Set logger
        self.logger = logger

    def setAngle(self, x: float, y: float, z: float, alpha: float, beta: float, gamma: float):
        """
        Calculates the leg lengths and servo angles for a robotic platform based on the given position and orientation parameters, and sets the servo angles accordingly.

        Parameters:
            x (float): The x-coordinate of the platform's position.
            y (float): The y-coordinate of the platform's position.
            z (float): The z-coordinate of the platform's position.
            alpha (float): The rotation angle around the x-axis (in degrees or radians, depending on implementation).
            beta (float): The rotation angle around the y-axis (in degrees or radians, depending on implementation).
            gamma (float): The rotation angle around the z-axis (in degrees or radians, depending on implementation).

        Description:
            - Uses the `calculate` method of the `platform` object to compute the lengths of the legs required to achieve the specified position and orientation.
            - Logs the calculated leg lengths for debugging purposes.
            - Uses the `getAngles` method of the `platform` object to compute the servo angles based on the leg lengths and predefined constraints (e.g., 15 to 65 degrees).
            - Logs the calculated servo angles for debugging purposes.
            - Sets the rotation angle of each servo motor using the `setRotationAngle` method of the `smh` object.
        """
        leg_length_list = self.platform.calculate(x, y, z, alpha, beta, gamma)
        if leg_length_list != None:
            for index, leg_length in enumerate(leg_length_list):
                self.logger.debug(f"Length of leg {index}: {leg_length}")

        angle_list = self.platform.getAngles(15, 65, leg_length_list)
        for index, angle in enumerate(angle_list):
            self.logger.debug(f"Angle of servo {index}: {angle}")
            self.smh.setRotationAngle(index, angle)
    
    def quickTest(self, radius=6.5, steps=100, period=0.01):
        """
        Perform a quick test by moving in a circular trajectory.
        This method moves the system in a circular trajectory based on the specified
        radius, number of steps, and time period between each step. The movement is
        achieved by calculating offsets in the x and y directions using trigonometric
        functions and applying these offsets iteratively.
        Parameters:
            radius (float, optional): The radius of the circular trajectory. Defaults to 6.5.
            steps (int, optional): The number of discrete steps to divide the circle into. Defaults to 100.
            period (float, optional): The time interval (in seconds) between each step. Defaults to 0.01.
        Returns:
            None
        """
        self.logger.info("Quick test startet")
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
        """
        Perform a test using the Nunchuk controller to control angles based on joystick input.
        This method initializes a Nunchuk object, continuously reads its joystick and button inputs,
        calculates offsets based on the joystick position, and attempts to set angles accordingly.
        The test runs indefinitely unless interrupted.
        Parameters:
            radius (float, optional): The maximum radius for joystick offset calculations. Defaults to 7.5.
            period (float, optional): The delay between each measurement in seconds. Defaults to 0.001.
        Behavior:
            - Reads joystick x and y positions and calculates offsets.
            - Reads button states (C and Z buttons).
            - Attempts to set angles using the calculated offsets.
            - Sleeps for the specified period between iterations.
        """
        self.logger.info("Nunchuk test startet")
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
    
    def nunchukAccelerometerTest(self, platform, radius=90, min_radius=-15, max_radius=15, period=0.01):
        """
        Perform a test of the Nunchuk accelerometer and adjust angles based on measured values.
        This method continuously reads accelerometer data from a Nunchuk device, calculates
        offsets based on the readings, and adjusts angles accordingly. The adjustments are
        constrained within specified minimum and maximum radius values. The method logs the
        start of the test and runs in an infinite loop until interrupted.
        Parameters:
            platform: The platform on which the test is being executed (not used in the method).
            radius (int, optional): The base radius used for calculating offsets. Default is 90.
            min_radius (int, optional): The minimum allowable offset value. Default is -15.
            max_radius (int, optional): The maximum allowable offset value. Default is 15.
            period (float, optional): The time interval (in seconds) between successive measurements. Default is 0.01.
        Raises:
            Exception: If an error occurs while setting the angle, it is caught and ignored.
        """
        self.logger.info("Nuncuck accelerometer test started!")
        exit()
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
                self.setAngle(0, 0, 62, x_offset, y_offset, 0)
            except:
                pass
            time.sleep(period)
    
    def ballOnPlateTest(self, virtual=True):
        """
        Executes the "Ball on Plate" test using a specified environment and model.

        This method initializes and runs the "Ball on Plate" test, which can be 
        executed in either a virtual or physical environment. It uses the 
        Stable-Baselines3 (SB3) library to load and run a pre-trained model 
        for the specified environment.

        Args:
            virtual (bool, optional): Determines whether the test is run in a 
                virtual environment. Defaults to True.

        Logs:
            Logs the start of the test and its mode (virtual or physical).

        Notes:
            - The environment ID is hardcoded as 'BallOnPlate-v0'.
            - The model directory and file name are predefined as "bop/0_8" 
              and "best_model.zip", respectively.
            - The model type is set to "PPO" (Proximal Policy Optimization).
        """
        self.logger.info(f"Ball on plate test startet (virtual={virtual})")
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
    """
    Main function to execute different operational modes for the system.
    Parameters:
        mode (str): The operational mode to execute. Options include:
            - 'nunchuck': Runs the nunchuk test.
            - 'quick_test': Runs a quick test with specified parameters.
            - 'ball_on_plate': Runs the ball-on-plate test (virtual or physical).
        reinforcement_learning_virtual (bool): Specifies whether to use virtual 
            reinforcement learning for the 'ball_on_plate' mode.
        radius (float): The radius parameter used in certain modes.
        steps (int): The number of steps for the 'quick_test' mode.
        period (float): The time period parameter used in certain modes.
        log_level (int): The logging level for the manager.
    Returns:
        None: This function does not return a value.
    Notes:
        - If 'ball_on_plate' mode is selected and `reinforcement_learning_virtual` 
            is False, the functionality is not yet implemented.
        - If an invalid mode is provided, a message will prompt the user to use 
            the help option for available modes.
    """
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
    # Add a help command to display all available arguments
    parser.add_argument(
        '---help',
        help='Displays all available arguments and their descriptions.',
        action='help'
    )
    # Add a mode argument to specify the operational mode
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
    # Add an argument to enable reinforcement learning in a virtual environment
    parser.add_argument(
        '-rlm',
        '--reinforcement_learning_mode',
        help='Defines the environment for the ball-on-plate experiment. '
             'Use this flag to run the simulation in a virtual environment. '
             'Omit it to execute on the physical platform.',
        required=False,
        action='store_true',
        default=False,
    )
    # Add an argument to specify the radius for motion or offset range
    parser.add_argument(
        '-r',
        '--radius',
        help='Specifies the radius of the circular motion or offset range for the tests. '
             'This value determines the extent of movement in the x and y directions.',
        required=False,
        type=float,
        default=6.5,
    )
    # Add an argument to define the number of steps for circular motion
    parser.add_argument(
        '-s',
        '--steps',
        help='Defines the number of steps for the circular motion in the quick test mode. '
             'A higher number results in smoother motion.',
        required=False,
        type=int,
        default=100,
    )
    # Add an argument to specify the time interval between motion steps
    parser.add_argument(
        '-p',
        '--period',
        help='Specifies the time interval (in seconds) between each step of the motion. '
             'A smaller value results in faster motion.',
        required=False,
        type=float,
        default=0.05,
    )
    # Add an argument to set the logging level for the application
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

    # Parse the command-line arguments
    args = parser.parse_args()

    # Call the main function with parsed arguments
    main(
        args.mode,
        args.reinforcement_learning_mode,
        args.radius,
        args.steps,
        args.period,
        args.log_level
    )