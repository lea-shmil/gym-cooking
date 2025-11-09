Maps
    To create new maps add textual maps manually to utils/levels following the instructions in design.md
    There is also a script to generate random maps located at utils/map_generator.py
    The pddl maps can be generated using the pddl_problem_generator.py script. simply provide the path to the textual 
    

Run
    To run the environment see instructions in gym_cooking/README.md
    All runs are logged in experiment_log.txt located in gym_cooking
    All vector representations of the states are logged in state_logs folder located in env_log (relevant for rl only)

Experiments
    To run experiments use the run_experiments.sh script located in gym_cooking.
    You can specify the planner, map, number of runs, and other parameters.
    The results of the experiments are also logged in experiment_log.txt
    The content of the log can be exported to a csv file using the export_log_to_csv.py script located in gym_cooking/utils.
    
