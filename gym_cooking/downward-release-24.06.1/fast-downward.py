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
    print("Received arguments:", sys.argv)

    domain_file = sys.argv[1]
    problem_file = sys.argv[2]
    evaluator = sys.argv[3]  # Pass evaluator dynamically
    search = sys.argv[4]     # Pass search strategy dynamically

    # Measure time to generate the plan

    sys.argv = [
        'fast-downward.py',
        domain_file,
        problem_file,
        '--evaluator', evaluator,
        '--search', search
    ]
    main()

