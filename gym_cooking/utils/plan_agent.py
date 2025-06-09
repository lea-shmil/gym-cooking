import os
import shutil

class plan_agent:
    def __init__(self, name, id_color, recipes, arglist, env):
        self.name = name
        self.color = id_color
        self.recipes = recipes
        self.arglist = arglist
        self.env = env
        self.plan_file_path = f"utils/plans/{self.arglist.level}_plan.txt"  # Path to the plan file
        self.actions_queue = self._load_plan()

    def _load_plan(self):

        # Define paths
        sas_plan_path = r'C:\Users\Administrator\Documents\GitHub\gym-cooking\sas_plan'
        shutil.copyfile(sas_plan_path, self.plan_file_path)

        """Load the plan from the relevant plan.txt file."""
        if not os.path.exists(self.plan_file_path):
            raise FileNotFoundError(f"Plan file not found: {self.plan_file_path}")

        actions = []
        with open(self.plan_file_path, "r") as file:
            lines = file.readlines()

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
        parts = action_line.split()
        agent_num = parts[1][1]  # agent num A[1]
        if agent_num != self.name.split('-')[1]:  # Check if the action is for this agent
            return 0, 0  # No-op if not for this agent
        start = parts[2]  # e.g., X4Y1
        end = parts[3]    # e.g., X5Y1

        # Calculate the movement direction
        start_x, start_y = int(start[1]), int(start[3])
        end_x, end_y = int(end[1]), int(end[3])
        dx, dy = end_x - start_x, end_y - start_y

        return dx, dy

    def select_action(self):
        """Return the next action for the agent."""
        if not self.actions_queue:
            raise RuntimeError("No more actions in the plan.")
        print(f"Agent {self.name} executing action: {self.actions_queue[0]}")
        return self.actions_queue.pop(0)
