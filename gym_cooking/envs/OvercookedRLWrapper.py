import json

import numpy as np
from gym import Wrapper
from gym.spaces import Box, MultiDiscrete

from gym_cooking.utils.agent import AgentRepr
import os

world_object_map = {
    'Counter': 3,
    'Floor': 4,
    'Cutboard': 5,
    'Delivery': 6,
    'Tomato': 7,
    'Lettuce': 8,
    'Plate': 9}


class OvercookedRLWrapper(Wrapper):
    def __init__(self, env):
        super().__init__(env)

        #steps limiter
        self.arg = 1000
        grid_size = env.world.width * env.world.height
        vector_length = grid_size + 3 * len(self.sim_agents)  # Each agent has 3 attributes: x, y, id
        self.observation_space = Box(low=0, high=255, shape=(vector_length,), dtype=np.uint8)
        self.action_space = MultiDiscrete([5, 5])
        self.log_file = "env_log.txt"  # File to log states and actions

        # Clear the log file at the start
        with open(self.log_file, "w") as log:
            log.write("")

        # create PDDL file based on the level name
        # parse name_of_level from arglist.level
        name_of_level = self.arglist.level.split('/')[-1]  # Extract the level name from the path
        print("Name of level is: " + name_of_level)

        # check if pddl file exists in utils/levels as name_of_level.pddl
        pddl_file_path = f"utils/pddls/{name_of_level}.pddl"
        if not os.path.exists(pddl_file_path):
            print(f"PDDL file for {name_of_level} does not exist. Creating a new one.")
            with open(pddl_file_path, 'w') as pddl_file:
                pddl_file.write(f"; PDDL file for {name_of_level}\n")
                state = self._process_observation(self.env.get_repr(), self.env.world.get_object_list())
                state_to_pddl(self, state, name_of_level,  self.env.world.width, self.env.world.height, pddl_file_path)
        else:
            print(f"PDDL file for {name_of_level} already exists.")





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
        vector_length = grid_size + len(self.sim_agents) * 3

        #print(obs_repr)
        #print(world_objects)

        # Initialize the vector
        vector = np.zeros(vector_length, dtype=np.uint8)

        # Step 1: Encode world and objects
        for obj in world_objects:
            x, y = obj.location
            index = x * self.env.world.width + y
            vector[index] = world_object_map.get(obj.name, -1)  # Use the mapping to encode the object type

        # Step 2: Encode only agents
        offset = grid_size
        for obj_group in obs_repr:
            if isinstance(obj_group, AgentRepr):
                x, y = obj_group.location
                vector[offset] = x  # X-coordinate
                vector[offset + 1] = y  # Y-coordinate
                if obj_group.name == 'agent-1':
                    vector[offset + 2] = 1
                else:
                    vector[offset + 2] = 2
                offset += 3
        print("this is the vector" + "\n" + str(vector))
        return vector

