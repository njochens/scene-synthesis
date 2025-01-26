# scene-synthesis

Before you can build the docker image you need to download the pretrained weights for the bedroom and living room models from the original MiDiffusion paper [here](https://drive.google.com/drive/folders/14N87Ap90KNaDlRv5u6UeCV1h_MT9QqaN?usp=sharing).
Copy the `model.pt` for bedroom into the folder `population_midiffusion/input/bedroom-weights` and do the same for the living room weights. **Be careful not to overwrite the `config.yaml` file!**

To build the docker image navigate into `population_midiffusion` and run:

```
docker build -t population_midiffusion .
```

Once the image has been successfully created you can run

```
docker container run --gpus all -v /tmp/.X11-unix:/tmp/.X11-unix -e DISPLAY=unix$DISPLAY -p 5002:5002 -it population_midiffusion
```

to execute and connect to the docker container.
