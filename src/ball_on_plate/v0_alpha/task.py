from asyncio import Event
import gymnasium as gym
import logging
from stable_baselines3 import A2C, DQN, PPO

from src.ball_on_plate.v0_alpha import environment
from src.stewart_platform.servo_motor_handler import ServoMotorHandler
from src.stewart_platform.stewart_platform import StewartPlatform
from src.video_capture.video_capture import CameraThreadWithAV

def run(env_id, path_to_model, platform:StewartPlatform, cam:CameraThreadWithAV, sb3_model, device='cpu', render_fps=32, logger: logging=None, stop_event: Event=None):
    logger = logger or logging.getLogger(__name__)

    smh = ServoMotorHandler(logger)

    env = gym.make(env_id, platform, smh, cam, render_fps=render_fps)

    if sb3_model == "a2c":
        model = A2C.load(
            path_to_model,
            env=env,
            device=device
        )
    elif sb3_model == "dqn":
        model = DQN.load(
            path_to_model,
            env=env,
            device=device
        )
    elif sb3_model == "ppo":
        model = PPO.load(
            path_to_model,
            env=env,
            device=device
        )
        
    count = 0
    # Run a test
    obs = env.reset()[0]
    env.render()
    terminated = False
    while True and not stop_event.is_set():
        count += 1
        action, _ = model.predict(observation=obs, deterministic=True) # Turn on deterministic, so predict always returns the same behavior
        obs, _, terminated, truncated, _ = env.step(action)

        env.render()

        if terminated or truncated:
            if terminated:
                logger.debug(f"Success (count: {count})")
            else:
                logger.debug(f"Failed (count: {count})")
            break
        