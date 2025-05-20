import argparse
import logging
import time


class Nunchuk:

    def __init__(self, base_radius: int, base_angle: list, platform_radius: int, platform_angle: list):
        self.base_radius = base_radius
        self.base_angle = base_angle
        self.platform_radius = platform_radius
        self.platform_angle = platform_angle

    """
    A class to handle the Nunchuk controller.
    """
    def parser(self, parser=None):
        parser = argparse.ArgumentParser(
            parents=[parser] if parser else [],
            prog='Set',
            usage='%(prog)s [options]',
            description='Set the Stewart platform.',
            epilog='Example: %(prog)s -r 5.8 -p 0',
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
            '-p',
            '--period',
            help='Set the period of the circle',
            required=False,
            type=float,
            default=0
        )
        parser.add_argument(
            '--use_accelerometer',
            help='Use the accelerometer',
            required=False,
            action='store_true',
            default=False,
        )

        self.args, _ = parser.parse_known_args()
        self.radius = self.args.radius
        self.period = self.args.period
        self.use_accelerometer = self.args.use_accelerometer
    
    def manual(self, radius, period, use_accelerometer):
        """
        Set the parameters for the Nunchuk controller.
        """
        self.radius = radius
        self.period = period
        self.use_accelerometer = use_accelerometer

    def run(self, logger):        
        from src.stewart_platform.stewart_platform import StewartPlatform
        from src.stewart_platform.servo_motor_handler import ServoMotorHandler
        from src.nunchuk.nunchuk import Nunchuk

        # Initialize the Stewart platform
        platform = StewartPlatform(self.base_radius, self.base_angle, self.platform_radius, self.platform_angle)
        
        # Initialize the servo motor handler
        smh = ServoMotorHandler(logger)

        # Initialize the Nunchuk controller
        nc = Nunchuk()

        # Get the arguments
        radius = self.radius
        period = self.period
        use_accelerometer = self.use_accelerometer
        logger = logger or logging.getLogger("StewartPlatform.Circle")

        while True:
            # Get the Nunchuk values
            nc.measure()
            nc.dump()
            
            # Calculate the x and y offsets based on the Nunchuk values
            if use_accelerometer:
                x_offset = radius / 512 * (nc.accel_x_mean - 512)
                if x_offset > radius:
                    x_offset = radius
                elif x_offset < -radius:
                    x_offset = -radius
                y_offset = -(radius / 512 * (nc.accel_y_mean - 512))
                if y_offset > radius:
                    y_offset = radius
                elif y_offset < -radius:
                    y_offset = -radius
            
            # If not using the accelerometer, use the joystick values
            else:
                x_offset = radius / 128 * (nc.joy_x - 128)
                y_offset = -(radius / 128 * (nc.joy_y - 128))
            try:
                # Set the angle of the Stewart platform based on the Nunchuk values
                smh.set(platform, 0, 0, 62, x_offset, y_offset, 0)
            except:
                pass
            
            # Sleep for the specified period
            time.sleep(period)
