import gymnasium as gym
from gymnasium import spaces
from gymnasium.envs.registration import register
from gymnasium.utils.env_checker import check_env


from src.ball_on_plate.v0 import agent as bop
import numpy as np

gym.registry.clear()

register(
    id="BallOnPlate-v0",
    entry_point="src.ball_on_plate.v0.environment:BallOnPlateEnv",
)

class BallOnPlateEnv(gym.Env):
    """Custom Environment that follows gym interface.

    This is a simple environment where a robot can move in a grid and pick up a target object.
    The robot can move in four directions: up, down, left, right.
    The robot receives a reward of +1 for picking up the target object and -1 for hitting the walls.
    """
    metadata = {"render_modes": ["human"]}

    def __init__(self, render_mode=None, render_fps=60, simulation_mode=True, show_display=True):
        super().__init__()
        self.render_mode = render_mode

        self.ball = bop.BallOnPlate(fps=render_fps, simulation_mode=simulation_mode, show_display=show_display)
        self.action_space = spaces.Box(
            low=np.array([
                -self.ball.max_angle,
                -self.ball.max_angle
            ]),
            high=np.array([
                self.ball.max_angle,
                self.ball.max_angle
            ]),
            shape=(2, ),
            dtype=np.float32
        ) 
        # spaces.Discrete(len(bop.BallOnPlateAction))

        self.observation_space = spaces.Box(
            low=np.array([
                -1.0, -1.0,
                -1.0, -1.0,
                -self.ball.max_angle, -self.ball.max_angle,
                -1.0, -1.0,
                0.0
            ]),
            high=np.array([
                1.0, 1.0,
                1.0, 1.0,
                self.ball.max_angle, self.ball.max_angle,
                1.0, 1.0,
                1.0
            ]),
            shape=(9, ),
            dtype=np.float32
        )

        self.max_steps = 1000

    def _get_state(self):
        obs = np.array([
            self.ball.sx / self.ball.plate_radius,
            self.ball.sy / self.ball.plate_radius,
            self.ball.vx / self.ball.max_velocity,
            self.ball.vy / self.ball.max_velocity,
            np.deg2rad(self.ball.roll),
            np.deg2rad(self.ball.pitch),
            self.ball.target_pos[0] / self.ball.plate_radius,
            self.ball.target_pos[1] / self.ball.plate_radius,
            1.0 if self.ball.isOnTarget else 0.0
        ], dtype=np.float32)
        return obs
    
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)

        self.steps = 0

        self.ball.reset(seed)
        
        obs = self._get_state()

        info = {}

        if self.render_mode == "human":
            self.render()

        return obs, info
    
    def step(self, action):

        # Increment steps
        self.steps += 1

        # Perform action and get some informations back
        # old_dist = np.linalg.norm(np.array(self.ball.target_pos) - np.array([self.ball.sx, self.ball.sy]))
        finish, isOnTarget, boarder_crossed = self.ball.perform_action(action)
        # new_dist = np.linalg.norm(np.array(self.ball.target_pos) - np.array([self.ball.sx, self.ball.sy]))

        # Basic rewards
        reward = -1
        if isOnTarget:
            reward += 2

        # Check ending condition
        terminated = False
        truncated = False
        if finish:
            reward += 100
            terminated = True
        elif self.steps > self.max_steps or boarder_crossed:
            reward -= 100
            truncated = True

        # Get observation
        obs = self._get_state()

        # Generate some info for debug, just in case you need it
        info = {
            "ball_pos": (self.ball.sx, self.ball.sy),
            "target_pos": self.ball.target_pos,
        }

        return obs, reward, terminated, truncated, info
    
    def render(self):
        self.ball.render()
    
if __name__ == "__main__":
    env = gym.make("BallOnPlate-v0", render_mode="human", render_fps=5, simulation_mode=True)
    
    # Use this to check our custom environment
    print("Check environment begin")
    check_env(env.unwrapped)
    print("Check environment end")

    for _ in range(10):
        
        # Reset environment
        obs, info = env.reset()
        done = False

        while not done:
        
            action = env.action_space.sample()  # Sample a random action
            print(action)
            obs, reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated

            if env.render_mode == "human":
                print(action)
                print(f"Reward {reward}")
                env.render()
        
        env.close()