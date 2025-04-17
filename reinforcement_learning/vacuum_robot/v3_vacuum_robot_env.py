import gymnasium as gym
from gymnasium import spaces
from gymnasium.envs.registration import register
from gymnasium.utils.env_checker import check_env

import v3_vacuum_robot as vr
import numpy as np

gym.registry.clear()

register(
    id="VacuumRobot-v3",
    entry_point="v3_vacuum_robot_env:VacuumRobotEnv",
)

class VacuumRobotEnv(gym.Env):
    """Custom Environment that follows gym interface.

    This is a simple environment where a robot can move in a grid and pick up a target object.
    The robot can move in four directions: up, down, left, right.
    The robot receives a reward of +1 for picking up the target object and -1 for hitting the walls.
    """
    metadata = {"render_modes": ["human"], "render_fps": 4}

    def __init__(self, grid_rows=5, grid_cols=5, n_dirt=5, n_wall=4, render_mode=None, debug=False):
        super().__init__()
        self.grid_rows = grid_rows
        self.grid_cols = grid_cols
        self.render_mode = render_mode
        self.debug = debug

        self.varcuum_robot = vr.VacuumRobot(grid_rows, grid_cols, n_dirt, n_wall, fps=self.metadata["render_fps"])
        self.action_space = spaces.Discrete(len(vr.RobotAction))

        self.observation_space = spaces.Box(
            low=0,
            high=1.0,
            shape=(4, self.grid_rows, self.grid_cols),
            dtype=np.float32,
        )

        self.reset()
    
    def _get_state(self):
        obs = np.zeros(shape=self.observation_space.shape, dtype=np.float32)
        
        # Set robot pos
        row_pos, col_pos = self.varcuum_robot.robot_station_pos
        obs[0, row_pos, col_pos] = 1.0

        # Set robot pos
        row_pos, col_pos = self.varcuum_robot.robot_pos
        obs[1, row_pos, col_pos] = 1.0
        
        # Set dust pos
        for row_pos, col_pos in self.varcuum_robot.dust_list:
            obs[2, row_pos, col_pos] = 1.0

        # Set dust pos
        for row_pos, col_pos in self.varcuum_robot.wall_list:
            obs[3, row_pos, col_pos] = 1.0
        
        return obs

    
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)

        self.steps = 0

        self.varcuum_robot.reset(seed)
        
        obs = self._get_state()

        info = {}

        if self.render_mode == "human":
            self.render()

        return obs, info
    
    def step(self, action):

        # Increment steps
        self.steps += 1

        # Perform action and get some informations back
        tile_cleaned, all_tiles_cleaned, robot_at_station, hit_wall = self.varcuum_robot.perform_action(vr.RobotAction(action))

        # Basic rewards
        reward = -1
        if tile_cleaned:
            reward += 5
        elif vr.RobotAction(action) == vr.RobotAction.SUCK:
            reward -= 1
        elif hit_wall:
            reward -= 1
        
        # Check ending condition
        terminated = False
        truncated = False
        if all_tiles_cleaned and robot_at_station:
            reward += 20
            terminated = True
        elif self.steps > self.grid_rows * self.grid_cols * 2:
            reward -= 20
            truncated = True

        # Get observation
        obs = self._get_state()

        # Generate some info for debug, just in case you need it
        info = {
            "robot_pos": self.varcuum_robot.robot_pos,
            "dust_list": self.varcuum_robot.dust_list
        }
        
        return obs, reward, terminated, truncated, info
    
    def render(self):
        self.varcuum_robot.render()
    
if __name__ == "__main__":
    env = gym.make("VacuumRobot-v3", render_mode="human")
    
    # Use this to check our custom environment
    print("Check environment begin")
    check_env(env.unwrapped)
    print("Check environment end")

    # Reset environment
    obs, info = env.reset()
    done = False
    
    while not done:
    
        action = env.action_space.sample()  # Sample a random action
        obs, reward, terminated, truncated, info = env.step(action)
        done = terminated or truncated

        if env.render_mode == "human":
            print(vr.RobotAction(action))
            print(f"Reward {reward}")
            env.render()
    
    env.close()