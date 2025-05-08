import os
import time
import gymnasium as gym
import numpy as np
from stable_baselines3 import A2C, DQN, PPO
from stable_baselines3.common.callbacks import EvalCallback

from stewart_platform.reinforcement_learning.ball_on_plate import v0_ball_on_plate_env

def train_sb3(env_id, dir, model="PPO", use_existing_model=None, device='cpu'):
    os.makedirs(f"./models/{dir}", exist_ok=True)

    env = gym.make(env_id)

    # Evaluierung während des Trainings
    eval_callback = EvalCallback(
        env,
        eval_freq=10000,
        n_eval_episodes=10,
        deterministic=True,
        render=False,
        best_model_save_path=f"./models/{dir}"
    )

    if model == "A2C":
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
                tensorboard_log=f"./tensorboard/{dir}",
                device=device
            )
    elif model == "DQN":
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
                tensorboard_log=f"./tensorboard/{dir}",
                device=device
            )
    # PPO mit angepassten Hyperparametern
    elif model == "PPO":
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
                tensorboard_log=f"./tensorboard/{dir}",
                device=device
            )
    
    # Training mit 500.000 Schritten
    STEPS_PER_ITERATION = 5_000

    for _ in range(40):
        model.learn(
            total_timesteps=STEPS_PER_ITERATION,
            callback=eval_callback,
            progress_bar=True,
            reset_num_timesteps=False
        )

        model.save(f"./models/{dir}/{model_name}")

        run_sb3(env_id, dir, model_name, model="PPO", episods=1)

def run_sb3(env_id, dir, model_name, model="PPO", episods=10):

    env = gym.make(env_id, simulation_mode=False)

    if model == "A2C":
        model = A2C.load(
            f"./models/{dir}/{model_name}",
            env=env
        )
    elif model == "DQN":
        model = DQN.load(
            f"./models/{dir}/{model_name}",
            env=env
        )
    elif model == "PPO":
        model = PPO.load(
            f"./models/{dir}/{model_name}",
            env=env
        )

    for _ in range(episods):
        count = 0
        # Run a test
        obs = env.reset()[0]
        env.render()
        terminated = False
        while True:
            count += 1
            action, _ = model.predict(observation=obs, deterministic=True) # Turn on deterministic, so predict always returns the same behavior
            obs, _, terminated, truncated, _ = env.step(action)

            env.render()

            if terminated or truncated:
                if terminated:
                    print(f"Success (count: {count})")
                else:
                    print(f"Failed (count: {count})")
                break


if __name__ == "__main__":
    env_id = 'BallOnPlate-v0'
    dir = "bop/0_9"
    model_name = "best_model.zip"
    train_sb3(env_id, dir, model="PPO", device='auto')
    # train_sb3(env_id, model_dir, tensorboard_dir, useopencl_existing_model=f"{model_dir}/{model_name}")
    # run_sb3(env_id, dir, model_name, model="PPO")