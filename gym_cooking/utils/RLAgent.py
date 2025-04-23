from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv


class RLAgent:
    def __init__(self, name, id_color, recipes, arglist, env):
        self.name = name
        self.color = id_color
        self.recipes = recipes
        self.arglist = arglist
        self.model = PPO("MlpPolicy", env, verbose=1)

    def train(self, timesteps=10000):
        """Train the RL agent."""
        print(f"Training {self.name} for {timesteps} timesteps...")
        self.model.learn(total_timesteps=timesteps)

    def select_action(self, obs):
        """Use the trained model to predict an action."""
        action, _ = self.model.predict(obs, deterministic=True)
        return action


    #TODO : implement the agent using RLSuperAgent should make decisions for all rl agents