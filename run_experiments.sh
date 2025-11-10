#!/bin/bash

source /c/Users/Administrator/anaconda3/etc/profile.d/conda.sh
#source /c/Conda/etc/profile.d/conda.sh
conda activate gym_cooking

# --- FIX: Add project to PYTHONPATH ---
# Get the absolute path to the directory where this script is located
# (This is now the project root, which is what we want)
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
# Add that directory to Python's search path
export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"

echo "Current Working Directory: $(pwd)"
echo "Setting PYTHONPATH to: $PYTHONPATH"
# --- END FIX ---


levels=('blocks_salad' 'blocks_tomato' 'blocks_tl' 'map1_salad' 'map1_tomato' 'map1_tl' 'map3_salad' 'map3_tl' 'map3_tomato')
#levels=('blocks_salad' 'blocks_salad_v2' 'blocks_tl' 'blocks_tl_v2' 'blocks_tomato' 'blocks_tomato_v2'   'full-divider_salad_v2' 'full-divider_tl' 'full-divider_tl_v2' 'full-divider_tomato' 'full-divider_tomato_v2'  'map1_salad' 'map1_tomato' 'map1_tl' 'map1_salad_v2' 'map1_tomato_v2' 'map1_tl_v2' 'map2_salad' 'map2_tomato' 'map2_tl' 'map2_salad_v2' 'map2_tomato_v2' 'map2_tl_v2', 'map3_salad' 'map3_tomato' 'map3_tl' 'map3_salad_v2' 'map3_tomato_v2' 'map3_tl_v2', 'map4_salad' 'map4_tomato' 'map4_tl' 'map4_salad_v2' 'map4_tomato_v2' 'map4_tl_v2')
#models=("rl" "plan" "plan" "bd")
models=("rl")

nseed=1
max_timesteps=1000
# Define evaluator and search strategies
evaluator1="hcea=cea()"
search1="lazy_greedy([hcea], preferred=[hcea])"

evaluator2="lmcut=lmcut(transform=adapt_costs(cost_type=one))"
#the default wont count the costs in the non numeric pddl
search2='astar(lmcut, bound=infinity, max_time=infinity, description="astar", verbosity=normal)'
#if we do cost_type=normal it will loop indefinitely

#evaluator2="hcea=cea()"
#search2='astar(hcea, pruning=stubborn_sets_simple(), cost_type=one, bound=infinity, max_time=300,. description="astar", verbosity=normal)'

plan_run_counter=0

for nagents in 2 3 4; do
  for level in "${levels[@]}"; do

    # If the number of agents is 3 or 4 (greater than 2),
    # but the level name does NOT start with "map",
    # then skip this combination.
    if [[ "$nagents" -gt 2 ]] && [[ "$level" != "map"* ]]; then
      echo "Skipping level $level with $nagents agents (not a 'map' level)."
      continue # Skip to the next level
    fi
    # --- End of New Check ---

    for model in "${models[@]}"; do
      for seed in $(seq 1 $nseed); do
        if [[ "$model" == "plan" ]]; then
          # Use plan_run_counter to alternate between evaluator/search
          if (( plan_run_counter % 2 == 0 )); then
            evaluator="$evaluator1"
            search="$search1"
          else
            evaluator="$evaluator2"
            search="$search2"
          fi
          #((plan_run_counter++)) # This is commenting out the astar currently
        else
          evaluator=""
          search=""
        fi

        # Set max-num-timesteps based on the model
        if [[ "$model" == "rl" ]]; then
          max_timesteps="--max-num-timesteps 10000"
        else
          max_timesteps="--max-num-timesteps 1000"
        fi

        # --- NEW: Dynamically build model arguments ---
        model_args=""
        for i in $(seq 1 $nagents); do
          # This builds a string like: --model1 plan --model2 plan ...
          model_args+="--model$i $model "
        done
        # --- END NEW ---

        echo "Running experiments with $max_timesteps, level=$level, model=$model, seed=$seed, nagents=$nagents, evaluator=$evaluator, search=$search"
        # Use the $nagents variable from the new outer loop and the new $model_args
        python main.py $max_timesteps --num-agents $nagents --seed $seed --level $level $model_args --evaluator "$evaluator" --search "$search"
        sleep 5
      done
    done
  done
done