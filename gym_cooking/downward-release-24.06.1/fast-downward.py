#! /usr/bin/env python3
import os
import sys

if __name__ == "__main__":
    from driver.main import main

    # Define all paths you want to add
    custom_paths = [
        r"C:\Program Files (x86)\GnuWin32\bin",
        r"C:\Program Files\mingw64\bin",
        r"C:\Program Files\CMake\bin"
    ]

    # Append them to PATH environment variable
    for path in custom_paths:
        if path not in os.environ["PATH"]:
            os.environ["PATH"] = path + os.pathsep + os.environ["PATH"]

    problem_file = r'C:\Users\Administrator\Documents\GitHub\gym-cooking\gym_cooking\utils\pddls\open-divider_tl.pddl'
    domain_file = r'C:\Users\Administrator\Documents\GitHub\gym-cooking\gym_cooking\utils\pddls\gym-cooking.pddl'
    evaluator = 'hcea=cea()'
    search = 'lazy_greedy([hcea], preferred=[hcea])'
    sys.argv = [
        'fast-downward.py',
        domain_file,
        problem_file,
        '--evaluator', evaluator,
        '--search', search
    ]

main()

