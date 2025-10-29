import os

# New integer encoding for the map grid features (per coordinate)
TILE_ENCODING = {
    '-': 0,  # Counter
    ' ': 1,  # Floor
    '/': 2,  # Chopping Board
    '*': 3   # Delivery Spot
}

# PDDL Predicate mapping for the new grid encoding
# TILE_ENCODING: 0=Counter, 1=Floor, 2=Chopping Board, 3=Delivery Spot
GRID_PREDICATES = {
    1: "is_floor",
    2: "is_cutting_board",
    3: "delivery_spot"
}

AGENT_PROPERTIES = 3
OBJECT_PROPERTIES = 7


def text_map_to_vector(map_file_path, num_agents_to_use):
    """
    Converts a textual map file into a flattened vector representation,
    respecting dynamic agent counts and object properties.

    The vector order is:
    1. Grid Features (Tile encoding for every cell, row by row)
    2. Agent Features (ID, X, Y for each used agent)
    3. Object Features (ID, X, Y, is_tomato, is_lettuce, is_plate, is_cut for each object)

    Args:
        map_file_path: Path to the textual map file.
        num_agents_to_use: The number of agents (1-4) to include in the vector.

    Returns:
        A tuple containing (state_vector, width, height, num_agents, num_of_objects).
    """

    if not os.path.exists(map_file_path):
        raise FileNotFoundError(f"Map file not found at: {map_file_path}")

    with open(map_file_path, 'r') as f:
        content = f.read().strip().split('\n')

    # --- 1. Parse Sections ---
    agent_lines = []

    # Find the separator line (usually a blank line or non-map line)
    try:
        goal_index = content.index(next(line for line in content if not line.strip() or not (line[0] in TILE_ENCODING or
                                                                                             line[0].isalpha())))
    except StopIteration:
        raise ValueError("Could not determine map, goal, or agent sections in the file.")

    # Map lines are before the goal
    map_lines = [line.strip() for line in content[:goal_index] if line.strip()]

    # Agent lines start after the goal
    agent_start_index = goal_index + 2
    for line in content[agent_start_index:]:
        if line.strip():
            try:
                # Agent lines contain two space-separated coordinates
                parts = [int(p) for p in line.strip().split()]
                if len(parts) == 2:
                    agent_lines.append(parts)
            except ValueError:
                # Stop when non-coordinate lines are hit (e.g., file end, or extra separators)
                break

    # Dimensions
    world_height = len(map_lines)
    if not world_height:
        raise ValueError("Map is empty.")
    world_width = len(map_lines[0])

    # --- 2. Extract Objects and Full Agent Coordinates ---

    # We must assume the file contains up to 4 agent coordinates.
    # Agent coordinates are (x, y). The ID is implicit (0, 1, 2, 3)
    agent_coords_all = []  # Will hold the full [ID, x, y, ID, x, y, ...] list

    # The file contains X, Y for the agents; we add the ID
    for i in range(4):  # Assume up to 4 agents in the file for coordinate data
        if i < len(agent_lines):
            x, y = agent_lines[i]
        else:
            # Placeholder for agents not explicitly listed but required by a static file format
            x, y = -1, -1  # Invalid coordinates
        # Add to the full list (ID, X, Y)
        agent_coords_all.extend([i, x, y])

    # Agent lookup for checking for carried objects
    # Only use coordinates for agents that will be included in the vector
    agents_to_include_coords = set(tuple(agent_lines[i]) for i in range(min(num_agents_to_use, len(agent_lines))))

    # Object parsing
    objects_data = []  # List of [char, x, y]
    temp_map = [list(row) for row in map_lines]  # Mutable map copy

    for y in range(world_height):
        for x in range(world_width):
            char = map_lines[y][x]
            if char in ['p', 't', 'l']:
                objects_data.append([char, x, y])

                # Check if an agent is standing here (carrying the object)
                if (x, y) in agents_to_include_coords:
                    # If carried, the underlying tile is a floor
                    temp_map[y][x] = ' '
                else:
                    # If not carried, the underlying tile is a counter
                    temp_map[y][x] = '-'
            elif char == '-':
                # Ensure a counter is a counter, unless an agent is standing there
                if (x, y) in agents_to_include_coords:
                    temp_map[y][x] = ' '
                # else: temp_map[y][x] remains '-'

    # --- 3. Construct Vector: Grid Features ---
    vector = []
    for row in temp_map:
        for char in row:
            vector.append(TILE_ENCODING.get(char, 1))  # Default to Floor if unknown/unhandled

    # --- 4. Construct Vector: Agent Features (TRIMMED) ---

    agents_elements_to_keep = num_agents_to_use * AGENT_PROPERTIES
    agent_coords_final = agent_coords_all[:agents_elements_to_keep]
    vector.extend(agent_coords_final)

    # --- 5. Construct Vector: Object Features ---
    num_of_objects = len(objects_data)

    for i, (char, x, y) in enumerate(objects_data):
        # Object properties: ID, x, y, is_tomato, is_lettuce, is_plate, is_cut
        features = [
            i,          # 0: Object ID (o0, o1, ...)
            x, y,       # 1, 2: X, Y coordinates
            1 if char == 't' else 0,  # 3: is_tomato
            1 if char == 'l' else 0,  # 4: is_lettuce
            1 if char == 'p' else 0,  # 5: is_plate
            0           # 6: is_cut (Defaulting to 0 since input file doesn't specify cutting)
        ]
        vector.extend(features)

    return vector, world_width, world_height, num_agents_to_use, num_of_objects


