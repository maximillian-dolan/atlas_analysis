#!/bin/bash

# Function to run the worker script
run_worker() {
    rank=$1
    python worker/hzz_script.py --rank $rank
}

# Get input argument
n=$1

# Run the counter script
python counter/hzz_counter.py --number_workers $n

# Run worker scripts with ranks 0 to n-1
for ((rank=0; rank<n; rank++)); do
    run_worker $rank
done

# Run the collector script
python collector/hzz_collector.py
