import os
from gym.wrappers import monitoring
import gymnasium as gym
import numpy as np
from stable_baselines3 import A2C, PPO
from stable_baselines3.common.callbacks import EvalCallback

import v2_vacuum_robot_env

from q_table import QTable

def run_q(episodes, is_training=True, render=False):

    env = gym.make("VacuumRobot-v2", render_mode='human' if render else None)

    if (is_training):
        q_table = QTable(
            env, 
            alpha=0.1, 
            gamma=0.9, 
            epsilon=1.0, 
            epsilon_decay=0.995, 
            min_epsilon=0.1
        )
        q_table.learn(total_episodes=episodes, max_steps=None)
        q_table.save("q_table.npy")
    else:
        q_table = QTable.load("q_table.npy")
        q_table.env = env

        for i in range(episodes):
            obs, info = env.reset()
            done = False
            total_reward = 0
            while not done:
                action = q_table.predict(obs)
                obs, reward, terminated, truncated, info = env.step(action)
                total_reward += reward
                if render:
                    env.render()
                done = terminated or truncated
            print(f"Episode {i+1} finished with total reward: {total_reward}")
    
        env.close()

def train_sb3(model_dir, model_name, use_existing_model=None):
    os.makedirs(model_dir, exist_ok=True)

    env = gym.make('VacuumRobot-v2')

    # Evaluierung während des Trainings
    eval_callback = EvalCallback(
        env,
        eval_freq=10000,
        n_eval_episodes=10,
        deterministic=True,
        render=False,
        best_model_save_path=f"{model_dir}/2"
    )
    
    if use_existing_model is not None:
        model = PPO.load(
            use_existing_model,
            env,
        )
    else:
        # PPO mit angepassten Hyperparametern
        model = PPO(
            "MlpPolicy",
            env,
            verbose=1,
            learning_rate=3e-4,
            gamma=0.99,
            n_steps=256,
            batch_size=64,
            ent_coef=0.01,
            tensorboard_log="./ppo_2dgrid_log/"
        )
    
    # Training mit 500.000 Schritten
    STEPS_PER_ITERATION = 50_000

    for i in range(10):
        model.learn(
            total_timesteps=STEPS_PER_ITERATION,
            callback=eval_callback,
            progress_bar=True,
            reset_num_timesteps=False
        )
        model.save(f"{model_dir}/{model_name}")

def run_sb3(model_dir, model_name):

    env = gym.make('VacuumRobot-v2')

    model = PPO.load(
        f"{model_dir}/{model_name}",
        env=env
    )

    # Run a test
    obs = env.reset()[0]
    env.render()
    terminated = False
    while True:
        action, _ = model.predict(observation=obs, deterministic=True) # Turn on deterministic, so predict always returns the same behavior
        obs, _, terminated, _, _ = env.step(action)

        env.render()

        if terminated:
            break


if __name__ == "__main__":
    # run_q(episodes=15_000, is_training=True, render=False)
    # run_q(episodes=10, is_training=False, render=True)

    model_dir = "models"
    model_name = "vacuum_robot.ppo"
    # train_sb3(model_dir, model_name, use_existing_model=f"{model_dir}/{model_name}")

    model_dir = "models/2"
    model_name = "best_model.zip"
    run_sb3(model_dir, model_name)
    