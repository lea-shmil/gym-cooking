import numpy as np
from stable_baselines3 import PPO

class RLAgent:
    def __init__(self, name, id_color, recipes, arglist, env):
        self.name = name
        self.color = id_color
        self.recipes = recipes
        self.arglist = arglist
        self.model = PPO("MlpPolicy", env, verbose=1)

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

#TODO implement reward learning logic
#TODO check if reward contains proper rewards to learn both movement and cooking