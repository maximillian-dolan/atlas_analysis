# hzz analysis

First navigate to hzz directory with:
```
$ cd hzz
```
## To run scripts on their own

```
$ python counter/hzz_counter.py --number_workers <number of divisions>

# Run for rank 0 up to rank number_workers-1
$ python worker/hzz_script.py --rank <rank>

$ python collector/hzz_collector.py
```
Alternatively you can run from the bash script:
```
$ hzz_bash.sh <number divisions>
```

## To run with docker containarisation

Run:
```
$ ./hzz_containers.sh <number divisions>
```
This will run the code as several containers, final plot will be saved within data and not automatically shown. To delete all images once containers have finished running, use:
```
$ docker rmi -f $(docker images -aq)
```

## To run and deploy with docker swarm

First create docker swarm on manager node using:
```
$ docker swarm init
```
Then add each worker node using worker-join token, before running on the manager node:
```
$ ./hzz_swarm.sh
```
To scale up or down with more worker nodes, first remove all services by running the following on the manager node:
```
$ docker service rm $(docker service ls -q)
```
Then add more worker nodes, and rerun hzz_swarm.sh



