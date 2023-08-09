# Docker image


## Docker-compose

For development purposes, we have set a docker-compose service.
To run this with a few commands, you must have docker-compose installed.

First, you need to give read/write/execute rights on the `fuseki-docker/configuration`
and `fuseki-docker/databases` folders to docker-compose.
This can be done with:
```
chmod a+rwx fuseki-docker/configuration
chmod a+rwx fuseki-docker/databases
```

Once this is done, you can run the docker-compose:

```
docker-compose up
```

Two services are deployed by this command (as described in `docker-compose.yml`):
- Fuseki from the `secoresearch/fuseki`, see more documentation on the image
  documentation in doc/fuseki.md

- The tdd-api image created from the Dockerfile, see more documentation on the
  tdd-api in doc/api.md
