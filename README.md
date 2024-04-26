# Domus TDD API

A Python and SPARQL based Thing Description Directory API compliant to:
https://www.w3.org/TR/wot-discovery/

To learn more about the routes and function of this server, see
the [API documentation](doc/api.md).

## Motivation

According to [World History Encyclopedia](https://www.worldhistory.org/article/77/the-roman-domus/) the

> Roman domus was much more than a place of dwelling for a Roman familia. It also served as a place of business and a religious center for worship. The size of a domus could range from a very small house to a luxurious mansion. In some cases, one domus took up an entire city-block, while more commonly, there were up to 8 domus per insula (city-block). All domus were free-standing structures. Some were constructed like modern-day townhouses with common walls between them, while others were detached.

In the same way the Domus TDD API does not just offer a standards-conformant interface as specified in the link above, but also allows for flexible and scalable deployment, and has the possibility for extensions to carry out a bit more than just store & retrieve operations.

## Configuration

The TDD API can be configured using two methods.

1. Using environment variables prefixing the variable names by `TDD__`
   (to avoid conflicts)

   ```
     export TDD__SPARQLENDPOINT_URL="http://my-new-sparql.endpoint/address"
     export TDD__CHECK_SCHEMA=True
   ```

2. Editing the `config.toml` file using the direct name of the variable

   ```
     SPARQLENDPOINT_URL="http://my-new-sparql.endpoint/address"
     CHECK_SCHEMA=True
   ```

Those two configurations can be mixed with a priority as follows:

1. If the value is set in an environment variable, use the environment variable value
2. If not, and it is set in the `config.toml`, use the `config.toml` value
3. If not, use the default value

The `config.toml` file can also be used to define FLask server configuration (c.f.
[documentation](https://flask.palletsprojects.com/en/2.1.x/config/#builtin-configuration-values)).

- The **SPARQLENDPOINT_URL** variable is mandatory

### Configuration variables

| Variable name                 | default value                             | description                                                                                                                                                    |
| ----------------------------- | ----------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [TDD__]TD_REPO_URL            | http://localhost:5000                     | The URL to access the TDD API server                                                                                                                           |
| [TDD__]SPARQLENDPOINT_URL     | http://localhost:3030/things              | The SPARQL endpoint URL                                                                                                                                        |
| [TDD__]CHECK_SCHEMA           | False                                     | Define if TDD API will check the TDs regarding to the JSON-Schema and SHACL shapes                                                                             |
| [TDD__]MAX_TTL                | None                                      | Integer, maximum time-to-live (in seconds) that a TD will be kept on the server (unlimited if None)                                                            |
| [TDD__]MANDATE_TTL            | False                                     | Boolean value, if set to True, it will only upload TDs having a time-to-live (ttl) value. The server will send a 400 HTTP code if the TD does not contain one. |
| [TDD__]LIMIT_BATCH_TDS        | 25                                        | Default limit of returned TDs by batch (used for pagination)                                                                                                   |
| [TDD__]ENDPOINT_TYPE          | None                                      | Special configuration to workaround SPARQL endpoints which do not follow the SPARQL standard. Possible values: `GRAPHDB` or `VIRTUOSO`                         |
| [TDD__]TD_JSONSCHEMA          | ./tdd/data/td-json-schema-validation.json | The path to the file containing JSON-Schema to validate the TDs                                                                                                |
| [TDD__]TD_ONTOLOGY            | ./tdd/data/td.ttl                         | The path to the file containing the TD OWL Ontology (only used for SHACL validation)                                                                           |
| [TDD__]TD_SHACL_VALIDATOR     | ./tdd/data/td-validation.ttl              | The path to the file containing the SHACL shapes (only used for SHACL validation)                                                                              |
| [TDD__]PERIOD_CLEAR_EXPIRE_TD | 3600                                      | The number of seconds between each clearing of expired TDs (0 to disable clearing expired TD)                                                                  |
| [TDD__]OVERWRITE_DISCOVERY    | False                                     | Use custom discovery context (for offline purposes)                                                                                                            |

## Deploy to develop on the API

### Create and activate a virtual environment

Create the [virtual environment](https://docs.python.org/3/library/venv.html)

```bash
python3 -m venv .venv
```

Activate the virtual environment (in each new terminal where you need the libraries
or the project)

```bash
source .venv/bin/activate
```

Install the project and it dependencies in the virtual environment by running:

```bash
pip install -e .[dev]
```

Install the JavaScript dependencies (the project relies on jsonld.js for JSON-LD framing)

```bash
npm ci
```

### Deploy a SPARQL endpoint

The TDD API relies on a SPARQL endpoint as database connection.
You need to set up one before you run the project.

In the [SPARQL endpoint documentation](doc/sparql-endpoints/README.md) we provide
you with guidelines on how to set-up your SPARQL endpoint.

### Run the flask server

First, set up your configuration (the SPARQL endpoint URL) (see [configuration](#configuration))
if your SPARQL endpoint URL is not the default http://localhost:3030/things.

Then run the flask server at the root of this project in your python virtual environment.

```bash
flask run
```

## Import data using script

To import the TDs from a directory to your SPARQL endpoint using the proxy api, run:

```bash
python scripts/import_all_plugfest.py /path/to/TDs/directory <WOT API URL>/things
```

To import without any JSON-SCHEMA validation, change the `check-schema` param as
follows:

```bash
python scripts/import_all_plugfest.py /path/to/TDs/directory <WOT API URL>/things?check-schema=false
```

## Deploy locally with docker-compose

For a quick launch of the SPARQL endpoint and TDD API with docker-compose:

```bash
chmod a+rwx fuseki-docker/configuration
chmod a+rwx fuseki-docker/databases
docker-compose build # builds api and sparqlendpoint
docker-compose up # runs api and sparqlendpoint
```

If you want to deploy only the TDD API using docker-compose and use an
existing SPARQL endpoint then you should edit the `config.toml` file with the
appropriate `SPARQLENDPOINT_URL` value (see [configuration](#configuration)).
Then run only the api image.
If the api image is already built you do not have to rebuild, relaunching it
will use the new config.

```bash
docker-compose build api # builds the api image
docker-compose run api # runs the api
```

## Deploy production

If you want to deploy production without using docker or docker-compose you can use
the following commands:

```bash
pip install .[prod]
gunicorn -b 0.0.0.0:5000 app:app
```

You can change the `-b` parameter if you want to deploy only for localhost
access, or public access, or change the port deployment.

In this example we use the configuration using the environment variables but you can edit
the `config.toml` file instead if you prefer.

## Code quality

A few quality tests (formatting, linting, testing) have been developed to keep
this code maintainable.
Some tests have been developed to test the API's behaviour in python.
We invite you to modify the tests if you change the behaviour and add
new tests if you develop new features.

You can do it with tox if you have it installed:

```bash
tox -p all
```

Or manually if you do not have tox installed:

```bash
black .
flake8
pytests tests
```

## Plugin

To use a specific plugin you can juste pip install the module and relaunch your
TDD-API server. The new plugins routes and transformers will then be available.

### Develop your own plugin

You can develop your own plugin to add features to your TDD-API server.
To do so you can create a new project and follow the instructions defined in the
[Plugin Documentation](doc/plugin.md) to add it to the TDD-API.

### Installing a plugin from pypi

Plugins are python packages. If the plugin you want to add is on Pypi, you
can simply `pip install` it.

## Publishing domus-tdd-api to pypi.org

To publish the package on pypi:

- bump the package version in setup.py
- tag the commit with the version
- run `npm ci && npm run build` to recreate the javascript bundles
- remove existing local dist and .egg folders `rm -rf build dist .egg .egg-info`
- build python package `python3 setup.py sdist bdist_wheel`
- install twine `pip install twine`
- verify package with twine `twine check dist/*`
- upload package to pypi `twine upload --skip-existing dist/*`
