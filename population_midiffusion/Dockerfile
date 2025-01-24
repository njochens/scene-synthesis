ARG TAG=11.1.1-cudnn8-devel
ARG DEBIAN_FRONTEND=noninteractive
FROM nvidia/cuda:$TAG

RUN apt update --allow-insecure-repositories --fix-missing
RUN apt install -y git python3-pip
WORKDIR /home
RUN git clone https://github.com/MIT-SPARK/ThreedFront.git
RUN git clone https://github.com/MIT-SPARK/MiDiffusion.git
WORKDIR /home/MiDiffusion
RUN pip install -e ../ThreedFront
RUN python3 setup.py build_ext --inplace
RUN pip install -e .
WORKDIR /home
COPY . /home/
RUN mv /home/revisions/utils.py /home/MiDiffusion/scripts/utils.py
RUN mv /home/revisions/generate_results.py /home/MiDiffusion/scripts/generate_results.py
RUN mv /home/revisions/render_results.py /home/ThreedFront/scripts/render_results.py
RUN mv /home/revisions/feature_extractors.py /home/MiDiffusion/midiffusion/networks/feature_extractors.py
RUN rm -r revisions
RUN pip install -r /home/requirements.txt
RUN rm requirements.txt
RUN export DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/Berlin
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN apt install ffmpeg libsm6 libxext6 -y

#CMD ["python3", "app.py"]

EXPOSE 5002