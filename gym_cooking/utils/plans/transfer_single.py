# This code is written by Yarin Benyamin.
# It is a work in progress of the code from the following link:
# https://github.com/SPL-BGU/ActionBasedNovelty/blob/main/heuristic_functions.py

from pddl_plus_parser.multi_agent import PlanConverter
from pddl_plus_parser.lisp_parsers import DomainParser, ProblemParser
import logging
import os

logging.root.setLevel(logging.ERROR)


# Configure the PlanConverter logger
plan_converter_logger = logging.getLogger("pddl_plus_parser.multi_agent.PlanConverter")
plan_converter_logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)
plan_converter_logger.addHandler(console_handler)


def parallel_execution(domain: str, problem: str, solution: str, agent_names: list, suffix: str = "") -> str:
    """Transform a single-agent PDDL solution file to a multi-agent PDDL solution file."""
    # Check if the domain file exists
    if not os.path.exists(domain):
        raise FileNotFoundError(f"Domain file not found: {domain}")
    # Check if the problem file exists
    if not os.path.exists(problem):
        raise FileNotFoundError(f"Problem file not found: {problem}")
    # Check if the solution file exists
    if not os.path.exists(solution):
        raise FileNotFoundError(f"Solution file not found: {solution}")

    # Log the content of the domain file for debugging
    with open(domain, "r") as domain_file:
        domain_content = domain_file.read()
        print(f"Domain file content:\n{domain_content}")

    # Parse the domain and problem files
    domain_parser = DomainParser(domain)
    try:
        parsed_domain = domain_parser.parse_domain()
    except IndexError as e:
        print("Error parsing the domain file. Please check the PDDL syntax.")
        raise e

    uproblem = ProblemParser(problem_path=problem, domain=parsed_domain)

    # Convert the single-agent plan to a multi-agent plan
    plan_converter = PlanConverter(parsed_domain)
    print(solution)
    print(agent_names)
    print(uproblem.parse_problem())
    joint_actions = plan_converter.convert_plan(
        uproblem.parse_problem(), solution, agent_names
    )
    return joint_actions
