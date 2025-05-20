import gym

from stable_baselines3 import A2C, DQN, PPO

from src.ball_on_plate.v0 import environment

class BallOnPlate:
    def __init__(self, env_id, render_fps, sb3_model, path_to_model, device, plate_size, max_angle):
        self.env = gym.make(env_id, simulation_mode=False, render_fps=render_fps, raw_image_event=None)
        self.sb3_model = sb3_model
        self.path_to_model = path_to_model
        self.device = device
        
        self.plate_size = plate_size, # (width, height) in m
        self.max_angle = max_angle # in degrees

        self.gravity = 9.81  # Gravity constant

    def apply_force(self, force):
        # Apply a force to the ball and update its position
        # This is a placeholder for the actual physics simulation
        pass

    def get_ball_position(self):
        return self.ball_position

    def reset(self):
        self.ball_position = (self.plate_size[0] / 2, self.plate_size[1] / 2)
    
    def run(self):
        if self.sb3_model == "a2c":
            model = A2C.load(
                self.path_to_model,
                env=self.env,
                device=self.device
            )
        elif self.sb3_model == "dqn":
            model = DQN.load(
                self.path_to_model,
                env=self.env,
                device=self.device
            )
        elif self.sb3_model == "ppo":
            model = PPO.load(
                self.path_to_model,
                env=self.env,
                device=self.device
            )
        
        obs = self.env.reset()[0]
        terminated = False
        while True:

            action, _ = model.predict(observation=obs, deterministic=False)