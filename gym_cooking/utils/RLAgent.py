#import numpy as np
from stable_baselines3 import PPO
#from stable_baselines3.common.vec_env import DummyVecEnv
import time
import os

from gym_cooking.utils.CustomCallback import TrajectoryCallback


class RLAgent:
    def __init__(self, name, id_color, recipes, arglist, env):
        self.name = name
        self.color = id_color
        self.recipes = recipes
        self.arglist = arglist
        self.env = env
        #, n_steps=100, batch_size=20
        self.model = PPO("MlpPolicy", env, verbose=1, seed=self.env.arglist.seed)
        self.steps_taken = 0
        self.successful = False
        self.steps_to_success = 0

        # # Define the mapping from discrete actions to navigation actions
        # #written in utils.py
        # self.action_mapping = {
        #     0: (0, -1),   # Move up
        #     1: (0, 1),  # Move down
        #     2: (-1, 0),  # Move left
        #     3: (1, 0),   # Move right
        #     4: (0, 0),   # No-op
        # }

    # def select_action(self, obs):
    #     """
    #     Select an action based on the preprocessed observation.
    #     """
    #     # Predict the action index
    #     action_index, _ = self.model.predict(obs.game.get_image_obs(), deterministic=True)
    #
    #     # Map the action index to the corresponding navigation action
    #     navigation_action = self.action_mapping.get(action_index, (0, 0))  # Default to no-op if invalid index
    #
    #     return navigation_action

    def train(self, total_timesteps=10000):
        """
        Train the RL agent using PPO.
        """
        callback = TrajectoryCallback(self.env, total_timesteps,  trajectory_dir="misc/metrics/trajectories")
        self.model.learn(total_timesteps=total_timesteps, callback=callback)
        self.successful = callback.success_logged
        self.steps_taken += total_timesteps  # Increment steps counter
        self.steps_to_success = callback.steps_to_success

        # Save the model with a timestamp
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        save_dir = "rl_zips"
        model_path = os.path.join(save_dir, f"{self.name}_ppo_model_{timestamp}.zip")
        self.model.save(model_path)
        print(f"Model saved to {model_path}")


#TODO implement reward learning logic
