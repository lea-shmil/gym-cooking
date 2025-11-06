#!/bin/bash

#source /c/Users/Administrator/anaconda3/etc/profile.d/conda.sh
source /c/Conda/etc/profile.d/conda.sh
conda activate gym_cooking

levels=('blocks_salad' 'blocks_salad_v2' 'blocks_tl' 'blocks_tl_v2' 'blocks_tomato' 'blocks_tomato_v2' 'credit-divider_salad' 'credit-divider_salad_v2' 'credit-divider_tl' 'credit-divider_tl_v2' 'credit-divider_tomato' 'credit-divider_tomato_v2' 'cubicle_salad' 'cubicle_salad_v2' 'cubicle_tl' 'cubicle_tl_v2' 'cubicle_tomato' 'cubicle_tomato_v2' 'full-divider_salad' 'full-divider_salad_v2' 'full-divider_tl' 'full-divider_tl_v2' 'full-divider_tomato' 'full-divider_tomato_v2' 'halfmap-divider_salad' 'halfmap-divider_salad_v2' 'halfmap-divider_tl' 'halfmap-divider_tl_v2' 'halfmap-divider_tomato' 'halfmap-divider_tomato_v2' 'large_tomato' 'large_tomato_3' 'open-divider_salad' 'open-divider_salad_v2' 'open-divider_tl' 'open-divider_tl_v2' 'open-divider_tomato' 'open-divider_tomato_v2' 'partial-divider_salad' 'partial-divider_salad_v2' 'partial-divider_tl' 'partial-divider_tl_v2' 'partial-divider_tomato' 'partial-divider_tomato_v2' 'plaza_salad' 'plaza_salad_v2' 'plaza_tl' 'plaza_tl_v2' 'plaza_tomato' 'plaza_tomato_v2')
levels=('blocks_tl' 'blocks_tl_v2' 'credit-divider_tl' 'credit-divider_tl_v2' 'cubicle_tl' 'cubicle_tl_v2' 'full-divider_tl' 'full-divider_tl_v2' 'halfmap-divider_tl' 'halfmap-divider_tl_v2' 'open-divider_tl' 'open-divider_tl_v2' 'partial-divider_tl' 'partial-divider_tl_v2' 'plaza_tl' 'plaza_tl_v2')
models=("rl")
#models=("rl" "plan")

nagents=2
#nseed=1
#nseed=5
max_timesteps=100
# Define evaluator and search strategies
evaluator1="hcea=cea()"
search1="lazy_greedy([hcea], preferred=[hcea])"

evaluator2="lmcut=lmcut(transform=adapt_costs(cost_type=one))"
#the default wont count the costs in the non numeric pddl
search2='astar(lmcut, bound=infinity, max_time=infinity, description="astar", verbosity=normal)'
#if we do cost_type=normal it will loop indefinitely

#evaluator2="hcea=cea()"
#search2='astar(hcea, pruning=stubborn_sets_simple(), cost_type=one, bound=infinity, max_time=300, description="astar", verbosity=normal)'

plan_run_counter=0

for level in "${levels[@]}"; do

  # --- Logic to set n_agents based on level name ---
  # Default n_agents to 2
  n_agents="2"

  if [[ "$level" == "large"* ]]; then
    # Condition 1: If level begins with 'large' (e.g., large_tomato), set n_agents to 4.
    n_agents="4"
  elif [[ "$level" == *"_3" ]]; then
    # Condition 2: If level ends with '_3' (e.g., large_tomato_3), set n_agents to 3.
    n_agents="3"
  fi

  for model in "${models[@]}"; do
   # for seed in $(seq 1 $nseed); do
    if [[ "$model" == "plan" ]]; then
      # Use plan_run_counter to alternate between evaluator/search
      if (( plan_run_counter % 2 == 0 )); then
        evaluator="$evaluator1"
        search="$search1"
      else
        evaluator="$evaluator2"
        search="$search2"
      fi
      #((plan_run_counter++))
    else
      evaluator=""
      search=""
    fi
    # Set max-num-timesteps based on the model
    if [[ "$model" == "rl" ]]; then
      max_timesteps="--max-num-timesteps 10000"
    else
      max_timesteps="--max-num-timesteps 100"
    fi

      echo "Running experiments with $max_timesteps, level=$level, model=$model, seed=$seed, evaluator=$evaluator, search=$search"
      python main.py $max_timesteps --num-agents $nagents --seed 1 --level $level --model1 $model --model2 $model --evaluator "$evaluator" --search "$search"
      sleep 5
#    done
  done
done