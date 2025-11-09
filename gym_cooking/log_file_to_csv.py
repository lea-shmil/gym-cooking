import re
import csv
import math
from typing import List, Dict, Any, Tuple

# --- Log Data Provided by User ---
# Merged log content for robust testing
# MODIFIED: Removed static log_content, as it will be read from a file.
# log_content = """ ... """

def seconds_to_hmsms(seconds: float) -> str:
    """Converts a float representing seconds into H:M:S:MS format."""
    if seconds is None or seconds == 'N/A' or seconds < 0:
        return "N/A" # Handle cases where time is not applicable

    seconds = abs(seconds)
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    remaining_seconds = seconds % 60

    # Calculate milliseconds from the fractional part of seconds
    milliseconds = math.floor((remaining_seconds - int(remaining_seconds)) * 1000)

    # Format the time as H:M:S:MS
    # Use f-string to ensure two digits for H, M, S, and three for MS
    return f"{hours:02d}:{minutes:02d}:{int(remaining_seconds):02d}:{milliseconds:03d}"

def extract_search_name(search_arg: str) -> str:
    """Extracts a simplified search algorithm name from the --search argument."""
    # Matches 'lazy_greedy' or 'astar' even if they contain parenthetical content
    match = re.match(r"(\w+)\s*\(.*?\)", search_arg)
    if match:
        return match.group(1)

    # Fallback for simple names
    return search_arg

def parse_log_content(log_data: str) -> List[Dict[str, Any]]:
    """Parses the log data line by line and extracts experiment results."""

    # Split the log content into individual lines
    lines = log_data.strip().split('\n')

    results = []
    current_experiment = {}

    # Regex patterns for core data extraction
    p_running = re.compile(r'--level (\S+) --model1 (\S+) --model2 \S+ --search (\S+)')
    p_planning = re.compile(r'Planning completed for \S+ in (\d+\.\d+) seconds')
    p_total_steps = re.compile(r'Agents succeeded after (\d+) steps') # NEW: For total steps
    p_steps = re.compile(r'Agent \S+: Steps taken: (\d+)') # Per agent steps (used for plan if total steps is missing)
    p_exec_time = re.compile(r'Time taken for .*?: (\d+\.\d+) seconds')
    p_success = re.compile(r'Experiment success: (True|False)')
    p_seed = re.compile(r'--seed (\d+)')

    for line in lines:
        # 1. Start of a new experiment block
        m_running = p_running.search(line)
        if m_running:
            # If we have data from a previous experiment, save it before starting a new one
            if current_experiment:
                # Remove the temporary flag before saving
                if '_total_steps_override' in current_experiment:
                    del current_experiment['_total_steps_override']
                results.append(current_experiment)

            # --- KEYERROR FIX ---
            # Initialize all keys for the new experiment dictionary
            current_experiment = {
                'Alg.': 'N/A',
                'Map': m_running.group(1),
                'Goal': 'N/A', # ADDED: New column for the goal
                'Instance': 'N/A', # RENAMED from GoalInstance
                'Planning time (s)': 'N/A',
                'Execution CPU time (s)': 'N/A',
                'Steps': 'N/A',
                '_total_steps_override': False, # Flag to prevent overwriting with agent-specific steps
                'Success': 'F'
            }

            # Extract Algorithm
            model_type = m_running.group(2)
            search_arg = m_running.group(3)
            search_name = extract_search_name(search_arg)

            # Only attach search algorithm for 'plan' agents
            if model_type == 'plan':
                current_experiment['Alg.'] = f"{model_type} ({search_name})"
            else:
                current_experiment['Alg.'] = model_type

            # Extract Seed (for Instance)
            m_seed = p_seed.search(line)
            if m_seed:
                current_experiment['Instance'] = m_seed.group(1) # RENAMED

            # --- NEW FEATURE: Extract Goal from Map name ---
            map_full = current_experiment['Map']
            parts = map_full.split('_')
            if len(parts) > 1:
                current_experiment['Goal'] = parts[-1]

        # 2. Extract Total Steps (Priority 1)
        m_total_steps = p_total_steps.search(line)
        if m_total_steps and current_experiment:
            steps_val = int(m_total_steps.group(1))

            # --- FIXED LOGIC ---
            # We want to capture the FIRST non-zero "Agents succeeded" line.

            # If we find a non-zero value, lock it in.
            if steps_val > 0:
                current_experiment['Steps'] = steps_val
                current_experiment['_total_steps_override'] = True
            # If we find a zero value, only set it if we haven't already locked in a non-zero value.
            elif steps_val == 0 and not current_experiment['_total_steps_override']:
                current_experiment['Steps'] = 0
                current_experiment['_total_steps_override'] = True

        # 3. Extract Planning Time
        m_planning = p_planning.search(line)
        if m_planning and current_experiment:
            current_experiment['Planning time (s)'] = float(m_planning.group(1))

        # 4. Extract Steps (Agent-specific, Priority 2: ONLY used if total steps was not found)
        m_steps = p_steps.search(line)
        if m_steps and current_experiment and not current_experiment['_total_steps_override']:
            # This is the line we rely on for plan agents where the 'Agents succeeded...' line is missing.
            current_experiment['Steps'] = int(m_steps.group(1))

        # --- CPU TIME FIX ---
        # 5. Extract Execution Time
        m_exec_time = p_exec_time.search(line)
        if m_exec_time and current_experiment:
            current_experiment['Execution CPU time (s)'] = float(m_exec_time.group(1))

        # 6. Extract Success
        m_success = p_success.search(line)
        if m_success and current_experiment:
            # Map True to 'Y' and False to 'F'
            current_experiment['Success'] = 'Y' if m_success.group(1) == 'True' else 'F'

    # Append the last processed experiment
    if current_experiment:
        # Remove the temporary flag before saving
        if '_total_steps_override' in current_experiment:
            del current_experiment['_total_steps_override']
        results.append(current_experiment)

    return results

