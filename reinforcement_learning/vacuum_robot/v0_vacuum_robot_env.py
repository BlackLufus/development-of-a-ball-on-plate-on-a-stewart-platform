import gymnasium as gym
from gymnasium import spaces
from gymnasium.envs.registration import register
from gymnasium.utils.env_checker import check_env

import v0_vacuum_robot as vr
import numpy as np

register(
    id="VacuumRobot-v0",
    entry_point="v0_vacuum_robot_env:VacuumRobotEnv",
)

class VacuumRobotEnv(gym.Env):
    """Custom Environment that follows gym interface.

    This is a simple environment where a robot can move in a grid and pick up a target object.
    The robot can move in four directions: up, down, left, right.
    The robot receives a reward of +1 for picking up the target object and -1 for hitting the walls.
    """
    metadata = {"render_modes": ["human"], "render_fps": 4}

    def __init__(self, grid_rows=5, grid_cols=5, render_mode=None):
        super().__init__()
        self.grid_rows = grid_rows
        self.grid_cols = grid_cols
        self.render_mode = render_mode

        self.varcuum_robot = vr.VacuumRobot(grid_rows, grid_cols, fps=self.metadata["render_fps"])
        self.action_space = spaces.Discrete(len(vr.RobotAction))

        self.observation_space = spaces.Box(
            low=0,
            high=np.array([self.grid_rows-1, self.grid_cols-1, self.grid_rows-1, self.grid_cols-1]),
            shape=(4, ),
            dtype=np.int32,
        )
    
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)

        self.varcuum_robot.reset()
        
        obs = np.concatenate([
            self.varcuum_robot.robot_pos,
            self.varcuum_robot.target_pos
        ])

        info = {}

        if self.render_mode == "human":
            self.render()

        return obs, info
    
    def step(self, action):
        target_reached = self.varcuum_robot.perform_action(vr.RobotAction(action))

        reward = -0.1
        terminated = False
        truncated = False
        if target_reached:
            reward = 10
            terminated = True

        obs = np.concatenate([
            self.varcuum_robot.robot_pos,
            self.varcuum_robot.target_pos
        ])

        info = {
            "robot_pos": self.varcuum_robot.robot_pos,
            "target_pos": self.varcuum_robot.target_pos,
        }

        if self.render_mode == "human":
            print(vr.RobotAction(action))
            self.render()
        
        return obs, reward, terminated, truncated, info
    
    def render(self):
        self.varcuum_robot.render()
    
if __name__ == "__main__":
    env = gym.make("VacuumRobot-v0", render_mode="human")
    
    # Use this to check our custom environment
    # print("Check environment begin")
    # check_env(env.unwrapped)
    # print("Check environment end")

    # Reset environment
    obs, info = env.reset()
    done = False
    
    while not done:
    
        action = env.action_space.sample()  # Sample a random action
        obs, reward, terminated, truncated, info = env.step(action)
        done = terminated or truncated
    
    env.close()