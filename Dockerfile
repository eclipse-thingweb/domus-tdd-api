# syntax=docker/dockerfile:1
FROM node:lts-bullseye-slim

RUN apt-get update && apt-get -y --no-install-recommends install \
    python3-pip \
    python3-setuptools \
    && rm -rf /var/lib/apt/lists/*

ENV FLASK_RUN_HOST=0.0.0.0
ENV TD_REPO_URL="http://localhost:5000"

RUN mkdir /tdd-api
COPY setup.py /tdd-api/
COPY tdd /tdd-api/tdd
COPY app.py /tdd-api/app.py
COPY package.json /tdd-api/
COPY package-lock.json /tdd-api/
COPY config.toml /tdd-api/config.toml
COPY README.md /tdd-api/README.md

WORKDIR /tdd-api
RUN npm ci

#RUN apk add --no-cache gcc musl-dev linux-headers
RUN pip3 install .[prod]

RUN useradd proxyapi --create-home
RUN mkdir /database
USER proxyapi

EXPOSE 5000
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
