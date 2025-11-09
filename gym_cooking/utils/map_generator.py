import os
import random
import re
import glob
from collections import deque

# --- Constants ---

# Mapping of tile characters to their grid type
TILE_MAP = {
    '-': 'counter',
    '_': 'counter', # Allow underscore as a counter
    ' ': 'floor',
    '/': 'cutboard',
    '*': 'delivery'
}

# Mapping of object characters to their properties
OBJECT_MAP = {
    't': {'is_tomato': 1, 'is_lettuce': 0, 'is_plate': 0, 'is_cut': 0},
    'l': {'is_tomato': 0, 'is_lettuce': 1, 'is_plate': 0, 'is_cut': 0},
    'p': {'is_tomato': 0, 'is_lettuce': 0, 'is_plate': 1, 'is_cut': 0},
}

# Goal text for each recipe type
GOAL_TEXT_MAP = {
    "salad": "Salad",
    "tomato": "SimpleTomato",
    "tl": "SimpleTomato\nSimpleLettuce"
}

# --- Main Public Functions ---

def generate_text_map(output_dir, width, height, num_plates, num_tomatoes, num_lettuce, num_delivery, num_cutboards):
    """
    Generates a new random map layout and saves it as three separate files,
    one for each recipe type (salad, tomato, tl).

    Ensures the map is walled and all critical stations/items are reachable
    by at least one of the 4 placed agents.

    Args:
        output_dir (str): The folder to save the map files in.
        width (int): The total width of the map (including walls).
        height (int): The total height of the map (including walls).
        num_plates (int): Number of plates to place.
        num_tomatoes (int): Number of tomatoes to place.
        num_lettuce (int): Number of lettuce to place.
        num_delivery (int): Number of delivery spots.
        num_cutboards (int): Number of cutting boards.

    Returns:
        list[str]: A list of file paths for the 3 generated maps.
    """
    if width < 5 or height < 5:
        raise ValueError("Map dimensions must be at least 5x5 to allow for walls and content.")

    # --- Map Generation Loop ---
    max_retries = 100
    for attempt in range(max_retries):
        # 1. Initialize empty grid with floor tiles
        grid = [[' ' for _ in range(width)] for _ in range(height)]

        # 2. Add Counter Walls
        for x in range(width):
            grid[0][x] = '-'  # Top wall
            grid[height-1][x] = '-' # Bottom wall
        for y in range(height):
            grid[y][0] = '-'  # Left wall
            grid[y][width-1] = '-' # Right wall

        # 3. Get valid interior coordinates for placing items
        valid_coords = _get_valid_placement_coords(grid, width, height)
        if len(valid_coords) < (num_plates + num_tomatoes + num_lettuce + num_delivery + num_cutboards + 4): # +4 for agents
            # print(f"Warning: Not enough valid coordinates ({len(valid_coords)}) for all items. Retrying...")
            continue # Not enough space, retry

        random.shuffle(valid_coords)

        # 4. Define static stations and dynamic objects
        static_stations = {
            '*': num_delivery,
            '/': num_cutboards
        }
        dynamic_objects = {
            'p': num_plates,
            't': num_tomatoes,
            'l': num_lettuce
        }

        # 5. Place static stations (Delivery, Cutboard)
        # These permanently change the grid tile
        station_coords = {}
        has_space = True
        for char, count in static_stations.items():
            station_coords[char] = []
            for _ in range(count):
                if not valid_coords:
                    has_space = False
                    break
                x, y = valid_coords.pop()
                grid[y][x] = char
                station_coords[char].append((x, y))
            if not has_space:
                break
        if not has_space:
            # print("Warning: Ran out of space placing static stations. Retrying...")
            continue

        # 6. Place dynamic objects (Plate, Tomato, Lettuce)
        # These are placed *on* tiles (assumed floor for placement)
        object_coords = {}
        for char, count in dynamic_objects.items():
            object_coords[char] = []
            for _ in range(count):
                if not valid_coords:
                    has_space = False
                    break
                x, y = valid_coords.pop()
                # We place the object, but the underlying tile is floor ' '
                # The map converter will later handle this
                grid[y][x] = char
                object_coords[char].append((x, y))
            if not has_space:
                break
        if not has_space:
            # print("Warning: Ran out of space placing dynamic objects. Retrying...")
            continue

        # 7. Place 4 Agents
        agent_coords = []
        for _ in range(4): # Always place 4 agents
            if not valid_coords:
                has_space = False
                break
            # Agents must be placed on a floor tile
            x, y = valid_coords.pop()
            if grid[y][x] != ' ': # This coord was taken by an object
                # Find a new spot that is guaranteed floor
                found_floor = False
                for i in range(len(valid_coords)):
                    fx, fy = valid_coords[i]
                    if grid[fy][fx] == ' ':
                        agent_coords.append(valid_coords.pop(i)) # Take this spot
                        found_floor = True
                        break
                if not found_floor:
                    has_space = False # No floor spots left
            else:
                agent_coords.append((x,y)) # Coord was floor, assign it

            if not has_space:
                break

        if not has_space:
            # print("Warning: Ran out of space placing agents. Retrying...")
            continue

        # 8. --- Reachability Check (Universal) ---
        # This layout must support all recipes, so we check all critical items.

        # Combine all critical coordinates
        critical_coords = set()
        for coords_list in station_coords.values():
            critical_coords.update(coords_list)
        for coords_list in object_coords.values():
            critical_coords.update(coords_list)

        # Define all required target *characters*
        required_targets = {'*', '/', 'p', 't', 'l'}

        # Find reachable targets from any agent
        reachable_targets = set()
        # We only *require* one agent to be able to reach everything
        # But we check all 4 for robustness
        for ax, ay in agent_coords:
            reachable_targets.update(_is_reachable(grid, (ax, ay), critical_coords))

        # Get the *characters* of the reachable targets
        reachable_target_chars = set()
        for x, y in reachable_targets:
            reachable_target_chars.add(grid[y][x])

        if required_targets.issubset(reachable_target_chars):
            # Success! This layout is valid for all recipes.

            # --- 9. Save all 3 map files ---
            base_map_name = _find_next_map_name(output_dir)
            generated_files = []

            # Create the map string
            map_str = "\n".join("".join(row) for row in grid)
            agent_loc_lines = "\n".join(f"{x} {y}" for x, y in agent_coords)

            for recipe_type, goal_text in GOAL_TEXT_MAP.items():
                filename = f"{base_map_name}_{recipe_type}.txt"
                filepath = os.path.join(output_dir, filename)

                output_content = f"{map_str}\n\n{goal_text}\n\n{agent_loc_lines}"

                with open(filepath, 'w') as f:
                    f.write(output_content)
                generated_files.append(filepath)

            print(f"Successfully generated 3 maps with base name: {base_map_name}")
            return generated_files

        # If check fails, the loop continues to the next attempt

    raise RuntimeError(f"Failed to generate a valid, fully reachable map after {max_retries} attempts.")