def process_and_save_results(parsed_data: List[Dict[str, Any]], output_filename: str = 'experiment_results.csv'):
    """Converts the parsed data, applies time formatting, and saves to a CSV file."""

    # --- FORMAT FIX ---
    # Define the final header order based on user request
    fieldnames = [
        'Alg.',
        'Map',
        'Goal',
        'Instance',
        'Planning time(H:M:S:MS)',
        'Execution CPU time(H:M:S:MS)',
        'Steps',
        'Success'
    ]

    final_rows = []
    for row in parsed_data:
        # --- FORMAT FIX ---
        new_row = {
            'Alg.': row['Alg.'],
            'Map': row['Map'],
            'Goal': row['Goal'],
            'Instance': row['Instance'], # RENAMED
            'Steps': row['Steps'],
            'Success': row['Success']
        }

        # Extract raw times
        raw_planning_time = row['Planning time (s)']
        raw_exec_time = row['Execution CPU time (s)']

        # Apply H:M:S:MS formatting and add to the new row with the exact key
        new_row['Planning time(H:M:S:MS)'] = seconds_to_hmsms(raw_planning_time)
        new_row['Execution CPU time(H:M:S:MS)'] = seconds_to_hmsms(raw_exec_time)

        final_rows.append(new_row)

    # Write to CSV
    try:
        with open(output_filename, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(final_rows)
        print(f"Successfully generated and saved results to '{output_filename}'")
    except Exception as e:
        print(f"An error occurred while writing the CSV file: {e}")


# --- Main execution block ---
if __name__ == "__main__":

    # MODIFIED: This block now reads from 'experiment_log.txt'
    # as seen in your local file path.
    try:
        with open('experiment_log.txt', 'r') as f:
            log_content = f.read()
    except FileNotFoundError:
        print("Error: 'experiment_log.txt' not found.")
        print("Please make sure the log file is in the same directory as the script.")
        exit()

    # 1. Parse the log content
    parsed_results = parse_log_content(log_content)

    # 2. Process and save the results to a CSV file
    process_and_save_results(parsed_results, 'experiment_results.csv')