def state_to_pddl(state, world_width, world_height, number_of_agents, number_of_objects, name_of_level, pddl_file_path):
    """
    Translates the state vector into a PDDL file, implementing the specific
    goal logic based on the level name.

    Args:
        state: The state vector representing the world.
        world_width: Width of the grid world.
        world_height: Height of the grid world.
        number_of_agents: Number of agents in the scene.
        number_of_objects: Number of dynamic objects in the scene.
        name_of_level: Name of the level (used for PDDL problem name and goal logic).
        pddl_file_path: Path to save the generated PDDL file.
    """

    with open(pddl_file_path, 'w') as pddl_file:
        # Write PDDL header
        pddl_file.write(f"; PDDL file for {name_of_level}\n")
        pddl_file.write(f"(define (problem {name_of_level})\n")
        pddl_file.write("(:domain grid_overcooked)\n\n")

        # Define Objects
        pddl_file.write("(:objects\n")

        # Grid cells (x0y0, x0y1, ...)
        for x in range(world_width):
            for y in range(world_height):
                pddl_file.write(f"    x{x}y{y} - cell\n")

        # Agents (a1, a2, ...)
        for i in range(number_of_agents):
            pddl_file.write(f"    a{i+1} - agent\n")

        # Dynamic Objects (o0, o1, o2, ...)
        for i in range(number_of_objects):
            pddl_file.write(f"    o{i} - veggieOrPlate\n")

        pddl_file.write(")\n\n")

        # Define initial state
        pddl_file.write("(:init\n")
        get_state(pddl_file, state, world_width, world_height, number_of_agents, number_of_objects)
        # get_state closes :init

        # --- Goal Finding Helpers (Determining which oN corresponds to t1/l1) ---
        grid_size = world_width * world_height

        def find_object_pddl_name(target_type: str) -> str:
            """Finds the PDDL name (oN) of the first object matching the target type."""
            offset = grid_size + (number_of_agents * AGENT_PROPERTIES)
            for j in range(number_of_objects):
                # indices: 3=tomato, 4=lettuce, 5=plate
                is_tomato = int(state[offset + 3])
                is_lettuce = int(state[offset + 4])

                if target_type == "tomato" and is_tomato:
                    return f"o{j}"
                elif target_type == "lettuce" and is_lettuce:
                    return f"o{j}"

                offset += OBJECT_PROPERTIES

            # Find the dynamic object names to substitute for static t1/l1
        t1_name = find_object_pddl_name("tomato")
        l1_name = find_object_pddl_name("lettuce")
        # ------------------------------------------------------------------------

        # Define goal (using the user's requested logic structure)
        pddl_file.write("(:goal\n")

        if "tomato" in name_of_level:
            pddl_file.write("   (and \n")
            pddl_file.write(f"       (delivered {t1_name})\n")
            pddl_file.write(f"       (tomato {t1_name})\n")
        elif "salad" in name_of_level:
            pddl_file.write("   (and \n")
            pddl_file.write(f"       (delivered {t1_name})\n")
            pddl_file.write(f"       (tomato {t1_name})\n")
            pddl_file.write(f"       (lettuce {t1_name})\n")
        elif "tl" in name_of_level:
            pddl_file.write("   (and \n")
            pddl_file.write(f"       (delivered {t1_name})\n")
            pddl_file.write(f"       (tomato {t1_name})\n")
            pddl_file.write(f"       (delivered {l1_name})\n")
            pddl_file.write(f"       (lettuce {l1_name})\n")
        pddl_file.write("   )\n")  # Closes the innermost AND/OR/implicit block
        pddl_file.write(")\n")  # Closes the :goal tag
        pddl_file.write(")\n")  # Closes the define tag


