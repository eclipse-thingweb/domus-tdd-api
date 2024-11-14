# syntax=docker/dockerfile:1
FROM node:lts-bullseye-slim

RUN apt-get update && apt-get -y --no-install-recommends install \
    python3-pip \
    python3-setuptools \
    python3-virtualenv \
    git \
    && rm -rf /var/lib/apt/lists/*

ENV FLASK_RUN_HOST=0.0.0.0
ENV TD_REPO_URL="http://localhost:5050"

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
#RUN virtualenv domus
#RUN chmod a+x domus/bin/activate
#RUN domus/bin/activate
RUN pip3 install -e ".[prod]"

#Install AID plugin
RUN git clone https://github.com/wiresio/domus-tdd-api-plugin-aid.git
WORKDIR /tdd-api/domus-tdd-api-plugin-aid
RUN pip3 install -e .

WORKDIR /tdd-api
RUN useradd proxyapi --create-home
RUN mkdir /database
USER proxyapi

EXPOSE 5050
CMD ["gunicorn", "-b", "0.0.0.0:5050", "app:app"]
