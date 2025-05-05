import numpy as np
from gym import Wrapper
from gym.spaces import Box, MultiDiscrete

class OvercookedRLWrapper(Wrapper):
    def __init__(self, env):
        super().__init__(env)

        # verified this is the correct observation space
        self.observation_space = Box(low=0, high=255, shape=(560, 560, 3), dtype=np.uint8)
        self.action_space = MultiDiscrete([5,5])

    def reset(self):
        # Call the original environment's reset method
        obs = self.env.reset()
        return self._process_observation(obs)

    def step(self, action_arr):
        # Call the original environment's step method
        action_mapping = {
            0: (0, -1),   # Move up
            1: (0, 1),  # Move down
            2: (-1, 0),  # Move left
            3: (1, 0),   # Move right
            4: (0, 0),   # No-op
        }
        action_dict = {}
        action_dict["agent-1"] = action_mapping[action_arr[0]]
        action_dict["agent-2"] = action_mapping[action_arr[1]]

        obs, reward, done, info = self.env.step(action_dict)

        if "obs" in info:
            del info["obs"]

        return self._process_observation(obs), reward, done, info

    def _process_observation(self, obs):
        # observation to the required format
        return self.env.game.get_image_obs()  # Image-based observation