def state_to_pddl(self, state, name_of_level,  world_width, world_height, pddl_file_path):
    """
    Translates the state vector into a PDDL file.

    Args:
        state: The state vector representing the world.
        world_width: Width of the grid world.
        world_height: Height of the grid world.
        pddl_file_path: Path to save the generated PDDL file.
    """
    with open(pddl_file_path, 'w') as pddl_file:
        # Write PDDL header
        pddl_file.write("; PDDL file for " + name_of_level + "\n")
        pddl_file.write("(define (problem " + name_of_level + ")\n")
        pddl_file.write("(:domain grid_overcooked)\n")

        # grid cells
        pddl_file.write("(:objects\n")
        for x in range(world_width):
            for y in range(world_height):
                pddl_file.write(f"    x{x}y{y} - cell\n")

        pddl_file.write("    a1 - agent\n")
        pddl_file.write("    a2 - agent\n")
        pddl_file.write("    p1 - object\n")
        pddl_file.write("    p2 - object\n")
        pddl_file.write("    l1 - object\n")
        pddl_file.write("    t1 - object\n")
        pddl_file.write(")\n\n")


        # Define initial state
        pddl_file.write("(:init\n")

        # add grid and objects
        grid_size = world_width * world_height
        for i in range(grid_size):
            x, y = divmod(i, world_width)
            if state[i] == world_object_map['Floor']:
                pddl_file.write(f"    (is_floor x{x}y{y})\n")
            elif state[i] == world_object_map['Cutboard']:
                pddl_file.write(f"    (is_cutting_board x{x}y{y})\n")
            elif state[i] == world_object_map['Delivery']:
                pddl_file.write(f"    (delivery_spot x{x}y{y})\n")
            elif state[i] > world_object_map['Delivery']:
                # go over map find key that matches the value of state[i]
                flag_p = True
                for key, value in world_object_map.items():
                    if value == state[i]:
                        if key.lower() == 'plate' and flag_p:
                            # If it's a plate, we need to add the second plate assuming there are two plates
                            pddl_file.write(f"    (object_at {key.lower()[0]}{2} x{x}y{y})\n")
                            pddl_file.write(f"    (occupied x{x}y{y})\n")
                            pddl_file.write(f"    ({key.lower()} {key.lower()[0]}{2})\n")
                            flag_p = False
                            continue
                        pddl_file.write(f"    (object_at {key.lower()[0]}{1} x{x}y{y})\n")
                        pddl_file.write(f"    (occupied x{x}y{y})\n")
                        pddl_file.write(f"    ({key.lower()} {key.lower()[0]}{1})\n")



        # add agents
        offset = grid_size
        #todo fix agent starting locations and all other automation of problems according to new pddl
        for i in range(2):  # Assuming 2 agents
            x, y, num = state[offset], state[offset + 1], state[offset + 2]
            pddl_file.write(f"    (agent_at a{num} x{x}y{y})\n")
            pddl_file.write(f"    (holding_nothing a{num})\n")
            offset += 3

        # adjacency predicates
        for x in range(world_width):
            for y in range(world_height):
                if x + 1 < world_width:
                    pddl_file.write(f"    (adjacent x{x}y{y} x{x + 1}y{y})\n")
                    pddl_file.write(f"    (adjacent x{x + 1}y{y} x{x}y{y})\n")
                if y + 1 < world_height:
                    pddl_file.write(f"    (adjacent x{x}y{y} x{x}y{y + 1})\n")
                    pddl_file.write(f"    (adjacent x{x}y{y + 1} x{x}y{y})\n")

        pddl_file.write(")\n\n")

        # Define goal

        # Define goal
        pddl_file.write("(:goal\n")
        if "tomato" in name_of_level:
            pddl_file.write("   (or\n")
            pddl_file.write("        (and (delivered t1)\n")
            pddl_file.write("             (tomato t1)\n")
            pddl_file.write("             (plate t1)\n")
            pddl_file.write("             (chopped t1))\n")
            pddl_file.write("        (and (delivered p1)\n")
            pddl_file.write("             (tomato p1)\n")
            pddl_file.write("             (plate p1)\n")
            pddl_file.write("             (chopped p1))\n")
            pddl_file.write("        (and (delivered p2)\n")
            pddl_file.write("             (tomato p2)\n")
            pddl_file.write("             (plate p2)\n")
            pddl_file.write("             (chopped p2))\n")
        elif "salad" in name_of_level:
            pddl_file.write("   (or\n")
            pddl_file.write("        (and (delivered t1)\n")
            pddl_file.write("             (tomato t1)\n")
            pddl_file.write("             (plate t1)\n")
            pddl_file.write("             (chopped t1)\n")
            pddl_file.write("             (lettuce t1))\n")
            pddl_file.write("        (and (delivered p1)\n")
            pddl_file.write("             (tomato p1)\n")
            pddl_file.write("             (plate p1)\n")
            pddl_file.write("             (chopped p1)\n")
            pddl_file.write("             (lettuce p1))\n")
            pddl_file.write("        (and (delivered p2)\n")
            pddl_file.write("             (tomato p2)\n")
            pddl_file.write("             (plate p2)\n")
            pddl_file.write("             (chopped p2)\n")
            pddl_file.write("             (lettuce p2))\n")
            pddl_file.write("        (and (delivered l1)\n")
            pddl_file.write("             (lettuce l1)\n")
            pddl_file.write("             (lettuce l1)\n")
            pddl_file.write("             (plate l1)\n")
            pddl_file.write("             (chopped l1))\n")
        elif "tl" in name_of_level:
            pddl_file.write("        (and \n")
            pddl_file.write("             (or \n")
            pddl_file.write("                 (and \n")
            pddl_file.write("                     (delivered t1)\n")
            pddl_file.write("                     (tomato t1)\n")
            pddl_file.write("                     (plate t1)\n")
            pddl_file.write("                     (chopped t1)\n")
            pddl_file.write("                 )\n")
            pddl_file.write("                 (and \n")
            pddl_file.write("                     (delivered p1)\n")
            pddl_file.write("                     (tomato p1)\n")
            pddl_file.write("                     (plate p1)\n")
            pddl_file.write("                     (chopped p1)\n")
            pddl_file.write("                 )\n")
            pddl_file.write("                 (and \n")
            pddl_file.write("                     (delivered p2)\n")
            pddl_file.write("                     (tomato p2)\n")
            pddl_file.write("                     (plate p2)\n")
            pddl_file.write("                     (chopped p2)\n")
            pddl_file.write("                 )\n")
            pddl_file.write("             )\n")
            pddl_file.write("             (or \n")
            pddl_file.write("                 (and \n")
            pddl_file.write("                     (delivered p1)\n")
            pddl_file.write("                     (lettuce p1)\n")
            pddl_file.write("                     (plate p1)\n")
            pddl_file.write("                     (chopped p1)\n")
            pddl_file.write("                 )\n")
            pddl_file.write("                 (and \n")
            pddl_file.write("                     (delivered p2)\n")
            pddl_file.write("                     (lettuce p2)\n")
            pddl_file.write("                     (plate p2)\n")
            pddl_file.write("                     (chopped p2)\n")
            pddl_file.write("                 )\n")
            pddl_file.write("                 (and \n")
            pddl_file.write("                     (delivered l1)\n")
            pddl_file.write("                     (lettuce l1)\n")
            pddl_file.write("                     (plate l1)\n")
            pddl_file.write("                     (chopped l1)\n")
            pddl_file.write("                 )\n")
            pddl_file.write("             )\n")
        pddl_file.write("   )\n") #first or/and
        pddl_file.write(")\n") # goal
        pddl_file.write(")\n") # end of define
