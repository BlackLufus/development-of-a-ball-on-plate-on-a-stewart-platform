import math
import os
import sys
import time
import cv2
import numpy as np
import pygame
from os import path

from src.detection.opencv.ball_tracker import BallTracker
from src.stewart_platform.servo_motor_handler import ServoMotorHandler
from src.stewart_platform.stewart_platform import StewartPlatform
    
class BallOnPlate:

    def __init__(self, fps=1):
        self.ball_tracker = BallTracker(debug=False)

        # Initialize the platform
        self.platform = StewartPlatform(
            86,
            [
                343,
                19,
                101,
                139,
                221,
                259
            ],
            86,
            [
                347,
                13,
                107,
                133,
                227,
                253
            ]
        )

        # Initialize the servo motor handler
        self.smh = ServoMotorHandler()

        # Set screen size
        self.screen_size = 512

        # Physikalische Parameter
        self.real_width = 0.20 # 30 cm in Metern (m)
        self.plate_radius = self.real_width / 2 # In meter (m)
        self.boarder_distance = 0.01 # in meter (m)
        self.tolerance = 0.015 # Tolerance next to target in meter (m)
        self.pixels_per_meter = 512 / self.real_width  # Convert platform to computer-readable coordinate system ()
        
        # Gravity
        self.g = 9.81
        self.max_velocity = 0.15
        self.max_angle = 7.5

        # Set random state
        self.np_random = np.random.RandomState()
        self.reset()

        self.fps = fps
        self.last_action = None
        self._init_pygame()
    
    def _init_pygame(self):
        # if self.raw_image_event:
        #     os.environ["SDL_VIDEODRIVER"] = "dummy"
        pygame.init() # initialize pygame
        pygame.display.init() # Initialize the display module

        # Game clock
        self.clock = pygame.time.Clock()

        # Default font
        self.action_font = pygame.font.SysFont("Calibre",30)
        self.action_info_height = self.action_font.get_height()

        # For rendering (floor)
        self.floor_cell_size = 64

        # For rendering (circle)
        self.circle_cell_size = 64

        # For rendering (floor)
        self.ball_cell_size = 64

        # Define game window size (width, height)
        self.window_size = (
            self.floor_cell_size * 8, 
            self.floor_cell_size * 8 + self.action_info_height * 6
        )

        # Initialize game window
        self.window_surface = pygame.display.set_mode(self.window_size) 

        # Load & resize images
        file_name = path.join(path.dirname(__file__), "images/ball.png")
        img = pygame.image.load(file_name)
        self.ball_img = pygame.transform.scale(img, (self.ball_cell_size, self.ball_cell_size))

        file_name = path.join(path.dirname(__file__), "images/circle.png")
        img = pygame.image.load(file_name)
        self.circle_img = pygame.transform.scale(img, (self.circle_cell_size, self.circle_cell_size))

        file_name = path.join(path.dirname(__file__), "images/floor.png")
        img = pygame.image.load(file_name)
        self.floor_img = pygame.transform.scale(img, (self.floor_cell_size, self.floor_cell_size))

    def reset(self, seed=None):
        if seed is not None:
            self.np_random = np.random.RandomState(seed)

        self.smh.set(self.platform, 0, 0, 62, 0, 0, 0)

        # initialize variables
        self.isOnTarget = False
        self.isOnTargetTime = 0.0
        self.roll = 0.0 # X-Axis
        self.pitch = 0.0 # Y-Axis
        self.vx = 0.0 # s/t
        self.vy = 0.0 # s/t
        self.sx = 0.0 # Position in Meter
        self.sy = 0.0 # Position in Meter

        # Set random target position
        self.target_pos = (
            0,
            0
            # self.np_random.uniform(-self.plate_radius + self.boarder_distance, self.plate_radius - self.boarder_distance),
            # self.np_random.uniform(-self.plate_radius + self.boarder_distance, self.plate_radius - self.boarder_distance)
        )

        position = None
        while not position:
            position = self.ball_tracker.get_ball_position()
            time.sleep(0.01)

        # Get initial ball position
        self.sx_old, self.sy_old = position

        # Set current time
        self.last_time = time.time()

    def get_ball_position(self, frame):
        """
        Arguments: 
        - frame: The
        """
        # Get ball position

        # Convert to real world coordinates
        x = (x - self.screen_size/2) / self.pixels_per_meter
        y = (y - self.screen_size/2) / self.pixels_per_meter
        return x, y

    def perform_action(self, action) -> bool:
        # Store last action
        self.last_action = action

        # Set roll and pitch for rotation
        self.roll = min(4, action[0])
        self.pitch = min(4, action[1])
        self.smh.set(self.platform, 0, 0, 62, self.roll, self.pitch, 0)


        position = None
        while not position:
            position = self.ball_tracker.get_ball_position()
            time.sleep(0.01)

        # Get current time
        self.current_time = time.time()
        self.delta_t = self.current_time - self.last_time
        self.last_time = self.current_time
        
        # Get new ball position
        self.sx, self.sy = position

        self.sx = int((self.sx / 644) * 512)
        self.sy = int((self.sy / 600) * 512)

        self.sx = (self.sx - self.screen_size/2) / self.pixels_per_meter
        self.sy = (self.sy - self.screen_size/2) / self.pixels_per_meter

        # Get Velocity
        self.vx = (self.sx - self.sx_old) / self.delta_t
        self.vy = (self.sy - self.sy_old) / self.delta_t
        self.sx_old = self.sx
        self.sy_old = self.sy

        # Check if ball crossed the border
        boarder_crossed = True if self.sx < -self.real_width/2 or self.sx > self.real_width/2 or self.sy < -self.real_width/2 or self.sy > self.real_width/2 else False

        # Check if ball is on target
        if (abs(self.sx - self.target_pos[0]) < self.tolerance and 
                abs(self.sy - self.target_pos[1]) < self.tolerance):
            self.isOnTarget = True
            self.isOnTargetTime += self.delta_t
        else:
            self.isOnTarget = False
            self.isOnTargetTime = 0
        return self.isOnTargetTime >= 3.0, self.isOnTarget, boarder_crossed

    def _meters_to_pixels(self, x, y, img_size):
        """Umrechnung physikalische Koordinaten (Meter) zu Pixelkoordinaten"""
        px = (x * self.pixels_per_meter) + self.screen_size/2 - img_size / 2
        py = (y * self.pixels_per_meter) + self.screen_size/2 - img_size / 2
        return int(px), int(py)
    
    def render(self):

        self._process_events()

        # clear to white background, otherwise text with varying length will leave behind prior rendered portions
        self.window_surface.fill((255,255,255))

        # Print current state on console
        for r in range(8):
            for c in range(8):
                
                # Draw floor
                pos = (c * self.floor_cell_size, r * self.floor_cell_size)
                self.window_surface.blit(self.floor_img, pos)

        # Draw circle
        pos = self._meters_to_pixels(*self.target_pos, self.circle_cell_size)
        self.window_surface.blit(self.circle_img, pos)

        # Draw ball
        pos = self._meters_to_pixels(self.sx, self.sy, self.ball_cell_size)
        self.window_surface.blit(self.ball_img, pos)

        # Draw Action
        text_img = self.action_font.render(f'Action: {self.last_action}', True, (0,0,0), (255,255,255))
        text_pos = (0, self.window_size[1] - self.action_info_height * 5)
        self.window_surface.blit(text_img, text_pos)

        # Draw X-Axis (roll)
        x_axis_img = self.action_font.render(f'X-Axis: {round(float(self.roll), 2)}°', True, (0,0,0), (255,255,255))
        x_axis_pos = (0, self.window_size[1] - self.action_info_height * 4)
        self.window_surface.blit(x_axis_img, x_axis_pos)

        # Draw Y-Axis (pitch)
        y_axis_img = self.action_font.render(f'Y-Axis: {round(float(self.pitch), 2)}°', True, (0,0,0), (255,255,255))
        y_axis_pos = (0, self.window_size[1] - self.action_info_height * 3)
        self.window_surface.blit(y_axis_img, y_axis_pos)

        # Draw Velocity
        velocity_img = self.action_font.render(f'Velocity -> x:{round(self.vx * 100, 2)}cm/s² y:{round(self.vy * 100, 2)}cm/s²', True, (0,0,0), (255,255,255))
        velocity_pos = (0, self.window_size[1] - self.action_info_height * 2)
        self.window_surface.blit(velocity_img, velocity_pos)

        # Draw Position
        position_img = self.action_font.render(f'Position -> x:{round(self.sx * 100, 2)}cm ({pos[0]}) y:{round(self.sy * 100, 2)}cm ({pos[1]})', True, (0,0,0), (255,255,255))
        position_pos = (0, self.window_size[1] - self.action_info_height * 1)
        self.window_surface.blit(position_img, position_pos)

        # Draw Target Position
        # if not self.raw_image_event:
        pygame.display.update()
        # Save image
        # else:
        #     surface_array = pygame.surfarray.array3d(pygame.display.get_surface())  
        #     image = np.transpose(surface_array, (1, 0, 2))  # (width, height, 3) -> (height, width, 3)
        #     image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)  # Correct color from RGB to BGR for OpenCV
        #     success, encoded_image = cv2.imencode('.jpg', image)
        #     if success:
        #         self.raw_image_event(encoded_image)
            # image.save(f'test_image/{datetime.now().strftime("%Y%m%d-%H%M%S%f")}.png')
            
                
        # Limit frames per second
        self.clock.tick(self.fps)

    def _process_events(self):
        # Process user events, key presses
        for event in pygame.event.get():
            # User clicked on X at the top right corner of window
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if(event.type == pygame.KEYDOWN):
                # User hit escape
                if(event.key == pygame.K_ESCAPE):
                    pygame.quit()
                    sys.exit()


if __name__ == "__main__":

    ballOnPlate = BallOnPlate(fps=20)
    ballOnPlate.render()
    while(True):

        random_action = (
            np.random.uniform(-ballOnPlate.max_angle, ballOnPlate.max_angle),
            np.random.uniform(-ballOnPlate.max_angle, ballOnPlate.max_angle)
        )
        print(f"Performing action: {random_action}")

        ballOnPlate.perform_action(random_action)
        ballOnPlate.render()
