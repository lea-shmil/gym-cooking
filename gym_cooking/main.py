# from environment import OvercookedEnvironment
# from gym_cooking.envs import OvercookedEnvironment
import os

from gym_cooking.envs.OvercookedRLWrapper import OvercookedRLWrapper
from gym_cooking.utils.plan_agent import plan_agent
from recipe_planner.recipe import *
from utils.world import World
from utils.agent import RealAgent, SimAgent, COLORS
from utils.RLAgent import RLAgent
from utils.core import *
from misc.game.gameplay import GamePlay
from misc.metrics.metrics_bag import Bag

import numpy as np
import random
import argparse
from collections import namedtuple

#from utils.logger import RecordTrajectories
import gym
import time
import logging

def setup_logger(log_file):
    """Set up a logger to log to both console and file."""
    logger = logging.getLogger("ExperimentLogger")
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(message)s')

    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger

def parse_arguments():
    parser = argparse.ArgumentParser("Overcooked 2 argument parser")

    #planning agents
    parser.add_argument("--evaluator", type=str, default="hcea=cea()", help="Evaluator for the planner")
    parser.add_argument("--search", type=str, default="lazy_greedy([hcea], preferred=[hcea])", help="Search strategy for the planner")


    # Environment
    parser.add_argument("--level", type=str, required=True)
    parser.add_argument("--num-agents", type=int, required=True)
    parser.add_argument("--max-num-timesteps", type=int, default=100, help="Max number of timesteps to run")
    parser.add_argument("--max-num-subtasks", type=int, default=14, help="Max number of subtasks for recipe")
    parser.add_argument("--seed", type=int, default=1, help="Fix pseudorandom seed")
    parser.add_argument("--with-image-obs", action="store_true", default=False, help="Return observations as images (instead of objects)")

    # Delegation Planner
    parser.add_argument("--beta", type=float, default=1.3, help="Beta for softmax in Bayesian delegation updates")

    # Navigation Planner
    parser.add_argument("--alpha", type=float, default=0.01, help="Alpha for BRTDP")
    parser.add_argument("--tau", type=int, default=2, help="Normalize v diff")
    parser.add_argument("--cap", type=int, default=75, help="Max number of steps in each main loop of BRTDP")
    parser.add_argument("--main-cap", type=int, default=100, help="Max number of main loops in each run of BRTDP")

    # Visualizations
    parser.add_argument("--play", action="store_true", default=False, help="Play interactive game with keys")
    parser.add_argument("--record", action="store_true", default=False, help="Save observation at each time step as an image in misc/game/record")

    # Models
    # Valid options: `bd` = Bayes Delegation; `up` = Uniform Priors
    # `dc` = Divide & Conquer; `fb` = Fixed Beliefs; `greedy` = Greedy
    parser.add_argument("--model1", type=str, default=None, help="Model type for agent 1 (bd, up, dc, fb, or greedy)")
    parser.add_argument("--model2", type=str, default=None, help="Model type for agent 2 (bd, up, dc, fb, or greedy)")
    parser.add_argument("--model3", type=str, default=None, help="Model type for agent 3 (bd, up, dc, fb, or greedy)")
    parser.add_argument("--model4", type=str, default=None, help="Model type for agent 4 (bd, up, dc, fb, or greedy)")

    return parser.parse_args()


def fix_seed(seed):
    np.random.seed(seed)
    random.seed(seed)


def initialize_agents(arglist, env, logger):
    real_agents = []

    with open('utils/levels/{}.txt'.format(arglist.level), 'r') as f:
        phase = 1
        recipes = []
        for line in f:
            line = line.strip('\n')
            if line == '':
                phase += 1

            # phase 2: read in recipe list
            elif phase == 2:
                recipes.append(globals()[line]())

            # phase 3: read in agent locations (up to num_agents)
            elif phase == 3:
                if len(real_agents) < arglist.num_agents:
                    loc = line.split(' ')
                    model_type = getattr(arglist, f"model{len(real_agents) + 1}")
                    if model_type == 'rl':
                        # Use your custom RL agent
                        real_agent = RLAgent(
                            name='agent-' + str(len(real_agents) + 1),
                            id_color=COLORS[len(real_agents)],
                            recipes=recipes,
                            arglist=arglist,
                            env=OvercookedRLWrapper(env)
                        )
                    elif model_type == 'plan':
                        #using plan agent
                        real_agent = plan_agent(
                            name='agent-' + str(len(real_agents) + 1),
                            id_color=COLORS[len(real_agents)],
                            recipes=recipes,
                            arglist=arglist,
                            env=env,
                            logger=logger,  # Pass the logger instance
                            evaluator=arglist.evaluator,
                            search=arglist.search
                        )
                    else:
                        # Default to RealAgent
                        real_agent = RealAgent(
                            arglist=arglist,
                            name='agent-' + str(len(real_agents) + 1),
                            id_color=COLORS[len(real_agents)],
                            recipes=recipes
                        )
                    real_agents.append(real_agent)

    return real_agents

