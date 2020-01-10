ARG BASE_CONTAINER=jupyter/tensorflow-notebook
FROM $BASE_CONTAINER

LABEL maintainer="Miriam Ruiz <miriam@debian.org>"

USER root

RUN \
    apt-get update && apt-get install -y \
        libcairo2-dev && \
    apt-get upgrade -y && \
    apt-get autoremove && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

USER $NB_USER

RUN \
    pip install --quiet 'pygame' && \
    pip install --quiet 'pycairo' && \
    pip install --quiet 'mido' && \
    pip install --quiet 'igraph' && \
    pip install --quiet 'scikit-learn' && \
    pip install --quiet 'tensorflow-datasets' && \
    fix-permissions $CONDA_DIR && \
    fix-permissions /home/$NB_USER
