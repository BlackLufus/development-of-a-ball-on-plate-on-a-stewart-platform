import random
import time
import numpy as np
import gymnasium as gym


class QTable:
    """
    A class implementing the Q-learning algorithm for reinforcement learning.
    This class is designed to work with a discrete action space and a discrete state space.
    It uses a Q-table to store the Q-values for each state-action pair.
    """

    def __init__(self, env: gym.Env, alpha=0.1, gamma=0.95, epsilon=1.0, epsilon_decay=0.995, min_epsilon=0.01):
        """
        Initializes the Q-table and sets hyperparameters.

        :param env: The environment to train on.
        :param alpha: Learning rate.
        :param gamma: Discount factor.
        :param epsilon: Exploration rate.
        :param epsilon_decay: Decay rate for exploration.
        :param min_epsilon: Minimum exploration rate.
        """
        # Initialize the Q-table with zeros
        self.env = env
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.min_epsilon = min_epsilon
        if env is not None:
            # Check if environment has discrete observation space
            if isinstance(env.observation_space, gym.spaces.Discrete):
                n_states = env.observation_space.n
                self.q_table = np.zeros((n_states, env.action_space.n))
            
            # Check if environment has Box (continuous) observation space
            elif isinstance(env.observation_space, gym.spaces.Box):
                # Get the shape of the observation space
                obs_shape = env.observation_space.shape[0]  # Should be 4 for [robot_x, robot_y, target_x, target_y]
                print(f"Observation space shape: {obs_shape}")
                
                # Get the bounds of each dimension
                low = env.observation_space.low
                high = env.observation_space.high
                print(high, low)
                
                # Create Q-table with correct dimensions based on observation bounds
                dims = []
                for i in range(obs_shape):
                    dim_size = int(high[i] - low[i] + 1)
                    dims.append(dim_size)
                
                # Add action dimension
                dims.append(env.action_space.n)
                
                # Initialize Q-table with all dimensions
                self.q_table = np.zeros(tuple(dims))
            else:
                raise ValueError(f"Unsupported observation space type: {type(env.observation_space)}")

    def _choose_action(self, state):
        """
        Returns the action with the highest Q-value for the given state.
        """
        # Epsilon-greedy action selection
        if random.uniform(0, 1) < self.epsilon:
            # Choose a random action (exploration)
            return self.env.action_space.sample()
        else:
            q_state_idx = tuple(state)
            # Choose the action with the highest Q-value for the current state
            return np.argmax(self.q_table[q_state_idx])
    
    def learn(self, total_episodes=100_000, max_steps=250):
        """
        Trains the Q-table using Q-learning algorithm.
        """
        iterations = 0
        done_count = 0
        total_steps = 0
        total_rewards = 0

        period_iterations = 0
        period_done_count = 0
        period_steps = 0
        period_rewards = 0

        # Loop through the number of episodes
        for episode in range(total_episodes):
            step = 0
            iterations += 1
            period_iterations += 1

            # Reset the environment for a new episode
            state, _ = self.env.reset()

            terminated = False

            # Loop through the maximum number of steps in the episode
            while not terminated and (max_steps is None or step < max_steps):
                step += 1
                total_steps += 1
                period_steps += 1

                # Choose an action based on the current state
                action = self._choose_action(state)
                # print(f"Episode: {episode}, Step: {step}, State: {state}, Action: {action}")

                # Take the action and observe the new state and reward
                new_state, reward, terminated, truncate, _ = self.env.step(action)

                q_state_action_idx = tuple(state) + (action,)
                q_new_state_idx = tuple(new_state)
                
                state = new_state
                total_rewards += reward
                period_rewards += reward
                
                # if episode % 1000 == 0:
                #     self.env.render()
                #     print(f"Episode: {episode}, Step: {step}, State: {state}, Action: {action}, Reward: {reward}, New State: {new_state}, Done: {done}")
                #     time.sleep(0.15)

                # Q-Learning Update
                old_value = self.q_table[q_state_action_idx]
                next_max = np.max(self.q_table[q_new_state_idx])
                new_value = (1 - self.alpha) * old_value + self.alpha * (reward + self.gamma * next_max)
                self.q_table[q_state_action_idx] = new_value

                if terminated:
                    done_count += 1
                    period_done_count += 1
                    break

            # Decay the exploration rate
            if self.epsilon_decay is not None:
                self.epsilon = max(self.min_epsilon, self.epsilon * self.epsilon_decay)
            else:
                epsilon = max(epsilon - 1/total_episodes, 0)  # Linear decay
            
            if episode % 1000 == 0:
                print("--------------------------")
                print(f"Episode {episode} of {total_episodes} completed. Current epsilon: {self.epsilon:.4f}")
                print("----------")
                print(f"Steps_mean: {total_steps / iterations:.2f}, Rewards_mean: {total_rewards / iterations:.2f}, Success_rate: {done_count / iterations:.2f}")
                print("----------")
                print(f"Period: {period_iterations}")
                print(f"Steps_mean: {period_steps / period_iterations:.2f}, Rewards_mean: {period_rewards / period_iterations:.2f}, Success_rate: {period_done_count / period_iterations:.2f}")
                print("--------------------------")
                period_iterations = 0
                period_done_count = 0
                period_steps = 0
                period_rewards = 0
            
            self.env.close()

    
    def predict(self, state):
        """
        Predicts the best action for the given state based on the Q-table.
        """
        q_state_idx = tuple(state)
        return np.argmax(self.q_table[q_state_idx])
    
    def save(self, filename):
        """
        Saves the Q-table to a file.
        """
        # Variable to store the Q-table
        q_table_metadata = {
            "q_table": self.q_table,
            "alpha": self.alpha,
            "gamma": self.gamma,
            "epsilon": self.epsilon,
            "epsilon_decay": self.epsilon_decay,
            "min_epsilon": self.min_epsilon
        }
        # Save the Q-table to a file
        np.save(filename, q_table_metadata)
        print(f"Q-table saved to {filename}")
    
    def load(filename):
        """
        Loads the Q-table from a file.
        """
        model = QTable(env=None)
        q_table_metadata = np.load(filename, allow_pickle=True).item()
        model.q_table = q_table_metadata["q_table"]
        model.alpha = q_table_metadata["alpha"]
        model.gamma = q_table_metadata["gamma"]
        model.epsilon = q_table_metadata["epsilon"]
        model.epsilon_decay = q_table_metadata["epsilon_decay"]
        model.min_epsilon = q_table_metadata["min_epsilon"]
        print(f"Q-table loaded from {filename}")
        return model
    