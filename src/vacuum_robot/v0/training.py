# https://www.youtube.com/watch?app=desktop&v=AoGRjPt-vms
# https://github.com/johnnycode8/gym_custom_env
# The example has been adapted to the environment of a vacuum robot

import gymnasium as gym
import numpy as np

import vacuum_robot.v0.environment as environment

from q_table import QTable

def run_q(episodes, is_training=True, render=False):

    env = gym.make("VacuumRobot-v0", render_mode='human' if render else None)

    if (is_training):
        q_table = QTable(
            env, 
            alpha=0.9, 
            gamma=0.9, 
            epsilon=1.0, 
            epsilon_decay=0.995, 
            min_epsilon=0.1
        )
        q_table.learn(total_episodes=episodes, max_steps=1000)
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



if __name__ == "__main__":
    run_q(episodes=10_000, is_training=True, render=False)
    run_q(episodes=10, is_training=False, render=True)
    