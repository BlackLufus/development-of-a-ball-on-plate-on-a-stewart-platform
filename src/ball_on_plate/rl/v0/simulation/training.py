from asyncio import Event
import os
import time
import gymnasium as gym
import numpy as np
import logging
from stable_baselines3 import A2C, DQN, PPO
from stable_baselines3.common.callbacks import EvalCallback

from src.ball_on_plate.v0 import environment

def train_sb3(env_id, id, sb3_model="PPO", use_existing_model=None, device='cpu', sequential_execution=False, iterations = 40, steps_per_iteration=5_000, logger=None):
    os.makedirs(f"./models/bop/{id}", exist_ok=True)

    env = gym.make(env_id)

    # Evaluierung während des Trainings
    eval_callback = EvalCallback(
        env,
        eval_freq=10000,
        n_eval_episodes=10,
        deterministic=True,
        render=False,
        best_model_save_path=f"./models/bop/{id}"
    )

    if sb3_model == "a2c":
        if use_existing_model is not None:
            model = A2C.load(
                use_existing_model,
                env,
                device=device
            )
        else:
            model = A2C(
                "MlpPolicy",
                env,
                verbose=1,
                learning_rate=3e-4,
                gamma=0.99,
                tensorboard_log=f"./tensorboard/bop/{id}",
                device=device
            )
    elif sb3_model == "dqn":
        if use_existing_model is not None:
            model = DQN(
                use_existing_model,
                env,
                device=device
            )
        else:
            model = DQN(
                "MlpPolicy",
                env,
                verbose=1,
                learning_rate=3e-4,
                gamma=0.99,
                batch_size=64,
                tensorboard_log=f"./tensorboard/bop/{id}",
                device=device
            )
    # PPO mit angepassten Hyperparametern
    elif sb3_model == "ppo":
        if use_existing_model is not None:
            model = PPO(
                use_existing_model,
                env,
                device=device
            )
        else:
            model = PPO(
                "MlpPolicy",
                env,
                verbose=1,
                learning_rate=3e-4,
                gamma=0.99,
                n_steps=256,
                batch_size=64,
                ent_coef=0.01,
                tensorboard_log=f"./tensorboard/bop/{id}",
                device=device
            )

    for _ in range(iterations):
        model.learn(
            total_timesteps=steps_per_iteration,
            callback=eval_callback,
            progress_bar=True,
            reset_num_timesteps=False
        )

        model.save(f"./models/bop/{id}/{model_name}")

        if sequential_execution:
            run_sb3(env_id, dir, model_name, model="PPO", episods=1, simulation_mode=True, render_fps=60)


def run_sb3(env_id, id, model_name, sb3_model, device='cpu', iterations=10, simulation_mode=False, render_fps=32, logger: logging=None, raw_image_event=None, stop_event: Event=None):
    logger = logger or logging.getLogger(__name__)

    env = gym.make(env_id, simulation_mode=simulation_mode, render_fps=render_fps, raw_image_event=raw_image_event)

    if sb3_model == "a2c":
        model = A2C.load(
            f"./models/bop/{id}/{model_name}",
            env=env,
            device=device
        )
    elif sb3_model == "dqn":
        model = DQN.load(
            f"./models/bop/{id}/{model_name}",
            env=env,
            device=device
        )
    elif sb3_model == "ppo":
        model = PPO.load(
            f"./models/bop/{id}/{model_name}",
            env=env,
            device=device
        )

    logger.debug(iterations)
    for _ in range(iterations):
        count = 0
        # Run a test
        obs = env.reset()[0]
        env.render()
        terminated = False
        while True or stop_event and not stop_event.is_set():
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


if __name__ == "__main__":
    env_id = 'BallOnPlate-v0'
    dir = "bop/0_9"
    model_name = "best_model.zip"
    # train_sb3(env_id, dir, model="PPO", device='cpu', iterations=100, steps_per_iteration=10_000)
    # train_sb3(env_id, model_dir, tensorboard_dir, useopencl_existing_model=f"{model_dir}/{model_name}")
    run_sb3(env_id, dir, model_name, model="ppo")