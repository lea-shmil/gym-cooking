from collections import OrderedDict
import numpy as np
import os

import string
from pathlib import Path
from gymnasium.spaces.utils import flatdim, Box

def get_problem_template(template_file_path: Path) -> string.Template:
    """Extract the template object from the template file.

    :return: the template object.
    """
    with open(template_file_path, "rt") as template_file:
        text = template_file.read()
        return string.Template(text)





class GymPDDL:
    def __init__(self, env, output_dir="solutions", do_learn=True, goal=-1):
        self.goal = goal
        print(f"this is env {env} and env type is {type(env)} and env observation space is {env.observation_space}")
        self.env = env.unwrapped
        print(f"this is env {env} and env type is {type(env)} and env observation space is {env.observation_space}")
        self.observation_space = env.observation_space
        self.action_space = env.action_space
        self.domain_name = env.spec.id

        self.state_dict = None
        self.round = lambda state: state  # precision, can use round

        # create domain file
        self.output_dir = output_dir

        self.action_type = type(self.action_space)

        if self.action_type == Box:
            self.selection_space = {(i / 100): f"p{i}" for i in range(101)}

            # can do normalization here
            # low = abs(float(self.action_space.low_repr))
            # high = abs(float(self.action_space.high_repr))
            # self.norm = lambda action: round(((action + high) / (high + low)) + 5e-4, 3)

            self.norm = lambda action: action

        if do_learn:
            self.generate_domain(
                self.domain_name,
                flatdim(self.observation_space),
                flatdim(self.action_space),
            )

        i = 1
        while os.path.exists(f"{output_dir}/pfile{i}.trajectory"):
            i += 1
        self.file_index = i

    def reset(self, vector, reset_reward=True):
        if reset_reward:
            self.total_reward = 0

        self.state_into_dict(vector)
        init_state = [self.round(v) for v in vector]

        return init_state

    def state_into_dict(self, state, reward=0):
        """takes the state and puts it into model"""
        if type(state) is tuple:
            state = np.array(state)

        self.add_reward(reward)

        self.state_dict = OrderedDict(
            {
                "s": state.ravel("f"),
                "r": [self.total_reward],
            }
        )

    def write_action(self, actions):
        if self.action_type == Box:
            self.file.write(f"(operators:")
            for i, action in enumerate(actions):
                self.file.write(
                    f" (a{i} {self.selection_space[self.round(self.norm(action))]})"
                )
        else:
            self.file.write(f"(operator: (a{actions})")

        self.file.write(f")\n")

    def write_state(self, state, reward: float = 0, game_over: bool = False):
        self.state_into_dict(state, reward)
        self.file.write("(:state")
        if game_over:
            self.file.write(" (game_over)")
        self.save_state()

    def write_game_over(self, state, reward: float = 0):
        self.write_action("_game_over")
        self.write_state(state, reward, True)

    def save_state(self):
        for state, value in self.state_dict.items():
            for i, v in enumerate(value):
                self.file.write(f" (= ({state}{i}) {self.round(v)})")
        self.file.write(")\n")

    def start_record(self, obs):
        self.file = open(f"{self.output_dir}/pfile{self.file_index}.trajectory", "w")
        self.file.write("((:init")
        self.generate_problem(obs)
        self.save_state()

    def generate_problem(self, obs, reset_reward=True):
        init_state = self.reset(obs, reset_reward)
        self._generate_problem("p1", init_state)

    def set_goal(self, goal):
        self.goal = goal

    def add_reward(self, reward):
        self.total_reward += reward

    def end_record(self):
        self.file.write(")")
        self.file.close()
        self.file_index += 1

    def generate_domain(
            self,
            instance_name: str,
            state_space_size: int,
            action_space_size: int,
    ) -> None:
        """
        Generate a single basic planning problem instance.

        :instance_name: the name of the problem instance.
        :trees_in_map: the number of trees in the map.
        :count_log_in_inventory: the number of logs in the inventory.
        """

        template = get_problem_template(Path("utils/domain_template.pddl"))
        template_mapping = {
            "instance_name": instance_name,
            "state_space": " ".join([f"(s{i})" for i in range(state_space_size)])
                           + " (r0)",
        }

        if self.action_type == Box:
            template_mapping["state_space"] = (
                    "(parameter_amount ?p - parameter) " + template_mapping["state_space"]
            )

            template_mapping["types"] = "(:types parameter - object)"

            template_mapping["action_space"] = " ".join(
                [
                    f"(:action a{i} :parameters (?p - parameter) :precondition () :effect ())"
                    for i in range(action_space_size)
                ]
            )
        else:
            template_mapping["types"] = ""

            template_mapping["action_space"] = " ".join(
                [
                    f"(:action a{i} :parameters () :precondition () :effect ())"
                    for i in range(action_space_size)
                ]
            )

        domain = f"{self.output_dir}/domain.pddl"
        with open(domain, "wt") as domain_file:
            domain_file.write(template.substitute(template_mapping))

    def _generate_problem(
            self,
            instance_name: str,
            initial_state: list,
    ) -> None:
        """
        Generate a single basic planning problem instance.

        :instance_name: the name of the problem instance.
        :trees_in_map: the number of trees in the map.
        :count_log_in_inventory: the number of logs in the inventory.
        """
        template = get_problem_template(Path("utils/problem_template.pddl"))
        template_mapping = {
            "instance_name": instance_name,
            "domain_name": self.domain_name,
            "initial_state": " ".join(
                [f"(= (s{i}) {v:.4f})" for i, v in enumerate(initial_state)]
                + [f"(= (r0) {self.total_reward:.4f})"]
            ),
        }

        if self.action_type == Box:
            template_mapping["objects"] = (
                    "(:objects "
                    + " ".join(
                [
                    f"(= (parameter_amount {p}) {v})"
                    for v, p in self.selection_space.items()
                ]
            )
                    + " - parameter)"
            )
        else:
            template_mapping["objects"] = ""

        if self.goal == -1:
            self.goal = self.env.spec.reward_threshold
            if self.goal is None:
                self.goal = 1000
        template_mapping["goal_state"] = f"(>= (r0) {self.goal})"

        problem = f"{self.output_dir}/problem.pddl"
        with open(problem, "wt") as problem_file:
            problem_file.write(template.substitute(template_mapping))
