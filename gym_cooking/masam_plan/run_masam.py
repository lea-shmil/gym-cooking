from pathlib import Path
from pddl_plus_parser.lisp_parsers.pddl_tokenizer import PDDLTokenizer

from pddl_plus_parser.models import Observation

from gym_cooking.masam_plan.sam_learning.learners.multi_agent_sam import MultiAgentSAM, MultiAgentObservation
from pddl_plus_parser.lisp_parsers import DomainParser, TrajectoryParser

if __name__ == "__main__":
    # take out pddl trajectories file
    multi_agent_observation = []
    trajectory_file = r"..\misc\metrics\trajectories\trajectory_20251029-221644.pddl"
    with open(trajectory_file, "r") as f:
        for line in f:
            if line.strip():  # skip empty lines
                multi_agent_observation.append(line.strip())

    # build agent?
    domain_path = Path(r"..\utils\pddls\gym-cooking.pddl")
    domain_parser = DomainParser(domain_path, partial_parsing=True).parse_domain()
    masam_agent = MultiAgentSAM(domain_parser)

    # parse trajectories
    trajectory_path = Path(trajectory_file)
    executing_agents = ["a1", "a2", "a3", "a4"]

    tokenizer = PDDLTokenizer(file_path=trajectory_path)
    observation_expression = tokenizer.parse()
    print(observation_expression[1])

    MA_observation = TrajectoryParser(domain_parser).parse_trajectory(trajectory_path, executing_agents)

    learned_model, learning_report = masam_agent.learn_combined_action_model([MA_observation])

    print(learned_model)
    print(learned_model.to_pddl())

