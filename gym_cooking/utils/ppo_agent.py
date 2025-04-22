import gym
import gym_cooking.utils.agent
from stable_baselines3 import PPO
from termcolor import colored as color


class PPOAgent:
    def __init__(self, arglist, name, id_color, recipes):
        super(PPOAgent, self).__init__(arglist=arglist, name=name, id_color=id_color, recipes=recipes)
        self.env = gym.envs.make("gym_cooking:overcookedEnv-v0", arglist=arglist)
        self.model = PPO("MlpPolicy", self.env, verbose=1)
        self.model.learn(total_timesteps=10000)
        self.env.reset()

    def train(self, total_timesteps=10000):
        self.model.learn(total_timesteps=total_timesteps)

    def save(self, path):
        self.model.save(path)

    def load(self, path):
        self.model = PPO.load(path, env=self.env)

    def predict(self, obs):
        action, _states = self.model.predict(obs)
        return action
