#!/bin/bash

# Remove the current saved plot
rm data/graph.png

# Record the start time
start_time=$(date +%s)

# Function to run the worker script
run_worker() {
    rank=$1
    python worker/hzz_script.py --rank $rank
}

# Get input argument
n=$1

# Check if the number of arguments is correct
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <number_of_workers>"
    exit 1
fi

# Run the counter script
python counter/hzz_counter.py --number_workers $n

# Run worker scripts with ranks 0 to n-1
for ((rank=0; rank<n; rank++)); do
    run_worker $rank
done

# Run the collector script
python collector/hzz_collector.py

# Record end time when plot is actually produced
while [ ! -f data/graph.png ]; do
    sleep 1
done
end_time=$(date +%s)

duration=$((end_time - start_time))
echo "Total time taken for analysis: $duration seconds."