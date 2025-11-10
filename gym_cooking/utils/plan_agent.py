import os
import re
import subprocess
import time
from pddl_plus_parser.multi_agent import PlanConverter
from pddl_plus_parser.lisp_parsers import DomainParser, ProblemParser
import logging

from typing import Tuple

from gym_cooking.utils.pddl_problem_generator import text_map_to_vector, state_to_pddl
from gym_cooking.utils.plans.transfer_single import parallel_execution

logging.root.setLevel(logging.ERROR)


class plan_agent:
    def __init__(self, name, id_color, recipes, arglist, env, logger, evaluator="hcea=cea()",
                 search="lazy_greedy([hcea], preferred=[hcea])"):
        self.name = name
        self.color = id_color
        self.recipes = recipes
        self.arglist = arglist
        self.env = env
        self.evaluator = evaluator
        self.search = search
        self.logger = logger
        self.plan_file_path = f"utils/plans/{self.arglist.level}_plan.txt"  # Path to the plan file
        self.actions_queue = self._load_plan()
        self.steps_taken = 0

    def _load_plan(self):
        # Define base directory
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # Keep going up one level until we find the sentinel file.
        while not os.path.exists(os.path.join(current_dir, "main.py")):
            parent_dir = os.path.dirname(current_dir)
            if parent_dir == current_dir:
                # We've hit the filesystem root and didn't find it.
                raise FileNotFoundError(f"Could not find project root (marker file main.py not found).")
            current_dir = parent_dir

        print(current_dir)
        # Convert relative paths to absolute paths
        domain_file = os.path.abspath(os.path.join(current_dir, "gym_cooking", "utils", "pddls", "gym-cooking.pddl"))
        #domain_file = os.path.abspath(os.path.join(current_dir,"gym_cooking", "masam_plan", "domain.pddl"))

        problem_file = os.path.abspath(
            os.path.join(current_dir, "gym_cooking", "utils", "pddls", f"{self.arglist.level}.pddl"))
        planner_script = os.path.abspath(
            os.path.join(current_dir, "gym_cooking", "downward-release-24.06.1", "fast-downward.py"))

        # Ensure paths are compatible with the operating system
        if os.name == "posix":  # Unix-like systems
            domain_file = domain_file.replace("\\", "/")
            problem_file = problem_file.replace("\\", "/")
            planner_script = planner_script.replace("\\", "/")
        else:  # Windows
            domain_file = domain_file.replace("/", "\\")
            problem_file = problem_file.replace("/", "\\")
            planner_script = planner_script.replace("/", "\\")

        # Ensure the plan directory exists
        os.makedirs(os.path.dirname(self.plan_file_path), exist_ok=True)

        if self.name == "agent-1":
            #updating pddl based on current number of agents
            map_file = os.path.join(current_dir, "gym_cooking", "utils", "levels", f"{self.arglist.level}.txt")
            state_vector, width, height, num_agents, num_objects = text_map_to_vector(map_file, self.env.arglist.num_agents)
            state_to_pddl(state_vector, width, height, num_agents, num_objects, self.arglist.level, problem_file)
            # Start timing the planning process
            start_time = time.perf_counter()

            # Call the Fast Downward planner
            command = [
                "python", planner_script,
                domain_file,
                problem_file,
                f"{self.evaluator}",
                f"{self.search}",
                f"{self.env.seed}"
            ]

            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            print(result)

            sas_plan_path = os.path.join(current_dir, "sas_plan")

            #  remove last line from sas_plan file
            with open(sas_plan_path, "r") as file:
                lines = file.readlines()
            # Remove the last line
            lines = lines[:-1]
            with open(sas_plan_path, "w") as file:
                file.writelines(lines)
            agent_names = ["a1", "a2", "a3", "a4"][:self.env.arglist.num_agents]
            result = parallel_execution(domain_file, problem_file, sas_plan_path, agent_names)
            print(result)
            if os.path.exists(sas_plan_path):
                with open(self.plan_file_path, "w") as f_out:
                    for joint_action in result:
                        # joint_action.actions is a list of ActionCall objects
                        f_out.write(f"({joint_action})\n")

                end_time = time.perf_counter()
                elapsed_time = end_time - start_time
                # Log the planning time
                self.logger.info(f"Planning completed for {self.arglist.level} in {elapsed_time:.8f} seconds")
            else:
                self.logger.error(f"Planner did not produce the plan file at expected location: {sas_plan_path}")
                self.logger.error(f"Experiment success: False")
                return []

            # Verify the plan file was created
            if not os.path.exists(self.plan_file_path):
                raise FileNotFoundError(f"Plan file {self.plan_file_path} was not created.")

        with open(self.plan_file_path, "r") as file:
            lines = file.readlines()

        actions = []
        for i, line in enumerate(lines):
            line = line.strip()
            if line == "" or line.isspace() or line.startswith("(REACH-GOAL") or line.startswith(";"):
                # Skip REACH-GOAL
                continue
            elif line.startswith("(DELIVER") and i == len(lines) - 1:
                # Include DELIVER if it's the last action
                actions.append(("(DELIVER", None))
            else:
                actions.append(self._parse_action(line))
        print(f"Agent {self.name} loaded actions: {actions}")
        return actions

    def _parse_coords(self, loc_string):
        """
        Parses a location string like 'x19y2' or 'x4y1' into (x, y) integers.
        """
        # This regex finds one or more digits (\d+) after 'x' and 'y'
        match = re.search(r"x(\d+)y(\d+)", loc_string)

        if not match:
            print(f"Error: Could not parse coordinates from '{loc_string}'")
            return 0, 0

        x = int(match.group(1)) # The first group (digits after x)
        y = int(match.group(2)) # The second group (digits after y)
        return x, y

    def _parse_action(self, action_line: str):
        """
        Parse a textual action line into a (dx, dy) environment action.
        This version correctly handles multi-digit coordinates.
        """
        # Find all actions in the line, e.g., "(move a1...)" "(move a2...)"
        actions = re.findall(r'\(([^()]*)\)', action_line)

        # Map actions by their order of appearance
        # pair['1'] = "move a1 x19y2 x18y2"
        # pair['2'] = "move a2 x5y5 x5y6"
        pair = {}
        if len(actions) >= 1:
            pair['1'] = actions[0]
        if len(actions) >= 2:
            pair['2'] = actions[1]
        if len(actions) >= 3:
            pair['3'] = actions[2]
        if len(actions) >= 4:
            pair['4'] = actions[3]

        # Get the index for this agent (e.g., 'agent-1' -> '1')
        agent_index = self.name.split('-')[1]

        if agent_index not in pair:
            # print(f"No action found for {self.name} in line.")
            return 0, 0 # No-op

        action_str = pair[agent_index]  # e.g., "move a1 x19y2 x18y2"

        # Check for no-op
        if "nop" in action_str:
            return 0, 0

        action_parts = action_str.split(" ")

        if len(action_parts) < 4:
            # Not a valid movement/interaction action
            return 0, 0

        start_str = action_parts[2]  # e.g., "x19y2"
        end_str = action_parts[3]    # e.g., "x18y2"

        # --- THIS IS THE FIX ---
        # Use the new regex-based parser instead of fixed indices
        start_x, start_y = self._parse_coords(start_str)
        end_x, end_y = self._parse_coords(end_str)
        # --- END OF FIX ---

        # Calculate the movement direction
        dx, dy = end_x - start_x, end_y - start_y

        return dx, dy


    def select_action(self):
        """Return the next action for the agent."""
        if not self.actions_queue:
            raise RuntimeError("No more actions in the plan.")
        self.steps_taken += 1
        print(f"Agent {self.name} executing action: {self.actions_queue[0]}")
        return self.actions_queue.pop(0)

    def parallel_execution(self, domain: str, problem: str, agent_names: list, suffix: str = "") -> list:
        """
        Transform a single-agent PDDL solution file to a multi-agent PDDL solution file
        and save the joint actions to a file in the same directory as the problem file.

        Parameters:
            domain (str): The path of the PDDL domain file.
            problem (str): The path of the PDDL problem file.
            agent_names (list): List of all the agents' names.
            suffix (str): Optional suffix for the solution file.

        Returns:
            list: A list of joint actions for the agents.
        """
        from pathlib import Path
        # Parse the domain and problem files
        domain_parser = DomainParser(domain).parse_domain()
        uproblem = ProblemParser(problem_path=problem, domain=domain_parser)
        # Convert the single-agent plan to a multi-agent plan
        plan_converter = PlanConverter(domain_parser)
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
        plan_file_path = os.path.abspath(
            os.path.join(base_dir, "gym_cooking", "utils", "plans", f"{self.arglist.level}_plan.txt")
        )
        joint_actions = plan_converter.convert_plan(
            uproblem.parse_problem(), plan_file_path, agent_names
        )
        with open(problem, "w") as f:
            f.write("\n; Joint Actions\n")
            for action in joint_actions:
                f.write(f"{action}\n")
        return joint_actions
