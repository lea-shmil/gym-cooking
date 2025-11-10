import json
import numpy as np
from gym import Wrapper
from gym.spaces import Box, MultiDiscrete
from gym_cooking.utils.pddl_problem_generator import text_map_to_vector

action_mapping = {
    0: (0, -1),  # Move up
    1: (0, 1),  # Move down
    2: (-1, 0),  # Move left
    3: (1, 0),  # Move right
    4: (0, 0),  # No-op
}

# 0=Counter, 1=Floor, 2=Cutboard, 3=Delivery Spot
tile_type = {
    0: "counter",
    1: "floor",
    2: "cutboard",
    3: "delivery",
    # The rest are included for compatibility but only 0-3 should be used for grid tiles
    7: "tomato",
    8: "lettuce",
    9: "plate"
}

AGENT_PROPERTIES = 3
OBJECT_PROPERTIES = 7


class OvercookedRLWrapper(Wrapper):
    def __init__(self, env):
        super().__init__(env)
        self.map_file = rf"gym_cooking\utils\levels\{self.env.arglist.level}.txt"
        self.vector, self.width, self.height, num_agents, self.num_objects = text_map_to_vector(self.map_file,
                                                                                                self.env.arglist.num_agents)
        self.observation_space = Box(low=0, high=255, shape=(len(self.vector),), dtype=np.uint8)
        action_vec = [5] * num_agents  # 5 actions per agent
        self.action_space = MultiDiscrete(action_vec)  # MultiDiscrete action space for 1-4 agents
        self.log_file = "env_log.txt"  # File to log states and actions
        self.last_action_dict = None
        self.success = False
        self.steps_to_success = 0

        # Clear the log file at the start
        with open(self.log_file, "w") as log:
            log.write("")

    def reset(self):
        # Call the original environment's reset method
        steps = self.steps_to_success
        self.env.reset()
        self.steps_to_success = steps
        self.vector, width, height, num_agents, num_objects = text_map_to_vector(self.map_file,
                                                                                 self.env.arglist.num_agents)
        return self.vector

    def step(self, action_arr):
        #  Call the original environment's step
        action_dict = {}
        #  actions per number of agents
        for i, action in enumerate(action_arr):
            action_dict[f"agent-{i + 1}"] = action_mapping[action]
        self.last_action_dict = action_dict

        with open(self.log_file, "a") as log:
            log.write("State:\n")
            log.write(np.array2string(np.array(self.vector)) + "\n")  # Write the state as a raw array

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

    def get_parameters(self, f, action_dict, width, height):
        """
        Translates agent actions and the current state vector into PDDL operators,
        and updates the state vector based on the action result.

        Args:
            self: The parent class instance.
            f: The file stream to write PDDL actions to.
            action_dict: Dictionary mapping agent keys (e.g., 'agent-1') to [dx, dy] actions.
            width: Width of the world grid.
            height: Height of the world grid.
        """
        # 1. Initialization and Dynamic Agent/Object Count
        grid_size = width * height
        num_agents = len(action_dict)
        agent_start_offset = grid_size
        object_start_offset = grid_size + AGENT_PROPERTIES * num_agents
        agent_keys = [f"agent-{i + 1}" for i in range(num_agents)]
        actions = []
        num_objects = (len(self.vector) - object_start_offset) // OBJECT_PROPERTIES

        # 2. Iterate through each agent dynamically ('a' is the 0-based index: 0, 1, 2, ...)
        for a, agent_key in enumerate(agent_keys):
            current_agent_offset = agent_start_offset + (a * AGENT_PROPERTIES)

            # 2.1 Read current state
            # Note: self.vector[current_agent_offset] is the agent ID (0, 1, 2, ...)
            x_start = int(self.vector[current_agent_offset + 1])
            y_start = int(self.vector[current_agent_offset + 2])
            start_loc = f"x{x_start}y{y_start}"

            # 2.2 Calculate destination state
            dx, dy = action_dict[agent_key]
            x_end = x_start + dx
            y_end = y_start + dy
            end_loc = f"x{x_end}y{y_end}"

            # Calculate destination tile properties
            dest_index = y_end * width + x_end
            dest = self.vector[dest_index]
            dest_tile = tile_type.get(dest, "unknown")

            # 2.3 Object Search
            object_dest_index = -1  # Vector index of the object at the destination tile
            object_held_index = -1  # Vector index of the object currently held by the agent

            for i in range(num_objects):
                # i_start is the index of the current object's ID in the vector
                i_start = object_start_offset + (i * OBJECT_PROPERTIES)

                # The X and Y coordinates of the object are at i_start + 1 and i_start + 2
                obj_x = int(self.vector[i_start + 1])
                obj_y = int(self.vector[i_start + 2])

                if obj_x == x_start and obj_y == y_start:
                    object_held_index = i_start

                # cant be the same object
                if obj_x == x_end and obj_y == y_end and object_held_index != i_start:
                    object_dest_index = i_start

            # --- PDDL Action Logic ---

            # Note: Indexes are relative to the object's ID (index 0 of the object block)
            # 3: is_tomato, 4: is_lettuce, 5: is_plate, 6: is_cut
            is_tomato_idx = 3
            is_lettuce_idx = 4
            is_plate_idx = 5
            is_cut_idx = 6

            # --- Collision Logic ---
            is_blocked_by_other_agent = False
            for j in range(num_agents):
                if a == j:
                    continue  # Skip checking against self

                # Calculate the offset for the other agent 'j'
                other_agent_offset = agent_start_offset + (j * AGENT_PROPERTIES)
                other_x = int(self.vector[other_agent_offset + 1])
                other_y = int(self.vector[other_agent_offset + 2])

                if x_end == other_x and y_end == other_y:
                    is_blocked_by_other_agent = True
                    break

            # 3. Move Action
            if dest_tile == "floor" and not is_blocked_by_other_agent and 0 < x_end < width - 1 and \
                    0 < y_end < height - 1 and (dx != 0 or dy != 0):
                action = "move"
                actions.append(f"({action} a{a + 1} {start_loc} {end_loc})")

                self.vector[current_agent_offset + 1] = x_end
                self.vector[current_agent_offset + 2] = y_end

                if object_held_index != -1:
                    self.vector[object_held_index + 1] = x_end
                    self.vector[object_held_index + 2] = y_end

            # 4. Pickup Action
            elif (dest_tile == "counter" or dest_tile == "cutboard") and object_dest_index != -1 and \
                    object_held_index == -1:
                action = "pickup"
                item_id = int(self.vector[object_dest_index])
                item = f"o{item_id}"

                actions.append(f"({action} a{a + 1} {end_loc} {item})")

                self.vector[object_dest_index + 1] = x_start
                self.vector[object_dest_index + 2] = y_start

            # 5. Chop Action
            elif (dest_tile == "cutboard" and object_dest_index == -1 and object_held_index != -1 and
                  int(self.vector[object_held_index + is_cut_idx]) == 0 and
                  int(self.vector[object_held_index + is_plate_idx]) == 0):
                action = "chop"
                item_id = int(self.vector[object_held_index])
                item = f"o{item_id}"
                actions.append(f"({action} a{a + 1} {end_loc} {item})")

                self.vector[object_held_index + is_cut_idx] = 1

                # 6. Delivery Action
            elif (dest_tile == "delivery" and object_held_index != -1 and
                  int(self.vector[object_held_index + is_plate_idx]) != 0 and
                  int(self.vector[object_held_index + is_cut_idx]) == 1):
                action = "deliver"
                item_id = int(self.vector[object_held_index])
                item = f"o{item_id}"
                actions.append(f"({action} a{a + 1} {end_loc} {item})")

                self.vector[object_held_index + 1] = -1
                self.vector[object_held_index + 2] = -1

            # 7. Put Down Action
            elif object_dest_index == -1 and object_held_index != -1:
                #  split put-down into 3 actions based on destination tile and object properties
                if dest_tile == "counter" and int(self.vector[object_held_index + is_cut_idx]) == 0 and \
                        int(self.vector[object_held_index + is_plate_idx]) == 0:
                    action = "put-down-unchopped-veggie"
                elif (dest_tile == "cutboard" or dest_tile == "counter") \
                        and int(self.vector[object_held_index + is_cut_idx]) == 1:
                    action = "put-down-chopped-veggie"
                elif (dest_tile == "cutboard" or dest_tile == "counter") \
                        and int(self.vector[object_held_index + is_plate_idx]) != 0:
                    action = "put-down-plate"
                else:
                    actions.append(f"(nop a{a + 1})")
                    continue

                item_id = int(self.vector[object_held_index])
                item = f"o{item_id}"
                actions.append(f"({action} a{a + 1} {end_loc} {item})")
                self.vector[object_held_index + 1] = x_end
                self.vector[object_held_index + 2] = y_end

            # 8. Merge Action
            elif object_held_index != -1 and object_dest_index != -1:
                # held is plate and not merged and dest is chopped and not merged
                if int(self.vector[object_held_index + is_plate_idx]) != 0 and \
                        int(self.vector[object_held_index + is_cut_idx]) == 0 and \
                        int(self.vector[object_dest_index + is_cut_idx]) == 1 and \
                        int(self.vector[object_dest_index + is_plate_idx]) == 0:

                    action = "merge-plate"
                # held is chopped and not merged and dest is plate and not merged
                elif int(self.vector[object_held_index + is_cut_idx]) == 1 and \
                        int(self.vector[object_dest_index + is_plate_idx]) != 0 and \
                        int(self.vector[object_held_index + is_plate_idx]) == 0 and \
                        int(self.vector[object_dest_index + is_cut_idx]) == 0:

                    action = "merge-plate-on-counter"
                # no plates involved, held is chopped lettuce and dest is chopped tomato
                elif int(self.vector[object_held_index + is_cut_idx]) == 1 \
                        and int(self.vector[object_dest_index + is_cut_idx]) == 1 \
                        and int(self.vector[object_held_index + is_plate_idx]) == 0 \
                        and int(self.vector[object_dest_index + is_plate_idx]) == 0 \
                        and int(self.vector[object_held_index + is_lettuce_idx]) == 1 \
                        and int(self.vector[object_dest_index + is_tomato_idx]) == 1:

                    action = "merge-no-plate-tomato"
                elif int(self.vector[object_held_index + is_cut_idx]) == 1 \
                        and int(self.vector[object_dest_index + is_cut_idx]) == 1 \
                        and int(self.vector[object_held_index + is_plate_idx]) == 0 \
                        and int(self.vector[object_dest_index + is_plate_idx]) == 0 \
                        and int(self.vector[object_held_index + is_tomato_idx]) == 1 \
                        and int(self.vector[object_dest_index + is_lettuce_idx]) == 1:

                    action = "merge-no-plate-lettuce"
                    # held is chopped tomato and dest is chopped lettuce
                else:
                    actions.append(f"(nop a{a + 1})")
                    continue

                item_id_held = int(self.vector[object_held_index])
                item = f"o{item_id_held}"

                item_id_dest = int(self.vector[object_dest_index])
                item_dest = f"o{item_id_dest}"

                actions.append(f"({action} a{a + 1} {end_loc} {item} {item_dest})")

                # Merge properties onto the held object

                self.vector[object_held_index + is_plate_idx] = (
                    max(self.vector[object_held_index + is_plate_idx], self.vector[object_dest_index + is_plate_idx]))
                self.vector[object_held_index + is_cut_idx] = \
                    max(self.vector[object_held_index + is_cut_idx], self.vector[object_dest_index + is_cut_idx])
                self.vector[object_held_index + is_tomato_idx] = \
                    max(self.vector[object_held_index + is_tomato_idx], self.vector[object_dest_index + is_tomato_idx])
                self.vector[object_held_index + is_lettuce_idx] = (max(self.vector[object_held_index + is_lettuce_idx],
                                                                       self.vector[object_dest_index + is_lettuce_idx]))
                # Invalidate/Remove the object at the destination tile
                self.vector[object_dest_index + 1] = -1
                self.vector[object_dest_index + 2] = -1
                self.vector[object_dest_index + is_plate_idx] = 0
                self.vector[object_dest_index + is_cut_idx] = 0

            # 9. Default Nop
            else:
                actions.append(f"(nop a{a + 1})")

        f.write(" ".join(actions) + ")\n")
