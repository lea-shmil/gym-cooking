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

AGENT_PROPERTIES = 3
OBJECT_PROPERTIES = 7

action_mapping = {
    0: (0, -1),  # Move up
    1: (0, 1),  # Move down
    2: (-1, 0),  # Move left
    3: (1, 0),  # Move right
    4: (0, 0),  # No-op
}

pddl_name = {
    1: 't1',
    2: 'l1',
    3: 'p1',
    4: 'p2',
}

# Check destination tile type
tile_type = {
    3: "counter",
    4: "floor",
    5: "cutboard",
    6: "delivery",
    7: "tomato",
    8: "lettuce",
    9: "plate"
}


class OvercookedRLWrapper(Wrapper):
    def __init__(self, env):
        super().__init__(env)

        grid_size = env.world.width * env.world.height
        objects = [obj[1] for obj in self.world.objects.items() if obj[0] in ["Tomato", "Lettuce", "Plate"]]
        object_size = sum(len(obj) for obj in objects)  # Calculate the size of the object representation
        vector_length = grid_size + AGENT_PROPERTIES * len(self.sim_agents) + object_size * OBJECT_PROPERTIES
        # Each agent has 3 attributes: x, y, id
        #  each object statuses (itemname, tomato, lettuce, plate, chopped, x, y)
        self.observation_space = Box(low=0, high=255, shape=(vector_length,), dtype=np.uint8)
        self.action_space = MultiDiscrete([5, 5])
        self.log_file = "env_log.txt"  # File to log states and actions
        self.vector = self._process_observation(self.env.get_repr(), self.env.world.get_object_list())
        self.no_op = 0

        # Clear the log file at the start
        with open(self.log_file, "w") as log:
            log.write("")

        # create PDDL file based on the level name
        # parse name_of_level from arglist.level
        name_of_level = self.arglist.level.split('/')[-1]  # Extract the level name from the path

        # check if pddl file exists in utils/levels as name_of_level.pddl
        pddl_file_path = f"utils/pddls/{name_of_level}.pddl"
        if not os.path.exists(pddl_file_path):
            print(f"PDDL file for {name_of_level} does not exist. Creating a new one.")
            with open(pddl_file_path, 'w') as pddl_file:
                pddl_file.write(f"; PDDL file for {name_of_level}\n")
                self.state_to_pddl(self.vector, name_of_level, self.env.world.width, self.env.world.height,
                                   pddl_file_path)
        else:
            print(f"PDDL file for {name_of_level} already exists.")

        # Create a filename for the trajectory file
        # Ensure the directory exists
        trajectory_dir = 'misc/metrics/trajectories/'
        os.makedirs(trajectory_dir, exist_ok=True)

        # Open the file for writing
        with open(f'{trajectory_dir}{self.filename}.trajectory', 'w') as f:
            f.write('(  (:init')  # Initialize the file
            get_state(f, self.vector, self.env.world.width, self.env.world.height)

    def reset(self):
        # Call the original environment's reset method
        obs = self.env.reset()
        self.vector = self._process_observation(self.env.get_repr(), self.env.world.get_object_list())
        return self.vector

    def step(self, action_arr):

        # Call the original environment's step method
        action_dict = {}
        action_dict["agent-1"] = action_mapping[action_arr[0]]
        action_dict["agent-2"] = action_mapping[action_arr[1]]

        with open(self.log_file, "a") as log:
            log.write("State:\n")
            log.write(np.array2string(self.vector) + "\n")  # Write the state as a raw array

        with open(self.log_file, "a") as log:
            log.write("Actions:\n")
            log.write(json.dumps(action_dict) + "\n")

        with open(f'misc/metrics/trajectories/{self.filename}.trajectory', 'a') as f:
            if self.no_op < 2:
                f.write('(operators: ')
                f.flush()
            self.get_parameters(f, action_dict, self.env.world.width, self.env.world.height)
            f.flush()
            if self.no_op < 2:
                f.flush()
                f.write(')\n')  # Close the operators list
                f.write('(:state ')
                get_state(f, self.vector, self.env.world.width, self.env.world.height)

        obs, reward, done, info = self.env.step(action_dict)
        if 'obs' in info:
            del info['obs']

        return self.vector, reward, done, info

    def _process_observation(self, obs_repr, world_objects):
        # Dynamically calculate vector length
        grid_size = self.env.world.width * self.env.world.height
        moving_objects, static_objects = [], []  # Separate lists for moving and static objects
        for obj in world_objects:
            if obj.name in ['Counter', 'Floor', 'Cutboard', 'Delivery']:
                static_objects.append(obj)
            else:
                moving_objects.append(obj)

        vector_length = grid_size + len(self.sim_agents) * AGENT_PROPERTIES + len(moving_objects) * OBJECT_PROPERTIES

        # Initialize the vector
        vector = np.zeros(vector_length, dtype=np.uint8)

        # Step 1: Encode static world
        for obj in static_objects:
            x, y = obj.location
            index = x * self.env.world.width + y
            vector[index] = world_object_map.get(obj.name, -1)  # Use the mapping to encode the object type

        # Step 2: Encode only agents
        offset = grid_size - 1
        for obj_group in obs_repr:
            if isinstance(obj_group, AgentRepr):
                x, y = obj_group.location
                vector[offset] = x  # X-coordinate
                vector[offset + 1] = y  # Y-coordinate
                if obj_group.name == 'agent-1':
                    vector[offset + 2] = 1
                else:
                    vector[offset + 2] = 2
                offset += AGENT_PROPERTIES

        plate_flag = False
        # Step 3: Encode moving objects
        for obj in moving_objects:
            x, y = obj.location
            name = world_object_map.get(obj.name, -1)
            if obj.name == 'Tomato':
                vector[offset] = 1
                vector[offset + 1] = 1
            elif obj.name == 'Lettuce':
                vector[offset] = 2
                vector[offset + 2] = 1
            elif obj.name == 'Plate' and not plate_flag:
                vector[offset] = 3
                vector[offset + 3] = 1
            else:  # second plate
                vector[offset] = 4
                vector[offset + 3] = 2
            vector[offset + 5] = x
            vector[offset + 6] = y
            offset += OBJECT_PROPERTIES
        return vector

    def state_to_pddl(self, state, name_of_level, world_width, world_height, pddl_file_path):
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
            get_state(pddl_file, state, world_width, world_height)

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
                pddl_file.write("             (tomato l1)\n")
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
            pddl_file.write("   )\n")  # first or/and
            pddl_file.write(")\n")  # goal
            pddl_file.write(")\n")  # end of define

    def get_parameters(self, f, action_dict, width, height):
        no_op = 0
        offset = width * height - 1
        object_offset = offset + AGENT_PROPERTIES * len(action_dict)  # Start after the grid and agent properties
        agent_keys = ["agent-1", "agent-2"]

        for a, agent_key in enumerate(agent_keys):
            x_start = self.vector[offset]
            y_start = self.vector[offset + 1]
            start_loc = f"x{x_start}y{y_start}"
            x_end = self.vector[offset] + action_dict[agent_key][0]
            y_end = self.vector[offset + 1] + action_dict[agent_key][1]
            end_loc = f"x{x_end}y{y_end}"
            OBJECTS_AT = 5
            dest = self.vector[x_end * width + y_end]
            dest_tile = tile_type.get(dest, "unknown")
            object_dest = -1
            object_held = -1
            PLATE = 2
            CHOP = 1
            for i in range(object_offset + OBJECTS_AT, len(self.vector), OBJECT_PROPERTIES):
                if self.vector[i] == x_start and self.vector[i + 1] == y_start and self.vector[i - OBJECTS_AT] \
                        in pddl_name:
                    object_held = i
                if self.vector[i] == x_end and self.vector[i + 1] == y_end and self.vector[i - OBJECTS_AT] in pddl_name:
                    object_dest = i
                i += OBJECT_PROPERTIES  # Move to the next object in the vector
            action = ""

            # Floor and no other agent blocking
            if dest_tile == "floor" and x_end != self.vector[offset + 3 - a * 6] and y_end != self.vector[
                offset + 3 + 1 - a * 6]:
                action = "move"
                f.write(f"    ({action} a{a + 1} {start_loc} {end_loc})\n")
                f.flush()
                self.vector[offset] = x_end
                self.vector[offset + 1] = y_end
                if object_held != -1:  # If the agent is holding an object, update its position
                    self.vector[object_held] = x_end
                    self.vector[object_held + 1] = y_end
            # need to check if there is an object location in dests location currently
            elif object_dest != -1 and object_held == -1:
                action = "pickup"
                item = pddl_name[self.vector[object_dest - OBJECTS_AT]]
                # Remove the object from the destination tile
                self.vector[object_dest] = x_start
                self.vector[object_dest + 1] = y_start
            # utboard need to check if agent is holding non plate non chopped object and that chopping board is not occuppied by an object
            elif dest_tile == "cutboard" and object_dest == -1 and object_held != -1 and self.vector[
                object_held - CHOP] == 0 and self.vector[object_held - PLATE] == 0:
                action = "chop"
                item = pddl_name[self.vector[object_held - OBJECTS_AT]]
                self.vector[object_held - 1] = 1  # Mark the object as chopped
            # Delivery need to check if agent is holding a plate with a chopped object
            elif dest_tile == "deliver" and object_held != -1 and self.vector[object_held - PLATE] != 0 and self.vector[
                object_held - CHOP] == 1:
                action = "deliver"
                item = pddl_name[self.vector[object_held - OBJECTS_AT]]
                self.vector[object_held] = -1
                self.vector[object_held + 1] = -1
            # need to check if agent is holding something and counter is empty or its a chopping board and agent is holding a plate or a chopped object
            elif object_dest == -1 and object_held != -1 and (
                    dest_tile == "counter" or (dest_tile == "cutboard" and self.vector[object_held - CHOP] == 1)):
                action = "put-down"
                item = pddl_name[self.vector[object_held - OBJECTS_AT]]
                self.vector[object_held] = x_end
                self.vector[object_held + 1] = y_end
            # merge plate i am holding the merged result
            elif object_held != -1 and object_dest != -1 and \
                    ((self.vector[object_held - PLATE] != 0 and self.vector[object_dest - CHOP] == 1) or
                     (self.vector[object_held - CHOP] == 1 and self.vector[object_dest - PLATE] != 0)):
                action = "merge"
                item = pddl_name[self.vector[object_held - OBJECTS_AT]]
                self.vector[object_dest] = -1
                self.vector[object_dest + 1] = -1
                self.vector[object_held - PLATE] = max(self.vector[object_held - PLATE],
                                                       self.vector[object_dest - PLATE])
                self.vector[object_held - CHOP] = max(self.vector[object_held - CHOP], self.vector[object_dest - CHOP])
                self.vector[object_held - 3] = max(self.vector[object_held - 3],
                                                   self.vector[object_dest - 3])  # lettuce
                self.vector[object_held - 4] = max(self.vector[object_held - 4], self.vector[object_dest - 4])  # tomato
            else:
                no_op += 1
                self.no_op = no_op
                offset += 3
                continue

            if dest_tile != "floor":
                f.write(f"    ({action} a{a + 1} {start_loc} {end_loc} {item})\n")
                f.flush()
            offset += 3
        self.no_op = no_op


