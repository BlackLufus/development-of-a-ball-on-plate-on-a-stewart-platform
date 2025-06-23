import sys
import time
import numpy as np
import pygame
from os import path

from src.detection.opencv.ball_tracker import BallTracker
from src.stewart_platform.servo_motor_handler import ServoMotorHandler
from src.stewart_platform.stewart_platform import StewartPlatform
    
class BallOnPlate:

    def __init__(self, fps=1, friction=0.95, Kp=4.0, Ki=2.0, Kd=1.0):
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
        
        self.screen_size = 512

        # Physikalische Parameter
        self.real_width = 0.15 # 30 cm in Metern (m)
        self.plate_radius = self.real_width / 2 # In meter (m)
        self.boarder_distance = 0.01 # in meter (m)
        self.tolerance = 0.015 # Tolerance next to target in meter (m)
        self.pixels_per_meter = 512 / self.real_width  # Convert platform to computer-readable coordinate system ()
        
        # Gravity
        self.g = 9.81
        self.max_velocity = 0.15
        self.max_angle = np.radians(4.0)
        self.friction = friction

        # PID-Controller
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd

        # Zustand
        self.integral_x = 0.0
        self.integral_y = 0.0
        self.prev_error_x = 0.0
        self.prev_error_y = 0.0
        self.delta_t = 0.1 # 100 ms in seconds (s)

        # Set random state
        self.np_random = np.random.RandomState()
        self.reset()

        self.fps = fps
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
        self.roll_theta = 0.0
        self.pitch_theta = 0.0
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

        position = None
        while not position:
            position = self.ball_tracker.get_ball_position()
            time.sleep(0.01)

        # Get initial ball position
        self.sx_old, self.sy_old = position

        # Set current time
        self.last_time = time.time()

    def perform_action(self) -> bool:
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

        # Get Target Position
        tsx, tsy = self.target_pos

        # PID for x
        ex = tsx - self.sx
        self.integral_x += ex * self.delta_t
        derivative_x = (ex - self.prev_error_x) / self.delta_t
        self.prev_error_x = ex
        ux = self.Kp * ex + self.Ki * self.integral_x + self.Kd * derivative_x

        # Set roll
        self.roll_theta = np.clip(ux, -self.max_angle, self.max_angle)
        self.roll = np.degrees(self.roll_theta)

        # PID for y
        ey = tsy - self.sy
        self.integral_y += ey * self.delta_t
        derivative_y = (ey - self.prev_error_y) / self.delta_t
        self.prev_error_y = ey
        uy = self.Kp * ey + self.Ki * self.integral_y + self.Kd * derivative_y

        # # Set pitch
        self.pitch_theta = np.clip(uy, -self.max_angle, self.max_angle)
        self.pitch = np.degrees(self.pitch_theta)

        # Check border crossed
        boarder_crossed = True if self.sx < -self.real_width/2 or self.sx > self.real_width/2 or self.sy < -self.real_width/2 or self.sy > self.real_width/2 else False

        # Is ball on target
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

    agent = BallOnPlate(fps=10, simulation_mode=False, friction=0.8, Kp=1.0, Ki=0.0, Kd=0.20)

    for _ in range(10):
        agent.reset()
        agent.render()
        while(True):
            finish, isOnTarget, boarder_crossed = agent.perform_action()
            print(f"Is on target: {isOnTarget}")
            agent.render()
            if finish:
                print("Episode is Successful!")
                break
            elif boarder_crossed:
                print("Episode Failed!")
                break