def reconfigure_map_layout(input_map_path, output_dir):
    """
    Loads an existing map file, preserves its grid (counters, floors,
    stations), and randomly re-places all agents and dynamic objects (t, l, p).

    Saves 3 reconfigured files (salad, tomato, tl) with incremented
    version numbers (e.g., map1_salad_v2.txt).

    Args:
        input_map_path (str): Path to the *base* map file (e.g., "map1_salad.txt").
        output_dir (str): The folder to save the reconfigured map files in.

    Returns:
        list[str]: A list of file paths for the 3 reconfigured maps.
    """
    if not os.path.exists(input_map_path):
        raise FileNotFoundError(f"Input map file not found: {input_map_path}")

    # --- 1. Parse Input Map File ---
    with open(input_map_path, 'r') as f:
        lines = [line.strip() for line in f.readlines()]

    grid_lines = []
    agent_lines = []
    goal_text = None
    parsing_state = 'map'

    for line in lines:
        if not line: # Skip empty lines
            continue

        if parsing_state == 'map':
            # Check if line looks like a map row
            if all(c in TILE_MAP or c in OBJECT_MAP for c in line):
                grid_lines.append(list(line))
            else:
                # First non-map line is the goal
                goal_text = line
                parsing_state = 'goal'

        elif parsing_state == 'goal':
            # Check if line looks like agent coords (e.g., "4 2")
            try:
                coords = list(map(int, line.split()))
                if len(coords) == 2:
                    agent_lines.append(coords)
                    parsing_state = 'agents'
                else:
                    # This is a multi-line goal (e.g., for 'tl')
                    goal_text += "\n" + line
            except ValueError:
                # This is a multi-line goal
                goal_text += "\n" + line

        elif parsing_state == 'agents':
            try:
                coords = list(map(int, line.split()))
                if len(coords) == 2:
                    agent_lines.append(coords)
            except ValueError:
                pass # Done parsing

    if not grid_lines or not agent_lines or not goal_text:
        raise ValueError(f"Failed to parse map, goal, or agents from: {input_map_path}")

    width = len(grid_lines[0])
    height = len(grid_lines)

    # --- 2. Separate Grid from Objects ---

    # Grid of floor, counters, and static stations
    base_grid = [[' ' for _ in range(width)] for _ in range(height)]

    # Counts of objects to be re-placed
    objects_to_place = {'t': 0, 'l': 0, 'p': 0}

    # Coordinates of static stations
    station_coords = {'*': [], '/': []}

    # All floor tiles that can hold items/agents
    available_floor_coords = []

    for y, row in enumerate(grid_lines):
        for x, char in enumerate(row):
            if char in OBJECT_MAP:
                # It's a dynamic object (t, l, p)
                objects_to_place[char] += 1
                base_grid[y][x] = ' ' # Underlying tile is floor
                if 0 < x < width - 1 and 0 < y < height - 1:
                    available_floor_coords.append((x, y))
            elif char in TILE_MAP:
                # It's a grid tile (-, _, ' ', /, *)
                base_grid[y][x] = char
                if char == ' ': # Floor
                    if 0 < x < width - 1 and 0 < y < height - 1:
                        available_floor_coords.append((x, y))
                elif char in station_coords: # Delivery or Cutboard
                    station_coords[char].append((x, y))
            else:
                base_grid[y][x] = ' ' # Default to floor if unknown

    num_agents_to_place = 4 # Always re-place 4 agents
    num_objects = sum(objects_to_place.values())

    if len(available_floor_coords) < (num_objects + num_agents_to_place):
        raise ValueError(f"Not enough available floor space ({len(available_floor_coords)}) "
                         f"to re-place {num_objects} objects and {num_agents_to_place} agents.")

    # --- 3. Re-placement Loop ---
    max_retries = 100
    for attempt in range(max_retries):
        random.shuffle(available_floor_coords)
        temp_coords = list(available_floor_coords) # Copy to pop from

        # Create a new grid to place objects into
        new_grid = [row[:] for row in base_grid]

        # 3.1 Re-place dynamic objects
        object_coords = {'t': [], 'l': [], 'p': []}
        has_space = True
        for char, count in objects_to_place.items():
            for _ in range(count):
                if not temp_coords:
                    has_space = False
                    break
                x, y = temp_coords.pop()
                new_grid[y][x] = char
                object_coords[char].append((x, y))
            if not has_space:
                break
        if not has_space:
            # print("Warning (Reconfig): Ran out of space for objects. Retrying...")
            continue

        # 3.2 Re-place 4 Agents
        agent_coords = []
        for _ in range(num_agents_to_place):
            if not temp_coords:
                has_space = False
                break
            # Agents must be placed on a floor tile
            x, y = temp_coords.pop()
            if new_grid[y][x] != ' ': # This coord was taken by an object
                # Find a new spot that is guaranteed floor
                found_floor = False
                for i in range(len(temp_coords)):
                    fx, fy = temp_coords[i]
                    if new_grid[fy][fx] == ' ':
                        agent_coords.append(temp_coords.pop(i)) # Take this spot
                        found_floor = True
                        break
                if not found_floor:
                    has_space = False # No floor spots left
            else:
                agent_coords.append((x,y)) # Coord was floor, assign it

            if not has_space:
                break

        if not has_space:
            # print("Warning (Reconfig): Ran out of space for agents. Retrying...")
            continue

        # 3.3 --- Reachability Check (Universal) ---
        # Combine all critical coordinates
        critical_coords = set()
        for coords_list in station_coords.values():
            critical_coords.update(coords_list)
        for coords_list in object_coords.values():
            critical_coords.update(coords_list)

        # Define all required target *characters*
        required_targets = {'*', '/', 'p', 't', 'l'}

        # Find reachable targets from any agent
        reachable_targets = set()
        for ax, ay in agent_coords:
            reachable_targets.update(_is_reachable(new_grid, (ax, ay), critical_coords))

        # Get the *characters* of the reachable targets
        reachable_target_chars = set()
        for x, y in reachable_targets:
            reachable_target_chars.add(new_grid[y][x]) # Check the *new* grid

        if required_targets.issubset(reachable_target_chars):
            # Success! This layout is valid.

            # --- 4. Save all 3 reconfigured map files ---
            generated_files = []

            # Create the map string
            map_str = "\n".join("".join(row) for row in new_grid)
            agent_loc_lines = "\n".join(f"{x} {y}" for x, y in agent_coords)

            for recipe_type, goal_text_from_map in GOAL_TEXT_MAP.items():

                # Re-build the input path for this recipe type to check its version
                in_path_base = os.path.basename(input_map_path)

                # Find the *original* recipe type from the input filename
                original_recipe_type = "salad" # default
                for rt in GOAL_TEXT_MAP.keys():
                    if f"_{rt}" in in_path_base:
                        original_recipe_type = rt
                        break

                in_path_for_recipe = in_path_base.replace(f"_{original_recipe_type}", f"_{recipe_type}")

                hypothetical_input_path = os.path.join(os.path.dirname(input_map_path), in_path_for_recipe)

                base_name_for_recipe, out_filepath = _get_next_versioned_filename(hypothetical_input_path, output_dir)

                # Use the correct goal text for this recipe type
                output_content = f"{map_str}\n\n{goal_text_from_map}\n\n{agent_loc_lines}"

                with open(out_filepath, 'w') as f:
                    f.write(output_content)
                generated_files.append(out_filepath)

            print(f"Successfully reconfigured and saved 3 maps with base name: {base_name_for_recipe}")
            return generated_files

    raise RuntimeError(f"Failed to reconfigure a valid, fully reachable map after {max_retries} attempts.")


# --- Private Helper Functions ---

def _is_reachable(grid, start_coord, target_coords):
    """
    Performs a Breadth-First Search (BFS) to find all reachable targets.
    Agents can ONLY move on floor tiles (' ').
    Targets are "reachable" if they are ADJACENT (N,S,E,W) to a reachable
    floor tile.

    Args:
        grid (list[list[str]]): The map grid.
        start_coord (tuple[int, int]): The (x, y) starting coordinate (an agent).
        target_coords (set[tuple[int, int]]): A set of (x, y) coordinates for all
                                               critical items to find.

    Returns:
        set[tuple[int, int]]: A set of the (x, y) coordinates from target_coords
                               that are reachable from the start_coord.
    """
    # Agent must start on a floor tile to be able to move
    if grid[start_coord[1]][start_coord[0]] != ' ':
        return set() # Agent is not on a floor tile, can't move

    q = deque([start_coord])
    visited = {start_coord}
    found_targets = set()

    width = len(grid[0])
    height = len(grid)

    # Directions: (dx, dy)
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)] # N, S, E, W

    while q:
        cx, cy = q.popleft() # Current (x, y)

        # Check all 4 adjacent neighbors OF THE CURRENT FLOOR TILE
        for dx, dy in directions:
            nx, ny = cx + dx, cy + dy # Neighbor (x, y)

            # Check bounds
            if not (0 <= nx < width and 0 <= ny < height):
                continue

            neighbor_coord = (nx, ny)

            # 1. Check if this neighbor IS a target
            if neighbor_coord in target_coords:
                found_targets.add(neighbor_coord)

            # 2. Check if we can MOVE to this neighbor (is it unvisited floor?)
            if neighbor_coord not in visited and grid[ny][nx] == ' ':
                visited.add(neighbor_coord)
                q.append(neighbor_coord)

    return found_targets


def _get_valid_placement_coords(grid, width, height):
    """
    Returns a list of (x, y) tuples for all interior tiles that are
    currently 'floor' (' ') and not adjacent to a corner.
    """
    coords = []
    for y in range(1, height - 1): # Iterate interior
        for x in range(1, width - 1): # Iterate interior

            # Must be a floor tile
            if grid[y][x] != ' ':
                continue

            # Check for corner adjacency
            is_near_corner = False
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx == 0 and dy == 0:
                        continue

                    nx, ny = x + dx, y + dy
                    # Check if neighbor (nx, ny) is a wall corner
                    is_wall_x = (nx == 0 or nx == width - 1)
                    is_wall_y = (ny == 0 or ny == height - 1)
                    if is_wall_x and is_wall_y:
                        is_near_corner = True
                        break
                if is_near_corner:
                    break

            if not is_near_corner:
                coords.append((x, y))

    return coords


def _find_next_map_name(output_dir):
    """
    Finds the next available map index (e.g., "map5").
    Scans for files like "map1_salad.txt", "map2_tl.txt", etc.

    Returns:
        str: The next map base name (e.g., "map1", "map2").
    """
    os.makedirs(output_dir, exist_ok=True)
    existing_files = glob.glob(os.path.join(output_dir, "map*_*.txt"))

    max_index = 0
    for f in existing_files:
        basename = os.path.basename(f)
        match = re.match(r"map(\d+)_", basename)
        if match:
            max_index = max(max_index, int(match.group(1)))

    return f"map{max_index + 1}"


def _get_next_versioned_filename(input_map_path, output_dir):
    """
    Parses an input filename (e.g., "map1_salad.txt" or "map1_salad_v2.txt")
    and finds the next available version number in the output directory.

    Args:
        input_map_path (str): The full path to the *source* map file.
        output_dir (str): The folder to save the new file in.

    Returns:
        tuple[str, str]: (base_name, next_filepath)
                         e.g., ("map1_salad", "path/to/output/map1_salad_v3.txt")
    """
    os.makedirs(output_dir, exist_ok=True)

    # 1. Parse the input filename
    basename = os.path.basename(input_map_path)

    # Regex to find base name (map1_salad) and optional version (_v2)
    # Allows for "map1_salad.txt" or "map1_salad_v2.txt"
    match = re.match(r"^(?P<base>map\d+_[a-z]+)(_v(?P<version>\d+))?\.txt$", basename)

    if not match:
        raise ValueError(f"Could not parse version from filename: {basename}")

    base_name = match.group('base') # e.g., "map1_salad"

    # 2. Find all existing versions in the output directory
    glob_pattern = os.path.join(output_dir, f"{base_name}*.txt")
    existing_files = glob.glob(glob_pattern)

    max_version = 0
    if not existing_files:
        # No files found in output dir.
        # Check the *input* file's version to start from there.
        in_match = re.match(r"^(?P<base>map\d+_[a-z]+)(_v(?P<version>\d+))?\.txt$", basename)
        if in_match and in_match.group('version'):
            max_version = int(in_match.group('version'))
        else:
            max_version = 1 # Original is v1
    else:
        # Files exist, find the highest version number
        for f in existing_files:
            f_base = os.path.basename(f)
            v_match = re.match(r"^%s_v(\d+)\.txt$" % re.escape(base_name), f_base)
            if v_match:
                # This is a versioned file like "map1_salad_v2.txt"
                max_version = max(max_version, int(v_match.group(1)))
            elif f_base == f"{base_name}.txt":
                # This is the base file "map1_salad.txt"
                max_version = max(max_version, 1) # Base file counts as v1

    # 3. Create the new filename
    next_version = max_version + 1
    next_filename = f"{base_name}_v{next_version}.txt"
    next_filepath = os.path.join(output_dir, next_filename)

    return base_name, next_filepath


# --- Example Usage ---

if __name__ == '__main__':
    # Define parameters
    MAP_OUTPUT_DIR = "../utils/levels"

    print(f"--- Generating new maps in '{MAP_OUTPUT_DIR}' ---")
    try:
        # Generate a new set of 3 maps (salad, tomato, tl)
        generated_files = generate_text_map(
            output_dir=MAP_OUTPUT_DIR,
            width=8,
            height=10,
            num_plates=3,
            num_tomatoes=2,
            num_lettuce=2,
            num_delivery=1,
            num_cutboards=2
        )

        print("\nGenerated files:")
        for f in generated_files:
            print(f" - {f}")

        # --- Reconfiguration Example ---
        if generated_files:
            print(f"\n--- Reconfiguring layout from '{generated_files[0]}' ---")

            # Take the first generated map (e.g., map1_salad.txt) and reconfigure it
            reconfig_files = reconfigure_map_layout(
                input_map_path=generated_files[0],
                output_dir=MAP_OUTPUT_DIR
            )

            print("\nReconfigured files:")
            for f in reconfig_files:
                print(f" - {f}")

            # # --- Reconfigure the *reconfigured* map ---
            # if reconfig_files:
            #     print(f"\n--- Reconfiguring *again* from '{reconfig_files[0]}' ---")
            #
            #     # Take the first reconfigured map (e.g., map1_salad_v2.txt) and reconfigure it
            #     reconfig_files_v3 = reconfigure_map_layout(
            #         input_map_path=reconfig_files[0],
            #         output_dir=MAP_OUTPUT_DIR
            #     )
            #
            #     print("\nReconfigured files (v3):")
            #     for f in reconfig_files_v3:
            #         print(f" - {f}")

    except (ValueError, RuntimeError, FileNotFoundError) as e:
        print(f"\nAn error occurred: {e}")