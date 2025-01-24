# scene-synthesis


To build the docker image navigate into `population_midiffusion` and run:

```
docker build -t population_midiffusion .
```

Once the image has been successfully created you can run

```
docker container run --gpus all -v /tmp/.X11-unix:/tmp/.X11-unix -e DISPLAY=unix$DISPLAY -p 5002:5002 -it population_midiffusion
```

to execute and connect to the docker container.
