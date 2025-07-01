# This code is written by Yarin Benyamin.
# It is an work in progress of the code from the following link:
# https://github.com/SPL-BGU/ActionBasedNovelty/blob/main/heuristic_functions.py
import re

from pddl_plus_parser.models import ActionCall
from pddl_plus_parser.multi_agent import PlanConverter

from pddl_plus_parser.lisp_parsers import DomainParser, ProblemParser

import logging

logging.root.setLevel(logging.ERROR)

from pathlib import Path


# Configure the PlanConverter logger
plan_converter_logger = logging.getLogger("pddl_plus_parser.multi_agent.PlanConverter")
plan_converter_logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)
plan_converter_logger.addHandler(console_handler)

def parallel_execution(
    domain: str, problem: str, solution: str,  agent_names: list, suffix: str = ""
) -> str:
    """Transform a single-agent PDDL sloution file to a multi-agent PDDL sloution file.

    domain: str
        The path of the PDDL domain file.
    problem: str
        The path of the PDDL problem file.
    agent_types: list
        List of all the agents names.
    """


    domain_parser = DomainParser(domain).parse_domain()

    uproblem = ProblemParser(problem_path=problem, domain=domain_parser)

    plan_converter = PlanConverter(domain_parser)

    joint_actions = plan_converter.convert_plan(
        uproblem.parse_problem(), solution, agent_names
    )
    print(len(joint_actions), "joint actions found in the solution file.")
    return joint_actions

if __name__ == "__main__":
    domain = Path(r"C:\Users\leash\Documents\GitHub\gym-cooking\gym_cooking\utils\pddls\gym-cooking.pddl")
    problem = Path(r"C:\Users\leash\Documents\GitHub\gym-cooking\gym_cooking\utils\pddls\open-divider_salad.pddl")
    solution = Path(r"C:\Users\leash\Documents\GitHub\gym-cooking\gym_cooking\utils\plans\open-divider_salad_plan.txt")
    agent_names = ["a1", "a2"]
    suffix = ""
    result = parallel_execution(domain, problem, solution, agent_names, suffix)
    print(result)

