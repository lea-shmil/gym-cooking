import numpy as np
from gym import Wrapper
from gym.spaces import Box, Discrete

class OvercookedRLWrapper(Wrapper):
    def __init__(self, env):
        super().__init__(env)

        # verified this is the correct observation space
        self.observation_space = Box(low=0, high=255, shape=(560, 560, 3), dtype=np.uint8)
        self.action_space = Discrete(4)

    def reset(self):
        # Call the original environment's reset method
        obs = self.env.reset()
        return self._process_observation(obs)

    def step(self, action_dict):
        # Call the original environment's step method
        print("step from the wrapper was called")
        obs, reward, done, info = self.env.step(action_dict)
        return self._process_observation(obs), reward, done, info

    def _process_observation(self, obs):
        # observation to the required format
        return self.env.game.get_image_obs()  # Image-based observation
