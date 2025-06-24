import math
import os
import sys
import time
import cv2
import numpy as np
import pygame
from os import path
    
class BallOnPlate:

    def __init__(self, fps=1, simulation_mode=True, raw_image_event=None):
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
        self.max_angle = 4

        # Additional varibales
        self.servo_delay = 0.015 # [s] (15ms)
        self.servo_noise_std = 0.1

        # Set random state
        self.np_random = np.random.RandomState()
        self.reset()

        self.fps = fps
        self.simulation_mode = simulation_mode
        self.raw_image_event = raw_image_event
        self.last_action = None
        self._init_pygame()
    
    def _init_pygame(self):
        if self.raw_image_event:
            os.environ["SDL_VIDEODRIVER"] = "dummy"
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
        self.distance_to_target_reward = 0.0
        self.distance_to_target = 0.0
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
        self.last_action = (0, 0)

    def perform_action(self, action) -> bool:

        # Randomize gravitational force
        self.g = np.random.uniform(9.7, 9.9)

        # check if it is simulation mode
        if self.simulation_mode:
            self.delta_t = self.np_random.uniform(0.05, 0.20)
        else:
            self.current_time = time.time()
            self.delta_t = self.current_time - self.last_time
            # print(self.delta_t)
            self.last_time = self.current_time

        # Set roll and pitch for rotation
        desired_roll  = self.last_action[0]
        desired_pitch = self.last_action[1]

        # Calculate delta angles
        delta_roll = desired_roll - self.roll
        delta_pitch = desired_pitch - self.pitch

        # Max agular speed
        self.max_agular_speed = 20.0

        # Degree times delta time
        max_delta_angle = self.max_agular_speed * self.delta_t

        # Result are roll and pitch
        self.roll = np.clip(delta_roll, -max_delta_angle, max_delta_angle)
        self.pitch = np.clip(delta_pitch, -max_delta_angle, max_delta_angle)

        # Get random noise
        noise_roll  = np.random.normal(0.0, self.servo_noise_std)
        noise_pitch = np.random.normal(0.0, self.servo_noise_std)

        # Add noice
        self.roll  = self.roll  + noise_roll
        self.pitch = self.pitch + noise_pitch

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
        self.friction_mu = np.random.uniform(0.96, 0.995)
        self.vx *= self.friction_mu
        self.vy *= self.friction_mu

        # Calculcate position for x
        self.sx = self.sx + self.vx * self.delta_t + (1/2) * self.ax * (self.delta_t * self.delta_t)

        # Calculcate position for y
        self.sy = self.sy + self.vy * self.delta_t + (1/2) * self.ay * (self.delta_t * self.delta_t)

        # Border crossed
        boarder_crossed = False
        if self.sx < -self.real_width/2 or self.sx > self.real_width/2 or self.sy < -self.real_width/2 or self.sy > self.real_width/2:
            boarder_crossed = True

        # Is ball on target
        if (abs(self.sx - self.target_pos[0]) < self.tolerance and 
                abs(self.sy - self.target_pos[1]) < self.tolerance):
            self.distance_to_target_reward = 1 - (math.sqrt(math.pow(self.sx - self.target_pos[0], 2) + math.pow(self.sy - self.target_pos[1], 2)) / self.tolerance)
            self.isOnTargetTime += self.delta_t
        else:
            self.distance_to_target_reward = -1
            self.isOnTargetTime = 0

        self.distance_to_target = math.sqrt(math.pow(self.sx - self.target_pos[0], 2) + math.pow(self.sy - self.target_pos[1], 2)) / self.plate_radius

        # Store last action
        self.last_action = action
            
        return self.isOnTargetTime >= 3.0, self.distance_to_target_reward, boarder_crossed
    
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
        x_axis_img = self.action_font.render(f'X-Axis: {round(float(self.roll), 2)}°', True, (0,0,0), (255,255,255))
        x_axis_pos = (0, self.window_size[1] - self.action_info_height * 5)
        self.window_surface.blit(x_axis_img, x_axis_pos)

        # Draw Y-Axis (pitch)
        y_axis_img = self.action_font.render(f'Y-Axis: {round(float(self.pitch), 2)}°', True, (0,0,0), (255,255,255))
        y_axis_pos = (0, self.window_size[1] - self.action_info_height * 4)
        self.window_surface.blit(y_axis_img, y_axis_pos)

        # Draw Accelerate
        accelerate_img = self.action_font.render(f'Accelerate -> x:{round(self.ax * 100, 2)}cm/s y:{round(self.ay * 100, 2)}cm/s', True, (0,0,0), (255,255,255))
        accelerate_pos = (0, self.window_size[1] - self.action_info_height * 3)
        self.window_surface.blit(accelerate_img, accelerate_pos)

        # Draw Velocity
        velocity_img = self.action_font.render(f'Velocity -> x:{round(self.vx * 100, 2)}cm/s² y:{round(self.vy * 100, 2)}cm/s²', True, (0,0,0), (255,255,255))
        velocity_pos = (0, self.window_size[1] - self.action_info_height * 2)
        self.window_surface.blit(velocity_img, velocity_pos)

        # Draw Position
        position_img = self.action_font.render(f'Position -> x:{round(self.sx * 100, 2)}cm ({pos[0]}) y:{round(self.sy * 100, 2)}cm ({pos[1]})', True, (0,0,0), (255,255,255))
        position_pos = (0, self.window_size[1] - self.action_info_height * 1)
        self.window_surface.blit(position_img, position_pos)

        # Draw Target Position
        if not self.raw_image_event:
            pygame.display.update()
        # Save image
        else:
            surface_array = pygame.surfarray.array3d(pygame.display.get_surface())  
            image = np.transpose(surface_array, (1, 0, 2))  # (width, height, 3) -> (height, width, 3)
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)  # Correct color from RGB to BGR for OpenCV
            success, encoded_image = cv2.imencode('.jpg', image)
            if success:
                self.raw_image_event(encoded_image)
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

    ballOnPlate = BallOnPlate(fps=20, simulation_mode=False)
    ballOnPlate.render()
    while(True):

        random_action = (
            np.random.uniform(-ballOnPlate.max_angle, ballOnPlate.max_angle),
            np.random.uniform(-ballOnPlate.max_angle, ballOnPlate.max_angle)
        )
        print(f"Performing action: {random_action}")

        ballOnPlate.perform_action(random_action)
        ballOnPlate.render()
