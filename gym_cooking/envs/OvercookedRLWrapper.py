import json
import numpy as np
from gym import Wrapper
from gym.spaces import Box, MultiDiscrete
from gym_cooking.utils.agent import AgentRepr
import os


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
        self.last_action_dict = None
        self.success = False
        self.steps_to_success = 0

        # Clear the log file at the start
        with open(self.log_file, "w") as log:
            log.write("")



    def reset(self):
        # Call the original environment's reset method
        steps = self.steps_to_success
        obs = self.env.reset()
        self.steps_to_success = steps
        self.vector = self._process_observation(self.env.get_repr(), self.env.world.get_object_list())
        return self.vector

    def step(self, action_arr):

        # Call the original environment's step method
        action_dict = {}
        action_dict["agent-1"] = action_mapping[action_arr[0]]
        action_dict["agent-2"] = action_mapping[action_arr[1]]

        self.last_action_dict = action_dict
        with open(self.log_file, "a") as log:
            log.write("State:\n")
            log.write(np.array2string(self.vector) + "\n")  # Write the state as a raw array

        with open(self.log_file, "a") as log:
            log.write("Actions:\n")
            log.write(json.dumps(action_dict) + "\n")

        steps = self.env.t

        obs, reward, done, info = self.env.step(action_dict)
        if 'obs' in info:
            del info['obs']

        if not self.success:
            self.success = self.env.successful

        if self.steps_to_success == 0 and self.success:
            self.steps_to_success = steps
            print("steps to success:", self.steps_to_success)

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
                offset += AGENT_PROPERTIES

        plate_flag = False
        # Step 3: Encode moving objects
        for obj in moving_objects:
            x, y = obj.location
            if obj.name == 'Tomato':
                vector[offset] = 1
                vector[offset + 1] = 1
            elif obj.name == 'Lettuce':
                vector[offset] = 2
                vector[offset + 2] = 1
            elif obj.name == 'Plate' and not plate_flag:
                vector[offset] = 3
                vector[offset + 3] = 1
                plate_flag = True
            else:  # second plate
                vector[offset] = 4
                vector[offset + 3] = 2
            vector[offset + 5] = x
            vector[offset + 6] = y
            offset += OBJECT_PROPERTIES
        return vector

    def get_parameters(self, f, action_dict, width, height):
        offset = width * height
        object_offset = offset + AGENT_PROPERTIES * len(action_dict)  # Start after the grid and agent properties
        agent_keys = ["agent-1", "agent-2"]
        actions = []

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
                actions.append(f"({action} a{a + 1} {start_loc} {end_loc})")
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
                actions.append(f"(nop )")
                continue

            if dest_tile != "floor":
                actions.append(f"({action} a{a + 1} {start_loc} {end_loc} {item})")
            offset += 3
        f.write(" ".join(actions) + ")\n")  # Close the operators section



