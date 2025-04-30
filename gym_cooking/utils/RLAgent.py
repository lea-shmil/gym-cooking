import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv

class RLAgent:
    def __init__(self, name, id_color, recipes, arglist, env):
        self.name = name
        self.color = id_color
        self.recipes = recipes
        self.arglist = arglist
        self.vec_env = DummyVecEnv([lambda: env])
        self.model = PPO("MlpPolicy", self.vec_env, verbose=1)

        # Define the mapping from discrete actions to navigation actions
        #written in utils.py
        self.action_mapping = {
            0: (0, -1),   # Move up
            1: (0, 1),  # Move down
            2: (-1, 0),  # Move left
            3: (1, 0),   # Move right
            4: (0, 0),   # No-op
        }

    def select_action(self, obs):
        """
        Select an action based on the preprocessed observation.
        """
        # Predict the action index
        action_index, _ = self.model.predict(obs.game.get_image_obs(), deterministic=True)

        # Map the action index to the corresponding navigation action
        navigation_action = self.action_mapping.get(action_index, (0, 0))  # Default to no-op if invalid index

        return navigation_action

    def train(self, total_timesteps=10000):
        """
        Train the RL agent using PPO.
        """
        # Use the environment to collect training data

        self.model.learn(total_timesteps=total_timesteps)
        self.model.save(f"{self.name}_ppo_model")  # Save the model after training


#TODO implement reward learning logic
