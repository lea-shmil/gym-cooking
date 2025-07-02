#!/bin/bash

source /c/Users/Administrator/anaconda3/etc/profile.d/conda.sh

conda activate gym_cooking

levels=("full-divider_salad" "partial-divider_salad" "open-divider_salad" "full-divider_tomato" "partial-divider_tomato" "open-divider_tomato" "full-divider_tl" "partial-divider_tl" "open-divider_tl")
#levels=("open-divider_tomato")
#models=("rl" "plan" "plan" "bd")
models=("plan" "plan")

nagents=2
nseed=1
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

# Loop over levels, models, and seeds
for level in "${levels[@]}"; do
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
        ((plan_run_counter++))
      else
        evaluator=""
        search=""
      fi
      # Set max-num-timesteps based on the model
      if [[ "$model" == "rl" ]]; then
        max_timesteps="--max-num-timesteps 30000"
      else
        max_timesteps="--max-num-timesteps 100"
      fi

      echo "Running experiment wit h $max_timesteps, level=$level, model=$model, seed=$seed, evaluator=$evaluator, search=$search"
      python main.py $max_timesteps --num-agents $nagents --seed $seed --level $level --model1 $model --model2 $model --evaluator "$evaluator" --search "$search"
      sleep 5
    done
  done
done