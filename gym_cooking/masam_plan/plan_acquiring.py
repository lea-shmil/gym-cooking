from pprint import pprint
from typing import List
from time import sleep
import requests
import re


class PlanningDomainsAPIError(Exception):
    """Raised when a valid response cannot be obtained from the planning.domains solver."""

    def __init__(self, message):
        super().__init__(message)


def get_api_response(delays: List[int]):
    if delays:
        sleep(delays[0])
        try:
            # different planners can be used by changing the service_url between package and solve
            # might requrie changing the key names in the following code
            # here are the names of the planners to add /package/name_here/solve

            # FD Planner [lama-first] does not work

            # Satisficing classical planning [dual-bfws-ffparser] works

            # Optimal classical planning [delfi] does not work

            #  numeric planning [enhsp] - timeout
            #
            # # PDDL3 support [optic] does not work

            # # Temporal planning  [tfd] does not work

            service_url = "https://solver.planning.domains:5001/package/dual-bfws-ffparser/solve"
            solve_request = requests.post(service_url, json=data, headers=headers).json()
            celery_result = requests.get("https://solver.planning.domains:5001/" +
                                         solve_request['result'])
            while celery_result.json().get("status", "") == 'PENDING':
                sleep(delays[0])
                celery_result = requests.get("https://solver.planning.domains:5001/" +
                                             solve_request['result'])
            # pprint(celery_result.json())
            sas_plan = celery_result.json()['result']['output']['plan']
            actions_with_objects = re.findall(r'\((.*?)\)', sas_plan)

            plan_list = [f'({action})' for action in actions_with_objects]
            return plan_list

        except TypeError:
            return get_api_response(delays[1:])


if __name__ == "__main__":

    level_name = "partial-divider_tomato"

    string_level = "../utils/pddls/" + level_name + ".pddl"
    data = {
        "domain": open("../utils/pddls/gym-cooking.pddl", "r").read(),
        "problem": open(string_level, "r").read(),
    }

    headers = {"persistent": "true"}

    plan = get_api_response([0, 1, 3, 5, 10])
    if plan is None:
        raise PlanningDomainsAPIError(
            "Could not get a valid response from the planning.domains solver after 5 attempts.",
        )
    else:
        print("Plan obtained successfully")
        # write the plan to a file under ../utils/plants with the name level_name + "plan.txt"
        string_plan = "../utils/plans/" + level_name + "_plan.txt"
        with open(string_plan, "w") as f:
            for action in plan:
                f.write(action + "\n")
