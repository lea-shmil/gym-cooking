from stable_baselines3.common.callbacks import BaseCallback
import time
import os

from gym_cooking.utils.pddl_problem_generator import get_state


class TrajectoryCallback(BaseCallback):
    def __init__(self, env, steps, trajectory_dir, verbose=0):
        super().__init__(verbose)
        self.env = env
        self.trajectory_dir = trajectory_dir
        self.current_trajectory_file = None
        self.success_logged = False
        self.steps_to_success = 0
        self.file_count = 1
        self.steps = steps

    def _on_training_start(self) -> None:
        # initialize pddl
        pddl_file_path = rf"C:\Users\Administrator\Documents\GitHub\gym-cooking\gym_cooking\utils\pddls\{self.env.arglist.level}.pddl"

        self.env.state_to_pddl(self.env.vector, self.env.arglist.level, self.env.world.width, self.env.world.height, pddl_file_path)

        """Initialize the first trajectory file with a timestamp."""
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        self.current_trajectory_file = os.path.join(
            self.trajectory_dir, f"trajectory_{timestamp}.pddl"
        )
        os.makedirs(self.trajectory_dir, exist_ok=True)
        with open(self.current_trajectory_file, "w") as f:
            f.write("((:init  ")
            get_state(f, self.env.vector, self.env.world.width, self.env.world.height)

    def _on_step(self) -> bool:
        """Write actions and states to the trajectory file."""
        self.steps -= 1

        if hasattr(self.env, "last_action_dict"):
            action_dict = self.env.last_action_dict

        with open(self.current_trajectory_file, "a") as f:
            if not self.success_logged:
                f.write("(operators: ")
                self.env.get_parameters(f, action_dict, self.env.world.width, self.env.world.height)
                f.write("(:state  ")
                get_state(f, self.env.vector, self.env.world.width, self.env.world.height)
        # Check for success and create a new file if needed
        if hasattr(self.env, "success") and self.env.success and not self.success_logged:
            with open(self.current_trajectory_file, "a") as f:
                f.write(")\n")  # Close the current trajectory
            self.file_count += 1
            if not self.success_logged:
                steps_to_success = self.env.steps_to_success
                self.success_logged = True
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            self.current_trajectory_file = os.path.join(
                self.trajectory_dir, f"trajectory_{timestamp} _{self.file_count}.pddl"
            )
            with open(self.current_trajectory_file, "w") as f:
                f.write("((:init  ")
                get_state(f, self.env.vector, self.env.world.width, self.env.world.height)
            self.env.reset()  # Reset the environment but keep training

            print("Saving success before PPO reset.")
            if steps_to_success > 0:
                print(f"Saving success before PPO reset. Steps to success: {steps_to_success}")
                self.steps_to_success = steps_to_success

        return True  # Stop the current training loop

        # # Check if step count exceeds the limit or fails the map...then also stop
        # if self.steps <= 0:
        #     with open(self.current_trajectory_file, "a") as f:
        #         f.write(")\n")  # Write closing statement
        #return True
