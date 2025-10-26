import os
import re
import subprocess
import time
from pddl_plus_parser.multi_agent import PlanConverter
from pddl_plus_parser.lisp_parsers import DomainParser, ProblemParser
import logging

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
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))

        # Convert relative paths to absolute paths
        domain_file = os.path.abspath(os.path.join(base_dir, "gym_cooking", "utils", "pddls", "gym-cooking.pddl"))
        problem_file = os.path.abspath(
            os.path.join(base_dir, "gym_cooking", "utils", "pddls", f"{self.arglist.level}.pddl"))
        planner_script = os.path.abspath(
            os.path.join(base_dir, "gym_cooking", "downward-release-24.06.1", "fast-downward.py"))

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

            # Construct path to the sas_plan file inside gym_cooking directory
            # gym_cooking/utils -> gym_cooking C:\Users\Administrator\Documents\GitHub\gym-cooking\gym_cooking\sas_plan
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            sas_plan_path = os.path.join(base_dir, "sas_plan")

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

    def _parse_action(self, action_line):
        """Parse a textual action into an environment action."""
        actions = re.findall(r'\(([^()]*)\)', action_line)
        pair = {}
        if len(actions) >= 1:
            pair['1'] = actions[0]
        if len(actions) >= 2:
            pair['2'] = actions[1]
        if len(actions) >= 3:
            pair['3'] = actions[2]
        if len(actions) >= 4:
            pair['4'] = actions[3]

        action = pair[self.name.split('-')[1]]  # agent 1 -> pair[1]
        print(action)
        if action == "nop ":  # Check if the action is for this agent
            return 0, 0  # No-op if not for this agent
        action = action.split(" ")
        start = action[2]  # e.g., X4Y1
        end = action[3]    # e.g., X5Y1

        # Calculate the movement direction
        start_x, start_y = int(start[1]), int(start[3])
        end_x, end_y = int(end[1]), int(end[3])
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
