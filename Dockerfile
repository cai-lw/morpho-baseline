FROM continuumio/miniconda3

WORKDIR /app
COPY requirements.txt .
COPY code/ ./code/
COPY scripts/ ./scripts/

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential cmake clang \
    && conda create -n dynet python=2

SHELL ["conda", "run", "-n", "dynet", "/bin/bash", "-c"]
RUN git clone https://github.com/ZurichNLP/emnlp2018-imitation-learning-for-neural-morphology.git \
    && cd emnlp2018-imitation-learning-for-neural-morphology \
    && pip install -r requirements.txt \
    && cd lib \
    && make \
    && conda create -n sharedtask python=3

SHELL ["conda", "run", "-n", "sharedtask", "/bin/bash", "-c"]
RUN pip install -r requirements.txt \
    && conda list \
    && git clone https://github.com/karlstratos/anchor.git \
    && cd anchor \
    && make

WORKDIR /app/scripts
ENTRYPOINT ["bash", "/app/scripts/main.sh"]
