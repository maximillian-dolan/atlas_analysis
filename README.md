# hzz analysis

First navigate to hzz directory with:
```
$ cd hzz
```

## To run with bash script

Run:
```
$ ./hzz_bash.sh <number divisions>
```
The value for the number of divisions will dictate how many divisions the analysis can be split into for running. This is purely demonstrative in this case, as they will still be run sequentially, not saving any time.

## To run with docker containarisation

Run:
```
$ ./hzz_bash.sh <number divisions>
```
This will run the code as several containers, final plot will be saved within data and not automatically shown.

## To run and deploy with docker swarm

First create docker swarm on manager node using:
```
$ docker swarm init
```
Then add each worker node using worker-join token, before running:
```
$ ./hzz_swarm.sh
```
To scale up or down with more worker nodes, first remove all services by running the following on the manager node:
```
$ docker service rm $(docker service ls -q)
```
Then add more worker nodes, and rerun hzz_swarm.sh



