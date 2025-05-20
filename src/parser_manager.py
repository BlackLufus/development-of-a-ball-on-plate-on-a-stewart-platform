import argparse
import atexit
from datetime import datetime
import logging
import os

class ParserManager:

    # List of available operations
    operations = [
        'set',
        'circle',
        'nunchuck',
        'ball_on_plate',
        'train_ball_on_plate',
        'video_capture_linux',
        'video_capture_windows'
    ]

    def __init__(self, base_radius, base_angle, platform_radius, platform_angle):
        """
        Initializes the ParserManager with the specified parameters.

        Args:
            base_radius (float): The radius of the base of the Stewart platform.
            base_angle (list): A list of angles for the base of the Stewart platform.
            platform_radius (float): The radius of the platform of the Stewart platform.
            platform_angle (list): A list of angles for the platform of the Stewart platform.
        Attributes:
            base_radius (float): The radius of the base of the Stewart platform.
            base_angle (list): A list of angles for the base of the Stewart platform.
            platform_radius (float): The radius of the platform of the Stewart platform.
            platform_angle (list): A list of angles for the platform of the Stewart platform.
        Behavior:
            - Initializes the base radius, base angle, platform radius, and platform angle.
            - Sets up the logger for the application.
        Raises:
            - ValueError: If any of the provided parameters are invalid.
        Returns:
            None
        """
        if not isinstance(base_radius, (int, float)):
            raise ValueError("base_radius must be a number.")
        if not isinstance(base_angle, list) or not all(isinstance(angle, (int, float)) for angle in base_angle):
            raise ValueError("base_angle must be a list of numbers.")
        if not isinstance(platform_radius, (int, float)):
            raise ValueError("plattform_radius must be a number.")
        if not isinstance(platform_angle, list) or not all(isinstance(angle, (int, float)) for angle in platform_angle):
            raise ValueError("plattform_angle must be a list of numbers.")
        if len(base_angle) != 6:
            raise ValueError("base_angle must contain exactly 6 angles.")
        if len(platform_angle) != 6:
            raise ValueError("plattform_angle must contain exactly 6 angles.")
        if base_radius <= 0:
            raise ValueError("base_radius must be a positive number.")
        if platform_radius <= 0:
            raise ValueError("plattform_radius must be a positive number.")
        if len(base_angle) != len(platform_angle):
            raise ValueError("base_angle and plattform_angle must have the same length.")
        if len(base_angle) != 6:
            raise ValueError("base_angle and plattform_angle must have exactly 6 angles.")
        if len(platform_angle) != 6:
            raise ValueError("base_angle and plattform_angle must have exactly 6 angles.")
        if not all(0 <= angle <= 360 for angle in base_angle):
            raise ValueError("All angles in base_angle must be between 0 and 360 degrees.")
        if not all(0 <= angle <= 360 for angle in platform_angle):
            raise ValueError("All angles in plattform_angle must be between 0 and 360 degrees.")
        if not os.path.isdir('./log'):
            os.mkdir('./log')
        self.base_radius = base_radius
        self.base_angle = base_angle
        self.platform_radius = platform_radius
        self.platform_angle = platform_angle

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
    
    def parse(self):
        """
        Parses command-line arguments for the Stewart Platform program.
        This method uses the argparse library to define and handle command-line arguments.
        It sets up the argument parser with options for specifying the operation mode,
        logging level, and logging directory. The parsed arguments are stored in the instance variables.
        Attributes:
            operation (str): The operation mode specified by the user.
            log_level (int): The logging level specified by the user.
            log_dir_path (str): The directory path for storing log files.
        Behavior:
            - Initializes an argument parser with a description of the program.
            - Adds arguments for operation mode, logging level, and logging directory.
            - Parses the command-line arguments and stores them in instance variables.
        Raises:
            argparse.ArgumentError: If the provided arguments do not match the expected format.
        Returns:
            self: Returns the instance of the ParserManager class with parsed arguments.
        """
        parser = argparse.ArgumentParser(
            prog='StewartPlatform',
            description='Stewart Platform control program for various test modes and experiments.',
            epilog='Example: %(prog)s -l 10 -ld ./log --run set',
            add_help=False
        )
        # Add a mode argument to specify the operational mode
        parser.add_argument(
            '--run',
            required=True,
            choices=self.operations,
            help='Specify the operation mode. '
                'Available options: set, circle, nunchuck, ball_on_plate, '
                'train_ball_on_plate, video_capture_linux, video_capture_windows.'
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
        # Add an argument to set the logging dir for the application
        parser.add_argument(
            '-ld',
            '--log_dir',
            help='Specifies the logging dir for the application. ',
            required=False,
            type=str,
            default='./log'
        )

        # Parse the command-line arguments
        args, _ = parser.parse_known_args()

        self.operation = args.run
        self.log_level = args.log_level
        self.log_dir_path = args.log_dir

        return self

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

        # Logging formatter
        formatter = logging.Formatter(
            '[%(asctime)s] %(name)s %(levelname)s: %(message)s', 
            datefmt='%H:%M:%S'
        )

        # Logging to file
        if not os.path.isdir(self.log_dir_path):
            os.mkdir(self.log_dir_path)
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

        self.logger.info("========================================")
        self.logger.info("Start programm StewartPlatform.")
        self.logger.info("-----")
        atexit.register(self.__cleanup__)       

    def run(self):
        """
        Runs the specified operation based on the parsed command-line arguments.
        This method checks the operation specified by the user and imports the corresponding parser module.
        It then creates an instance of the parser, calls its `parser` method to set up the parser,
        and finally calls the `run` method of the parser to execute the operation.
        Attributes:
            self.operation (str): The operation mode specified by the user.
            self.base_radius (float): The radius of the base of the Stewart platform.
            self.base_angle (list): A list of angles for the base of the Stewart platform.
            self.plattform_radius (float): The radius of the platform of the Stewart platform.
            self.plattform_angle (list): A list of angles for the platform of the Stewart platform.
        Behavior:
            - Checks the operation specified by the user.
            - Imports the corresponding parser module based on the operation.
            - Creates an instance of the parser and calls its `parser` method.
            - Calls the `run` method of the parser to execute the operation.
        Raises:
            ImportError: If the specified operation is not recognized or the corresponding module cannot be imported.
        Returns:
            None
        """
        if self.operation == 'set':
                from src.stewart_platform.task import Set
                model = Set(self.base_radius, self.base_angle, self.platform_radius, self.platform_angle)
                model.parser()
                self.setup_logger()
                model.run(self.logger)
        elif self.operation == 'circle':
                from src.stewart_platform.task import Circle
                model = Circle(self.base_radius, self.base_angle, self.platform_radius, self.platform_angle)
                model.parser()
                self.setup_logger()
                model.run(self.logger)
        elif self.operation == 'nunchuck':
                from src.nunchuk.task import Nunchuk
                model = Nunchuk(self.base_radius, self.base_angle, self.platform_radius, self.platform_angle)
                model.parser()
                self.setup_logger()
                model.run(self.logger)
        elif self.operation == 'ball_on_plate':
                from src.ball_on_plate.task import RunBallOnPlate
                model = RunBallOnPlate()
                model.parse()
                self.setup_logger()
                model.run(self.logger)
        elif self.operation == 'train_ball_on_plate':
                from src.ball_on_plate.task import TrainBallOnPlate
                model = TrainBallOnPlate()
                model.parse()
                self.setup_logger()
                model.run(self.logger)
        elif self.operation == 'video_capture_linux':
                from src.video_capture.task import VideoCaptureLinux
                model = VideoCaptureLinux()
                model.parse()
                self.setup_logger()
                model.run(self.logger)
        elif self.operation == 'video_capture_windows':
                from src.video_capture.task import VideoCaptureWindows
                model = VideoCaptureWindows()
                model.parse()
                self.setup_logger()
                model.run(self.logger)
