import json

import numpy as np
from gym import Wrapper
from gym.spaces import Box, MultiDiscrete

from gym_cooking.utils.agent import AgentRepr


class OvercookedRLWrapper(Wrapper):
    def __init__(self, env):
        super().__init__(env)

        grid_size = env.world.width * env.world.height
        repr = self.env.get_repr()
        numb_holdable_objects = sum(len(obj_group) if (isinstance(obj_group, tuple) and not isinstance(obj_group, AgentRepr)) else 1 for obj_group in repr)
        vector_length = grid_size + 3 * numb_holdable_objects
        self.observation_space = Box(low=0, high=255, shape=(vector_length,), dtype=np.uint8)
        self.action_space = MultiDiscrete([5, 5])
        self.log_file = "env_log.txt"  # File to log states and actions

        # Clear the log file at the start
        with open(self.log_file, "w") as log:
            log.write("")


    def reset(self):
        # Call the original environment's reset method
        obs = self.env.reset()
        return self._process_observation(self.env.get_repr(), self.env.world.get_object_list())

    def step(self, action_arr):

        # Log the current state before the action
        state = self._process_observation(self.env.get_repr(), self.env.world.get_object_list())
        with open(self.log_file, "a") as log:
            log.write("State:\n")
            log.write(np.array2string(state) + "\n")  # Write the state as a raw array


        # Call the original environment's step method
        action_mapping = {
            0: (0, -1),  # Move up
            1: (0, 1),  # Move down
            2: (-1, 0),  # Move left
            3: (1, 0),  # Move right
            4: (0, 0),  # No-op
        }
        action_dict = {}
        action_dict["agent-1"] = action_mapping[action_arr[0]]
        action_dict["agent-2"] = action_mapping[action_arr[1]]

        with open(self.log_file, "a") as log:
            log.write("Actions:\n")
            log.write(json.dumps(action_dict) + "\n")

        obs, reward, done, info = self.env.step(action_dict)
        if 'obs' in info:
            del info['obs']

        return state, reward, done, info

    def _process_observation(self, obs_repr, world_objects):
        # Dynamically calculate vector length
        grid_size = self.env.world.width * self.env.world.height
        num_objects = sum(len(obj_group) if (isinstance(obj_group, tuple) and not isinstance(obj_group, AgentRepr)) else 1 for obj_group in obs_repr)
        vector_length = grid_size + num_objects * 3

        # Initialize the vector
        vector = np.zeros(vector_length, dtype=np.uint8)

        # Step 1: Encode world objects
        for obj in world_objects:
            x, y = obj.location
            index = x * self.env.world.width + y
            vector[index] = hash(obj.name) % 256  # Encode object name

        # Step 2: Encode get_repr objects
        offset = grid_size
        for obj_group in obs_repr:
            if isinstance(obj_group, AgentRepr):
                x, y = obj_group.location
                vector[offset] = x  # X-coordinate
                vector[offset + 1] = y  # Y-coordinate
                if obj_group.holding == 'None':
                    vector[offset + 2] = 0
                else:
                    vector[offset + 2] = hash(obj_group.holding) % 256 if obj_group.holding != 'None' else 0
                offset += 3
            else:
                for obj in obj_group:
                    x, y = obj.location
                    vector[offset] = x  # X-coordinate
                    vector[offset + 1] = y  # Y-coordinate
                    vector[offset + 2] = int(obj.is_held)  # Held status
                    offset += 3
        print("this is the vector" + "\n" + str(vector))
        return vector
