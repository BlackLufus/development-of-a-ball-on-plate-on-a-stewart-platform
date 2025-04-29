from enum import Enum
import math
import random
import sys
import time
import numpy as np
import pygame
from os import path
    
class BallOnPlate:

    def __init__(self, fps=1, simulation_mode=True):
        self.screen_size = 512

        # Physikalische Parameter
        self.real_width = 0.3 # 30 cm in Metern
        self.plate_radius = self.real_width / 2
        self.boarder_distance = 0.05
        self.pixels_per_meter = 512 / self.real_width  # 1706.6667 px/m
        
        # Gravity
        self.g = 9.81
        self.max_velocity = 0.15
        self.max_angle = 7.5

        # Set random state
        self.np_random = np.random.RandomState()
        self.reset()

        self.fps = fps
        self.simulation_mode = simulation_mode
        self.last_action = None
        self._init_pygame()
    
    def _init_pygame(self):
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
        self.isOnTarget = False
        self.isOnTargetTime = 0.0
        self.roll = 0.0 # X-Axis
        self.pitch = 0.0 # Y-Axis
        self.ax = 0.0 # m/s^2
        self.ay = 0.0 # m/s^2
        self.vx = 0.0 # s/t
        self.vy = 0.0 # s/t
        self.sx = self.np_random.uniform(-self.plate_radius, self.plate_radius) # Position in Meter
        self.sy = self.np_random.uniform(-self.plate_radius, self.plate_radius) # Position in Meter
        self.target_pos = (
            self.np_random.uniform(-self.plate_radius + self.boarder_distance, self.plate_radius - self.boarder_distance),
            self.np_random.uniform(-self.plate_radius + self.boarder_distance, self.plate_radius - self.boarder_distance)
        )
        self.last_time = time.time()

    def perform_action(self, action) -> bool:
        # Store last action
        self.last_action = action

        # check if it is simulation mode
        if self.simulation_mode:
            self.delta_t = self.np_random.uniform(0.01, 0.20)
        else:
            self.current_time = time.time()
            self.delta_t = self.current_time - self.last_time
            print(self.delta_t)
            self.last_time = self.current_time

        # Set roll and pitch for rotation
        self.roll = action[0]
        self.pitch = action[1]

        # Calculate accelerate for x
        roll_theta = math.radians(self.roll)
        self.ax = (3/5) * self.g * np.sin(roll_theta)

        # Calculate accelerate for y
        pitch_theta = math.radians(self.pitch)
        self.ay = (3/5) * self.g * np.sin(pitch_theta)

        # Calculcate velocity for x
        self.vx = self.vx + self.ax * self.delta_t

        # Calculcate velocity for y
        self.vy = self.vy + self.ay * self.delta_t

        # friction (This need to be fixed)
        friction = 0.9999
        self.vx *=friction
        self.vy *=friction

        # Calculcate position for x
        self.sx = self.sx + self.vx * self.delta_t + (1/2) * self.ax * (self.delta_t * self.delta_t)

        # Calculcate position for y
        self.sy = self.sy + self.vy * self.delta_t + (1/2) * self.ay * (self.delta_t * self.delta_t)

        # Border crossed
        boarder_crossed = False
        if self.sx < -self.real_width/2 or self.sx > self.real_width/2 or self.sy < -self.real_width/2 or self.sy > self.real_width/2:
            boarder_crossed = True

        # Is ball on target
        tolerance = 0.025
        if (abs(self.sx - self.target_pos[0]) < tolerance and 
                abs(self.sy - self.target_pos[1]) < tolerance):
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
        text_pos = (0, self.window_size[1] - self.action_info_height * 6)
        self.window_surface.blit(text_img, text_pos)

        # Draw X-Axis (roll)
        x_axis_img = self.action_font.render(f'X-Axis: {round(self.roll, 5)}', True, (0,0,0), (255,255,255))
        x_axis_pos = (0, self.window_size[1] - self.action_info_height * 5)
        self.window_surface.blit(x_axis_img, x_axis_pos)

        # Draw Y-Axis (pitch)
        y_axis_img = self.action_font.render(f'Y-Axis: {round(self.pitch, 5)}', True, (0,0,0), (255,255,255))
        y_axis_pos = (0, self.window_size[1] - self.action_info_height * 4)
        self.window_surface.blit(y_axis_img, y_axis_pos)

        # Draw Accelerate
        accelerate_img = self.action_font.render(f'Accelerate -> x:{round(self.ax, 5)} y:{round(self.ay, 5)}', True, (0,0,0), (255,255,255))
        accelerate_pos = (0, self.window_size[1] - self.action_info_height * 3)
        self.window_surface.blit(accelerate_img, accelerate_pos)

        # Draw Velocity
        velocity_img = self.action_font.render(f'Velocity -> x:{round(self.vx, 5)} y:{round(self.vy, 5)}', True, (0,0,0), (255,255,255))
        velocity_pos = (0, self.window_size[1] - self.action_info_height * 2)
        self.window_surface.blit(velocity_img, velocity_pos)

        # Draw Position
        position_img = self.action_font.render(f'Position -> x:{round(self.sx, 5)} y:{round(self.sy, 5)}', True, (0,0,0), (255,255,255))
        position_pos = (0, self.window_size[1] - self.action_info_height * 1)
        self.window_surface.blit(position_img, position_pos)

        pygame.display.update()
                
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

    ballOnPlate = BallOnPlate(fps=60, simulation_mode=False)
    ballOnPlate.render()
    while(True):

        random_action = (
            np.random.uniform(-ballOnPlate.max_angle, ballOnPlate.max_angle),
            np.random.uniform(-ballOnPlate.max_angle, ballOnPlate.max_angle)
        )
        print(f"Performing action: {random_action}")

        ballOnPlate.perform_action(random_action)
        ballOnPlate.render()
