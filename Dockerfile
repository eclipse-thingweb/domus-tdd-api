# syntax=docker/dockerfile:1
FROM node:lts-bullseye-slim

RUN apt-get update && apt-get -y --no-install-recommends install \
    python3-pip \
    python3-setuptools \
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
COPY README.md /tdd-api/README.md
COPY webpack.config.js /tdd-api/webpack.config.js
COPY js-src /tdd-api/js-src

WORKDIR /tdd-api
RUN pip3 install -e ".[prod]"
RUN npm ci
RUN npm run build

#Uncomment to install AID plugin
#RUN git clone https://github.com/wiresio/domus-tdd-api-plugin-aid.git
#WORKDIR /tdd-api/domus-tdd-api-plugin-aid
#RUN pip3 install -e .

RUN useradd proxyapi --create-home
RUN mkdir /database
USER proxyapi

EXPOSE 5050
CMD ["gunicorn", "-b", "0.0.0.0:5050", "app:app"]
#Use the following line instead of the previous one if AID plugin is installed
#CMD ["gunicorn", "-b", "0.0.0.0:5050", "--chdir", "../", "app:app"]
