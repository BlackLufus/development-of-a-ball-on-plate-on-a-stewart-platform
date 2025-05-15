import os
from gym.wrappers import monitoring
import gymnasium as gym
import numpy as np
from stable_baselines3 import A2C, PPO
from stable_baselines3.common.callbacks import EvalCallback

import vacuum_robot.v1.environment as environment

from q_table import QTable

def run_q(episodes, is_training=True, render=False):

    env = gym.make("VacuumRobot-v1", render_mode='human' if render else None)

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

def train_sb3():
    model_dir = "models"
    os.makedirs(model_dir, exist_ok=True)

    env = gym.make('VacuumRobot-v1')

    # Evaluierung während des Trainings
    eval_callback = EvalCallback(
        env,
        eval_freq=10000,
        n_eval_episodes=10,
        deterministic=True,
        render=False
    )
    
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
    model.learn(
        total_timesteps=500_000,
        callback=eval_callback,
        progress_bar=True
    )

    # MAX_ITERATIONS = 1_000_000
    # SAVE_PER_ITERATIONS = 50_000
    # SAVE_ID = 1
    # current_iteration = 0
    # while current_iteration < MAX_ITERATIONS:
    #     current_iteration += 1

    #     model.learn(
    #         total_timesteps=SAVE_PER_ITERATIONS,
    #         callback=eval_callback,
    #         progress_bar=True
    #     )

    #     model.save(f"{model_dir}/ppo_{SAVE_ID}")
    #     SAVE_ID += 1

    model.save(f"{model_dir}/ppo_1")

def run_sb3():

    env = gym.make('VacuumRobot-v1')

    model = PPO.load(
        'models/vacuum_robot.ppo',
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

    # train_sb3()
    run_sb3()
    