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
$ docker-compose up
```
This will run the code as a container, final plot will be saved within data and not automatically shown. To stop the container run:
```
$ docker-compose down
```
Note that this will only delete the container, not the images themselves which will have to be deleted to be rebuilt if any of the code is altered.
