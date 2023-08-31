FROM python:3.11-slim-bullseye

VOLUME [ "/offat/data" ]

WORKDIR /offat/data
WORKDIR /offat

COPY . /offat/

RUN python3 -m pip install -U pip

RUN python -m pip install -e .

ENTRYPOINT [ "offat" ]