FROM jupyter/scipy-notebook

RUN jupyter labextension install @jupyterlab/toc

COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt