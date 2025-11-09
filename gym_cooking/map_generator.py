from typing import List, Tuple, Dict, Optional, Set
import random
import os
import re # Added for version parsing
import glob # Added for checking map index

# --- Constants for Map Generation and Recipe Requirements ---

# Set to always output 4 agent locations in the map file for consistent format
MAX_AGENTS_IN_FILE = 4

# Tile encoding used for output (must match map_converter.py's expectation)
TILE_CHARS = {'counter': '-', 'floor': ' ', 'cutboard': '/', 'delivery': '*'}
OBJECT_CHARS = {'plate': 'p', 'tomato': 't', 'lettuce': 'l'}

# NEW: Defines the exact goal text (including multi-line) for each recipe type
GOAL_TEXT_MAP = {
    "salad": "Salad",
    "tomato": "SimpleTomato",
    "tl": "SimpleTomato\nSimpleLettuce"
}

# This is now used for the UNIVERSAL reachability check
RECIPE_REQUIREMENTS = {
    "universal": [('tomato', 1), ('lettuce', 1), ('plate', 1), ('cutboard', 1), ('delivery', 1)],
}
# A simple list of all types we must check for reachability
UNIVERSAL_REQUIRED_TYPES = {'tomato', 'lettuce', 'plate', 'cutboard', 'delivery'}


# --- Helper Functions for Placement and Connectivity ---

def _get_valid_placement_coords(width: int, height: int, map_grid: List[List[str]]) -> List[Tuple[int, int]]:
    """
    Returns all INTERIOR coordinates that are currently floor (' ') or counter ('-').
    Placements are restricted to (1..width-2) and (1..height-2).
    """
    coords = []
    # Start at 1, end before height - 1 to stay inside the walls
    for y in range(1, height - 1):
        # Start at 1, end before width - 1 to stay inside the walls
        for x in range(1, width - 1):
            # Ensure the spot is currently empty or a counter (safe to place over)
            if map_grid[y][x] in [' ', '-']:
                coords.append((x, y))
    random.shuffle(coords)
    return coords

def _is_reachable(start_x: int, start_y: int, target_coords: Set[Tuple[int, int]], width: int, height: int, map_grid: List[List[str]]) -> bool:
    """
    Performs a simplified Breadth-First Search (BFS) to check if any target coordinate is reachable
    from the start coordinate, moving only on floor tiles (' ') or counter tiles ('-').
    """
    queue = [(start_x, start_y)]
    visited: Set[Tuple[int, int]] = set(queue)

    # Movement offsets: up, down, left, right
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

    while queue:
        x, y = queue.pop(0)

        if (x, y) in target_coords:
            return True # Target found!

        for dx, dy in directions:
            nx, ny = x + dx, y + dy

            # Check bounds AND that it hasn't been visited
            if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in visited:
                tile = map_grid[ny][nx]

                # Agents can move on floors (' '), and can stand next to/on stations/objects
                # This logic assumes agents can move through counter spaces as well to reach items
                if tile in [' ', '-', '/', '*'] or tile in OBJECT_CHARS.values():
                    visited.add((nx, ny))
                    queue.append((nx, ny))

    return False

def _find_next_map_index(output_dir: str) -> int:
    """
    Finds the next available map index (e.g., map1, map2, mapX).
    Checks for the existence of mapX_*.txt.
    """
    # 1. Ensure directory exists
    os.makedirs(output_dir, exist_ok=True)

    # 2. Find the next available sequential number
    index = 1
    while True:
        # Check if any file starting with "map<index>_" exists
        # e.g., map1_salad.txt, map1_tomato.txt
        check_path_pattern = os.path.join(output_dir, f"map{index}_*.txt")
        if not glob.glob(check_path_pattern):
            return index # This index is free
        index += 1

def _get_next_versioned_paths(original_path: str, output_dir: str) -> Dict[str, str]:
    """
    Takes the path of an existing file (e.g., map1_salad.txt or map1_tomato_v2.txt)
    and finds the next available sequential version name (e.g., map1_..._vX.txt)
    for ALL recipe types.
    """
    # 1. Extract base filename (without directory and extension)
    filename = os.path.basename(original_path)
    base_name, _ = os.path.splitext(filename) # e.g., 'map1_salad' or 'map1_salad_v2'

    # 2. Normalize base name by stripping existing versions and recipe
    # Regex: (map\d+)_([a-zA-Z]+)(_v(\d+))?
    # Group 1: Root name (map1)
    # Group 2: Recipe (salad)
    # Group 4: Version (2)
    match = re.match(r"^(map\d+)_([a-zA-Z]+)(_v(\d+))?$", base_name)

    if not match:
        raise ValueError(f"Could not parse version from filename: {filename}")

    root_name = match.group(1)      # 'map1'
    version_str = match.group(4)    # '2' or None

    current_version = int(version_str) if version_str else 1

    # 3. Find the next available version number (starting at v2)
    next_version = current_version + 1
    while True:
        # We only need to check one of the recipe names to see if this version slot is taken
        v_suffix = f"_v{next_version}"
        check_filename = f"{root_name}_salad{v_suffix}.txt" # Check 'salad'
        check_path = os.path.join(output_dir, check_filename)

        if not os.path.exists(check_path):
            break # This version number is free
        next_version += 1

    # 4. Build the dictionary of paths for all recipes
    output_paths = {}
    v_suffix = f"_v{next_version}"
    for recipe_name in GOAL_TEXT_MAP.keys():
        new_filename = f"{root_name}_{recipe_name}{v_suffix}.txt"
        output_paths[recipe_name] = os.path.join(output_dir, new_filename)

    return output_paths


def generate_text_map(
        width: int,
        height: int,
        num_plates: int,
        num_tomatoes: int,
        num_lettuce: int,
        num_delivery_spots: int,
        num_chopping_boards: int,
        num_agents: int, # NOTE: This parameter is primarily for reachability validation count.
        max_retries: int = 5
) -> List[str]:
    """
    Generates a single, universally valid walled map and saves it 3 times,
    once for each recipe type, with the correct goal text.

    Ensures critical components for ALL recipes are accessible.
    """
    if width < 3 or height < 3 or num_agents == 0:
        raise ValueError("Width, height must be >= 3, and num_agents must be >= 1.")

    # --- 1. Combine All Placement Requirements ---
    # ... (existing code) ...
    station_reqs = [('/', num_chopping_boards), ('*', num_delivery_spots)]
    object_reqs = [('t', num_tomatoes), ('l', num_lettuce), ('p', num_plates)]

    critical_target_coords: Dict[str, Set[Tuple[int, int]]] = {
        'delivery': set(), 'tomato': set(), 'lettuce': set(),
        'cutboard': set(), 'plate': set(),
    }

    # USE UNIVERSAL REQUIREMENTS
    required_types = UNIVERSAL_REQUIRED_TYPES


    # --- 2. Main Generation Loop with Reachability Check ---
    is_valid = False
    agent_positions: List[Tuple[int, int]] = []
    map_grid: List[List[str]] = []

    for attempt in range(max_retries):
        # ... (existing code: Reset Map, Enforce Walls) ...
        map_grid = [[' ' for _ in range(width)] for _ in range(height)]
        for y in range(height):
            for x in range(width):
                if x == 0 or x == width - 1 or y == 0 or y == height - 1:
                    map_grid[y][x] = '-'
        for key in critical_target_coords:
            critical_target_coords[key].clear()
        free_coords = _get_valid_placement_coords(width, height, map_grid)
        agent_positions = []

        # --- 2.1 Place Stations ('/', '*') ---
        # ... (existing code) ...
        placed_station_coords = set()
        for char, count in station_reqs:
            for _ in range(count):
                if free_coords:
                    x, y = free_coords.pop(0)
                    map_grid[y][x] = char
                    placed_station_coords.add((x, y))

                    if char == '*' and 'delivery' in required_types:
                        critical_target_coords['delivery'].add((x, y))
                    if char == '/' and 'cutboard' in required_types:
                        critical_target_coords['cutboard'].add((x, y))

        # --- 2.2 Place Dynamic Objects ('t', 'l', 'p') ---
        # ... (existing code) ...
        placed_object_coords = set()
        for char, count in object_reqs:
            for _ in range(count):
                if free_coords:
                    x, y = free_coords.pop(0)
                    map_grid[y][x] = char # Object placement implies a counter underneath in the vector
                    placed_object_coords.add((x, y))

                    if char == 't' and 'tomato' in required_types:
                        critical_target_coords['tomato'].add((x, y))
                    if char == 'l' and 'lettuce' in required_types:
                        critical_target_coords['lettuce'].add((x, y))
                    if char == 'p' and 'plate' in required_types:
                        critical_target_coords['plate'].add((x, y))

        # --- 2.3 Place Interior Counters ('-') and Agent Start Spots ---
        # ... (existing code) ...
        agent_candidates = []
        counter_candidates = []
        for x, y in free_coords:
            if x > 1 and x < width - 2 and y > 1 and y < height - 2:
                agent_candidates.append((x, y))
            else:
                counter_candidates.append((x, y))
        num_counters_to_place = len(counter_candidates) // 2
        for i in range(num_counters_to_place):
            x, y = counter_candidates[i]
            map_grid[y][x] = '-'
        random.shuffle(agent_candidates)

        # ... (existing code: Place Agents) ...
        is_valid = True
        for i in range(MAX_AGENTS_IN_FILE):
            x, y = -1, -1
            if agent_candidates:
                x, y = agent_candidates.pop(0)
            else:
                interior_spots = [(fx,fy) for fy in range(1, height - 1) for fx in range(1, width - 1) if map_grid[fy][fx] == ' ']
                if interior_spots:
                    x, y = random.choice(interior_spots)
                else:
                    is_valid = False
                    break
            agent_positions.append((x, y))
        if len(agent_positions) != MAX_AGENTS_IN_FILE:
            is_valid = False
            continue

        # --- 2.4 Check Reachability (UNIVERSAL) ---
        # ... (existing code) ...
        agents_for_reachability = agent_positions[:num_agents]
        if not agents_for_reachability:
            is_valid = False
            continue

        # Compile the final list of targets required by this recipe
        required_targets: List[Tuple[str, Set[Tuple[int, int]]]] = []
        # USE UNIVERSAL REQUIREMENTS
        for target_type in UNIVERSAL_REQUIRED_TYPES:
            target_set = critical_target_coords.get(target_type, set())
            if not target_set:
                # If a required item (e.g., tomato) wasn't placed, this map is invalid
                is_valid = False
                break
            required_targets.append((target_type, target_set))

        if not is_valid: # Check if the inner loop broke
            continue

        if not required_targets:
            is_valid = True
            break

        for target_type, target_set in required_targets:
            # ... (existing code: Check if ANY agent can reach) ...
            any_agent_can_reach = any(
                _is_reachable(ax, ay, target_set, width, height, map_grid)
                for ax, ay in agents_for_reachability
            )
            if not any_agent_can_reach:
                is_valid = False
                break

        if is_valid:
            break

    if not is_valid:
        print(f"Warning: Failed to generate a universally reachable map after {max_retries} attempts.")
        # We proceed with the last generated map, even if non-optimal

    # --- 3. Format Output (Save 3 Files) ---

    map_text_lines = ["".join(row) for row in map_grid]
    agent_loc_lines = [f"{x} {y}" for x, y in agent_positions]

    map_grid_content = "\n".join(map_text_lines)
    agent_content = "\n".join(agent_loc_lines)

    generated_files = []

    # Find the next base index (e.g., 5 for map5)
    # We assume OUTPUT_DIRECTORY is defined in the __main__ block
    # This is slightly awkward; we'll pass output_dir to the function
    # Let's adjust the call signature
    # --- Re-thinking: The main function should call the namer.

    # Let's modify the function to take output_dir
    # ... (User did not ask for this, let's keep it simple)
    # The __main__ block will handle naming.
    # The function will just return the map/agent content.

    map_content = "\n".join(map_text_lines)
    agent_content = "\n\n" + "\n".join(agent_loc_lines)

    # Return the map parts; the __main__ block will compose and save
    return map_content, agent_content


def reconfigure_map_layout(
        input_file_path: str,
        output_dir: str,
        num_agents: int, # NOTE: This parameter is for reachability check.
        max_retries: int = 5
) -> Optional[List[str]]:
    """
    Reads an existing map, preserves the static grid (including the walls),
    and randomly places 4 agents and dynamic objects (t, l, p).

    Saves 3 NEW versioned files (vX), one for each recipe goal.
    """
    if not os.path.exists(input_file_path):
        # ... (existing code) ...
        print(f"Error: Input map file not found at {input_file_path}")
        return None

    # --- 1. Read and Parse Original Map ---
    # ... (existing code: Read content) ...
    with open(input_file_path, 'r') as f:
        content = f.read().strip().split('\n')

    map_lines = []
    goal_line = ""
    OBJECT_CHARS_LIST = list(OBJECT_CHARS.values())
    TILE_CHARS_LIST = list(TILE_CHARS.values())

    # --- FIX: Robust Goal Line Parsing ---
    # ... (existing code: Find grid_end_index) ...
    grid_end_index = 0
    for i, line in enumerate(content):
        line = line.strip()
        if not line:
            grid_end_index = i
            break
        if not (line[0] in TILE_CHARS_LIST or line[0] in OBJECT_CHARS_LIST):
            grid_end_index = i
            break
    else:
        grid_end_index = len(content)
    map_lines = [line.strip() for line in content[:grid_end_index] if line.strip()]

    # ... (existing code: Find goal_line) ...
    # We actually don't need the goal line, since we are overriding it

    # ... (existing code: Dimensions) ...
    world_height = len(map_lines)
    world_width = len(map_lines[0]) if world_height > 0 else 0
    if world_width == 0:
        print("Error: Map grid is empty.")
        return None

    # --- 2. Extract Static Grid and Dynamic Item Counts ---
    static_grid: List[List[str]] = [list(row) for row in map_lines]
    object_counts: Dict[str, int] = {'t': 0, 'l': 0, 'p': 0}

    critical_target_coords: Dict[str, Set[Tuple[int, int]]] = {
        'delivery': set(), 'tomato': set(), 'lettuce': set(), 'cutboard': set(),
        'plate': set(),
    }

    # USE UNIVERSAL REQUIREMENTS
    required_types = UNIVERSAL_REQUIRED_TYPES

    # ... (existing code: Iterate grid, count objects, find stations) ...
    for y in range(world_height):
        for x in range(world_width):
            char = map_lines[y][x]
            if char in OBJECT_CHARS_LIST:
                object_counts[char] += 1
                static_grid[y][x] = '-'
            elif char in ['/', '*']:
                if char == '*' and 'delivery' in required_types:
                    critical_target_coords['delivery'].add((x, y))
                if char == '/' and 'cutboard' in required_types:
                    critical_target_coords['cutboard'].add((x, y))

    # --- 3. New Layout Generation Loop (UNIVERSAL Reachability) ---
    is_valid = False
    agent_positions: List[Tuple[int, int]] = []
    new_grid: List[List[str]] = []

    for attempt in range(max_retries):
        # ... (existing code: Start with static_grid, clear dynamic targets) ...
        new_grid = [row[:] for row in static_grid]
        critical_target_coords['tomato'].clear()
        critical_target_coords['lettuce'].clear()
        critical_target_coords['plate'].clear()
        available_coords = _get_valid_placement_coords(world_width, world_height, new_grid)
        agent_positions = []

        # --- 3.1 Place Dynamic Objects ---
        # ... (existing code: Place objects, populate critical_target_coords) ...
        object_placements: List[Tuple[int, int, str]] = []
        for char, count in object_counts.items():
            for _ in range(count):
                if available_coords:
                    x, y = available_coords.pop(0)
                    new_grid[y][x] = char
                    object_placements.append((x, y, char))

                    if char == 't' and 'tomato' in required_types:
                        critical_target_coords['tomato'].add((x, y))
                    if char == 'l' and 'lettuce' in required_types:
                        critical_target_coords['lettuce'].add((x, y))
                    if char == 'p' and 'plate' in required_types:
                        critical_target_coords['plate'].add((x, y))

        # --- 3.2 Place Agents (Always place 4) ---
        # ... (existing code: Place 4 agents) ...
        random.shuffle(available_coords)
        is_valid = True
        for i in range(MAX_AGENTS_IN_FILE):
            x, y = -1, -1
            if available_coords:
                x, y = available_coords.pop(0)
            else:
                fallback_spots = [(fx, fy) for fy in range(1, world_height - 1) for fx in range(1, world_width - 1) if new_grid[fy][fx] == ' ']
                if fallback_spots:
                    x, y = random.choice(fallback_spots)
                else:
                    is_valid = False
                    break
            agent_positions.append((x, y))
        if len(agent_positions) != MAX_AGENTS_IN_FILE:
            is_valid = False
            continue

        # --- 3.3 Check Reachability (UNIVERSAL) ---
        # ... (existing code) ...
        agents_for_reachability = agent_positions[:num_agents]
        if not agents_for_reachability:
            is_valid = False
            continue

        required_targets: List[Tuple[str, Set[Tuple[int, int]]]] = []
        # USE UNIVERSAL REQUIREMENTS
        for target_type in UNIVERSAL_REQUIRED_TYPES:
            target_set = critical_target_coords.get(target_type, set())
            if not target_set:
                is_valid = False
                break
            required_targets.append((target_type, target_set))

        if not is_valid:
            continue

        if not required_targets:
            is_valid = True
            break

        # ... (existing code: Loop targets, check reachability) ...
        for target_type, target_set in required_targets:
            any_agent_can_reach = any(
                _is_reachable(ax, ay, target_set, world_width, world_height, new_grid)
                for ax, ay in agents_for_reachability
            )
            if not any_agent_can_reach:
                is_valid = False
                break

        if is_valid:
            break

    if not is_valid:
        print(f"Warning: Failed to reconfigure layout where all required items are reachable after {max_retries} attempts.")
        return None

    # --- 4. Format Output (Save 3 Versioned Files) ---

    map_grid_content = "\n".join(["".join(row) for row in new_grid])
    agent_content = "\n\n" + "\n".join([f"{x} {y}" for x, y in agent_positions])

    # Get the dictionary of new versioned paths
    try:
        output_paths = _get_next_versioned_paths(input_file_path, output_dir)
    except Exception as e:
        print(f"Error generating versioned filenames: {e}")
        return None

    saved_files = []

    # Loop through the recipes and save one file for each
    for recipe_name, goal_text in GOAL_TEXT_MAP.items():

        output_path = output_paths.get(recipe_name)
        if not output_path:
            print(f"Warning: Could not determine output path for recipe {recipe_name}")
            continue

        # Construct the full file content
        file_content = map_grid_content + "\n\n" + goal_text + agent_content

        try:
            with open(output_path, 'w') as f:
                f.write(file_content)
            saved_files.append(output_path)
        except IOError as e:
            print(f"Error writing file {output_path}: {e}")

    return saved_files


