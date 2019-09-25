FROM continuumio/miniconda3:4.6.14

WORKDIR /app

RUN apt-get update && yes Y | apt-get install build-essential

RUN conda install -c r r-essentials 