def get_state(pddl_file, state, world_width, world_height):
    # add grid and objects
    grid_size = world_width * world_height

    # add agents
    offset = grid_size - 1
    agent_locs = {}
    for i in range(2):  # Assuming 2 agents
        x, y, num = state[offset], state[offset + 1], state[offset + 2]
        pddl_file.write(f"    (agent_at a{num} x{x}y{y})\n")
        pddl_file.write(f"    (holding_nothing a{num})\n")
        pddl_file.write(f"    (occupied x{x}y{y})\n")
        offset += 3
        agent_locs[f'a{num}'] = (x, y)  # Store agent locations for later use
    #
    flag_p = True
    for i in range(grid_size):
        x, y = divmod(i, world_width)
        if state[i] == world_object_map['Floor']:
            pddl_file.write(f"    (is_floor x{x}y{y})\n")
            # not occupied if agents are not on the floor
            if not any(agent_loc == (x, y) for agent_loc in agent_locs.values()):
                pddl_file.write(f"    (not (occupied x{x}y{y}))\n")
        elif state[i] == world_object_map['Cutboard']:
            pddl_file.write(f"    (is_cutting_board x{x}y{y})\n")
        elif state[i] == world_object_map['Delivery']:
            pddl_file.write(f"    (delivery_spot x{x}y{y})\n")
        elif state[i] > world_object_map['Delivery']:
            # go over map find key that matches the value of state[i]
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
