###########################
# Run on manager node only!
###########################

# Get the number of worker nodes
n=$(docker node ls | grep -vc "Leader") - 1

# Give each worker node a rank
for ((i = 0; i < n+1; i++)); do
    worker_id=$(docker node ls | grep -nv "Leader" | sed -n "$((2))p" | awk '{print $1}' | cut -d ':' -f 2)
    docker node update --label-add rank=$i $worker_id
done

# Build images
docker build -t counter_image ./counter/
docker build -t worker_image ./worker/
docker build -t collector_image ./collector/

# Create shared volume
docker volume create --driver local --opt type=none --opt device=./data --opt o=bind shared_volume

# Create collector and counter service on just manager node
manager_id=$(docker node ls | grep -n "Leader" | awk '{print $1}' | cut -d ':' -f 2)

docker service create --name counter --constraint "node.id==$manager_id" --mount type=volume,source=shared_volume,target=/app/data counter_image python hzz_counter.py --number_workers n
docker service create --name collector --constraint "node.id==$manager_id" --mount type=volume,source=shared_volume,target=/app/data collector_image python hzz_collector.py

# Create service for relevant rank on each worker node
for ((i = 0; i < n+1; i++)); do

    worker_id=$(docker node ls | grep -nv "Leader" | sed -n "$((2))p" | awk '{print $1}' | cut -d ':' -f 2)
    rank=$(docker node inspect --format '{{ index .Spec.Labels "rank" }}' $worker_id)

    docker service create --name worker_$i --constraint "node.id==$worker_id" --env RANK=$rank --mount type=volume,source=shared_data,target=/app/data worker_image python hzz_script.py --rank $rank
done