def main_loop(arglist):
    """The main loop for running experiments."""
    print("Initializing environment and agents.")

    log_file = "experiment_log.txt"
    logger = setup_logger(log_file)

    logger.info(f"Running: python main.py --num-agents {arglist.num_agents} --seed {arglist.seed} "
                f"--level {arglist.level} --model1 {arglist.model1} --model2 {arglist.model2} "
                f"--search {arglist.search} --evaluator {arglist.evaluator} ")


    env = gym.envs.make("gym_cooking:overcookedEnv-v0", arglist=arglist)
    obs = env.reset()

    # game = GameVisualize(env)
    real_agents = initialize_agents(arglist=arglist, env=env, logger=logger)
    #super_agent = RLSuperAgent(num_agents=

    # Start timing the agent's execution
    agent_start_time = time.time()

    rl_flag = True
    # if there is an rl agent change env to rl wrapper
    if isinstance(real_agents[0], RLAgent):
        env = OvercookedRLWrapper(env)

    # Info bag for saving pkl files
    bag = Bag(arglist=arglist, filename=env.filename)
    bag.set_recipe(recipe_subtasks=env.all_subtasks)

    info = {"t": 0}

    while (not env.done()) and rl_flag:

        action_dict = {}
        for agent in real_agents:
            if not isinstance(agent, RLAgent):
                if isinstance(agent, plan_agent):
                    action = agent.select_action()
                else:
                    action = agent.select_action(obs=obs)
                action_dict[agent.name] = action

        if not isinstance(real_agents[0], RLAgent):
            obs, reward, done, info = env.step(action_dict=action_dict)
            if isinstance(real_agents[0], RealAgent):
                for agent in real_agents:
                    agent.refresh_subtasks(world=env.world)
        elif isinstance(real_agents[0], RLAgent):
            #callback = RecordTrajectories()
            # open trajectory file with current time stamp and level name

            real_agents[0].train(total_timesteps=arglist.max_num_timesteps)
            rl_flag = False


        # Saving info
        if isinstance(real_agents[0], RealAgent):
            bag.add_status(cur_time=info['t'], real_agents=real_agents)

    # End timing and calculate elapsed time
    agent_end_time = time.time()
    elapsed_time = agent_end_time - agent_start_time

    # Log metrics

    if isinstance(real_agents[0], RLAgent) and real_agents[0].successful:
        logger.info(f"Agent {real_agents[0].name}: Steps taken: {real_agents[0].steps_to_success}")
    else:
        logger.info(f"Agent {real_agents[0].name}: Steps taken: {real_agents[0].steps_taken}")
    logger.info(f"Time taken for {arglist.level} with {arglist.model1} and {arglist.model2}: {elapsed_time:.2f} seconds")

    # Log overall success
    success = env.successful
    if isinstance(real_agents[0], RLAgent):
        success = real_agents[0].successful
    logger.info(f"Experiment success: {success}")

    # Delete the plan file after the run is complete
    if isinstance(real_agents[0], plan_agent):
        try:
            if os.path.exists(real_agents[0].plan_file_path):
                os.remove(real_agents[0].plan_file_path)
                logger.info(f"Deleted plan file: {real_agents[0].plan_file_path}")
        except Exception as e:
            logger.error(f"Failed to delete plan file: {e}")

    # Saving final information before saving pkl file
    if not isinstance(real_agents[0], RLAgent):
        bag.set_collisions(collisions=env.collisions)
        bag.set_termination(termination_info=env.termination_info,
                successful=env.successful)

if __name__ == '__main__':
        arglist = parse_arguments()
        if arglist.play:
            # might need to change arglist for environment because the make wont work for my new agent
            env = gym.envs.make("gym_cooking:overcookedEnv-v0", arglist=arglist)
            env.reset()

            # Pass env to some RL baseline and see if it works

            game = GamePlay(env.filename, env.world, env.sim_agents)
            game.on_execute()
        else:
            model_types = [arglist.model1, arglist.model2, arglist.model3, arglist.model4]
            assert len(list(filter(lambda x: x is not None,
                model_types))) == arglist.num_agents, "num_agents should match the number of models specified"
            fix_seed(seed=arglist.seed)
            main_loop(arglist=arglist)


#TODO: USE THE CALLBACK CODE TO SAVE THE OBSERVATIONS
    # import pickle
    #
    # # Step 2: Open the pickle file in binary read mode
    # with open('misc/metrics/pickles/partial-divider_salad_agents2_seed1_model1-bd_model2-bd.pkl', 'rb') as file:
    #     # Step 3: Load the data from the file
    #     data = pickle.load(file)
    #
    # # Now you can use the 'data' variable
    # print(data)