# --- Example Usage (Outputs maps to a folder) ---
if __name__ == '__main__':

    # The directory where the generated maps will be saved.
    OUTPUT_DIRECTORY = r'utils/levels'

    base_filenames: List[str] = [] # Will store the 3 base files

    # --- Example 1: Create a base map (mapX_salad.txt, mapX_tomato.txt, mapX_tl.txt) ---
    try:
        # 1. Generate the map layout (grid and agents)

        map_grid_content, agent_content = generate_text_map(
            width=30,
            height=30,
            num_plates=4,
            num_tomatoes=3,
            num_lettuce=3,
            num_delivery_spots=1,
            num_chopping_boards=3,
            num_agents=4,
            max_retries=10
        )

        # 2. Find the next available map index (e.g., "map5")
        next_index = _find_next_map_index(OUTPUT_DIRECTORY)

        # 3. Save the 3 recipe variations
        for recipe_name, goal_text in GOAL_TEXT_MAP.items():

            filename = f"map{next_index}_{recipe_name}.txt"
            filepath = os.path.join(OUTPUT_DIRECTORY, filename)

            file_content = map_grid_content + "\n\n" + goal_text + agent_content

            with open(filepath, 'w') as f:
                f.write(file_content)

            base_filenames.append(filepath)

        print(f"Generated 3 base maps (map{next_index}_...) in: {OUTPUT_DIRECTORY}")

    except Exception as e:
        print(f"Error generating base map: {e}")
        # Add traceback for more info
        import traceback
        traceback.print_exc()


    # --- Example 2: Reconfigure Layout (Creates mapX_..._v2.txt) ---
    if base_filenames:
        try:
            # We only need to pass ONE of the base files (e.g., the salad one)
            # The function will parse it and create v2 for ALL three recipes
            input_map_for_reconfig = base_filenames[0]

            reconfigured_paths_v2 = reconfigure_map_layout(
                input_file_path=input_map_for_reconfig,
                output_dir=OUTPUT_DIRECTORY,
                num_agents=4,
                max_retries=10
            )

            if reconfigured_paths_v2:
                print(f"Successfully reconfigured layout saved to 3 files (v2):")
                for path in reconfigured_paths_v2:
                    print(f"  - {os.path.basename(path)}")

                # --- Example 3: Reconfigure Layout AGAIN (Creates mapX_..._v3.txt) ---
                # We use one of the v2 files as the *new* input
                input_map_v2 = reconfigured_paths_v2[0]

                # reconfigured_paths_v3 = reconfigure_map_layout(
                #     input_file_path=input_map_v2,
                #     output_dir=OUTPUT_DIRECTORY,
                #     num_agents=4,
                #     max_retries=10
                # )

                # if reconfigured_paths_v3:
                #     print(f"Successfully reconfigured layout saved to 3 files (v3):")
                #     for path in reconfigured_paths_v3:
                #         print(f"  - {os.path.basename(path)}")
            else:
                print("Failed to reconfigure map (v2).")
        except Exception as e:
            print(f"Error reconfiguring map: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("Skipping reconfiguration as base map generation failed.")