def get_state(pddl_file, state, world_width, world_height, agents, objects):
    """
    Writes the initial state predicates to the PDDL file based on the state vector.
    This function is generalized for variable sizes.
    """
    grid_size = world_width * world_height

    # 1. Add Agent Predicates
    offset = grid_size
    agent_locs = {}

    for i in range(agents):
        # Agent vector properties: [id, x, y]
        agent_x = int(state[offset + 1])
        agent_y = int(state[offset + 2])

        # PDDL agent name: a1, a2...
        agent_name = f"a{i+1}"

        pddl_file.write(f"(agent_at {agent_name} x{agent_x}y{agent_y})")
        pddl_file.write(f"(holding_nothing {agent_name})")
        pddl_file.write(f"(occupied x{agent_x}y{agent_y})")

        offset += AGENT_PROPERTIES
        agent_locs[agent_name] = (agent_x, agent_y)

    # 2. Add Grid Predicates
    for i in range(grid_size):
        x = i % world_width
        y = i // world_width

        tile_encoding = int(state[i])
        predicate = GRID_PREDICATES.get(tile_encoding)

        if predicate:
            pddl_file.write(f"({predicate} x{x}y{y})")

        # Add adjacency predicates
        if x + 1 < world_width:
            pddl_file.write(f"(adjacent x{x}y{y} x{x + 1}y{y})")
            pddl_file.write(f"(adjacent x{x + 1}y{y} x{x}y{y})")
        if y + 1 < world_height:
            pddl_file.write(f"(adjacent x{x}y{y} x{x}y{y + 1})")
            pddl_file.write(f"(adjacent x{x}y{y + 1} x{x}y{y})")

    # 3. Add Object Predicates
    offset = grid_size + (agents * AGENT_PROPERTIES)

    for i in range(objects):
        # Object vector properties: [id, x, y, is_tomato, is_lettuce, is_plate, is_cut]
        # Note: The object ID is already in the vector, but we use the loop index 'i' for consistent PDDL naming.
        obj_x = int(state[offset + 1])
        obj_y = int(state[offset + 2])
        is_tomato = int(state[offset + 3])
        is_lettuce = int(state[offset + 4])
        is_plate = int(state[offset + 5])
        is_cut = int(state[offset + 6])

        # PDDL object name: o0, o1, o2...
        object_name = f"o{i}"

        pddl_file.write(f"(object_at {object_name} x{obj_x}y{obj_y})")
        pddl_file.write(f"(occupied x{obj_x}y{obj_y})")

        # Define object type and state

        if is_tomato:
            pddl_file.write(f"(tomato {object_name})")
        if is_lettuce:
            pddl_file.write(f"(lettuce {object_name})")
        if is_plate:
            pddl_file.write(f"(plate {object_name})")
        else:
            pddl_file.write(f"(not-plate {object_name})")
        if is_cut:
            pddl_file.write(f"(is_cut {object_name})")

        offset += OBJECT_PROPERTIES

    pddl_file.write(")\n")


if __name__ == '__main__':
    # Example usage
    map_file = r'levels\large_tomato.txt'  # Path to your map file
    pddl_output_file = r'pddls\large_tomato_3.pddl'  # Path to save the PDDL file
    level_name = 'large_tomato_3'  # Example level name

    state_vector, width, height, num_agents, num_objects = text_map_to_vector(map_file, 3)
    state_to_pddl(state_vector, width, height, num_agents, num_objects, level_name, pddl_output_file)
