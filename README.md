# Python based Thing Description Directory API compliant to: https://www.w3.org/TR/wot-discovery/

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
appropriate `SPARQLENDPOINT_URL` value. Then run only the api image.
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
export TDD__SPARQLENDPOINT_URL=<sparql endpoint url>
export TDD__TD_JSONSCHEMA=tdd/data/td-json-schema-validation.json
gunicorn -b 0.0.0.0:5000 app:app
```

You can change the `-b` parameter if you want to deploy only for localhost
access, or public access, or change the port deployment.

In this example we use the configuration using the environment variables but you can edit
ths `config.toml` file instead if you prefer.

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

### Deploy a Fuseki server locally

You can either use a distant SPARQL server or use a SPARQL server locally.

We propose to use Apache Jena Fuseki, which has a nice administration interface.
Download the Fuseki projet (apache-jena-fuseki-X.Y.Z.zip) from
https://jena.apache.org/download/index.cgi

Then unzip the downloaded archive.
To launch the server, in the apache-jena-fuseki-X.Y.Z folder, run

```
./fuseki-server
```

The server will run on http://localhost:3030.
If you want to create the dataset with the right configuration, you can copy-paste
`fuseki-docker/configuration/things.ttl` into `apache-jena-fuseki-X.Y.Z/run/configuration`

```
cp fuseki-docker/configuration/things.ttl path/to/apache-jena-fuseki-X.Y.Z/run/configuration
```

More documentation on Fuseki in this project is available in `doc/fuseki.md`

### Run the flask server

```bash
export TDD__SPARQLENDPOINT_URL=<sparql endpoint url>
export TDD__TD_JSONSCHEMA=tdd/data/td-json-schema-validation.json
flask run
```

You can edit the `config.toml` file to change the configuration instead of using
environment variables if you prefer.

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

To import snapshots bundle (discovery data) use the proper script as following:

```bash
python scripts/import_snapshot.py /path/to/snapshots.json <WOT API URL>/things
```

The `check-schema` param also works on this route.

## Configuration

The TDD API can be configured using two methods. The first one is editing the
`config.toml` file and the other one is using environment variables. Those two
configuration can be mixed with a priority for the environment variables. It
means that, for each variable, TDD API will search for the environment
variables first, if they are not defined, then it will search for the
`config.toml` values and if the variables are not defined in environment
variable nor in `config.toml` the default value will be used.

The configuration variables are the same on both methods, except that
the environment variables must be prefixed with `TDD__` to avoid conflicts.
The `config.toml` file can also be used to define FLask server configuration (c.f.
[documentation](https://flask.palletsprojects.com/en/2.1.x/config/#builtin-configuration-values)).

### Configuration variables

| Variable name             | default value                             | description                                                                                                                                                    |
| ------------------------- | ----------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [TDD__]TD_REPO_URL        | http://localhost:5000                     | The URL to access the TDD API server                                                                                                                           |
| [TDD__]SPARQLENDPOINT_URL | http://localhost:3030/things              | The SPARQL endpoint URL                                                                                                                                        |
| [TDD__]TD_JSONSCHEMA      | ./tdd/data/td-json-schema-validation.json | The path to the file containing JSON-Schema to validate the TDs                                                                                                |
| [TDD__]CHECK_JSON_SCHEMA  | False                                     | Define if TDD API will check the TDs regarding to the `TD_JSONSCHEMA` schema                                                                                   |
| [TDD__]MAX_TTL            | None                                      | Integer, maximum time-to-live (in seconds) that a TD will be kept on the server (unlimited if None)                                                            |
| [TDD__]MANDATE_TTL        | False                                     | Boolean value, if set to True, it will only upload TDs having a time-to-live (ttl) value. The server will send a 400 HTTP code if the TD does not contain one. |
| [TDD__]LIMIT_BATCH_TDS    | 25                                        | Default limit of returned TDs by batch                                                                                                                         |

## Notes on Virtuoso - TODO Change to a general section about tested Triplestores (Jena, GraphDB, Virtuoso and include this as a subsection)

https://vos.openlinksw.com/owiki/wiki/VOS

`/Applications/Virtuoso Open Source Edition v7.2.app/Contents/virtuoso-opensource/bin` -> `./virtuoso-t +foreground +configfile ../database/virtuoso.ini`

`/Applications/Virtuoso\ Open\ Source\ Edition\ v7.2.app/Contents/virtuoso-opensource/bin/isql localhost:1111 -U dba -P dba`

```
GRANT EXECUTE ON DB.DBA.SPARQL_INSERT_DICT_CONTENT TO "SPARQL";
GRANT EXECUTE ON DB.DBA.SPARQL_DELETE_DICT_CONTENT TO "SPARQL";
DB.DBA.RDF_DEFAULT_USER_PERMS_SET ('nobody', 7);
GRANT EXECUTE ON DB.DBA.SPARUL_RUN TO "SPARQL";
GRANT EXECUTE ON DB.DBA.SPARQL_INSERT_QUAD_DICT_CONTENT TO "SPARQL";
GRANT EXECUTE ON DB.DBA.L_O_LOOK TO "SPARQL";
GRANT EXECUTE ON DB.DBA.SPARUL_CLEAR TO "SPARQL";
GRANT EXECUTE ON DB.DBA.SPARUL_DROP TO "SPARQL";
GRANT EXECUTE ON DB.DBA.SPARQL_UPDATE TO "SPARQL";
```

http://127.0.0.1:8890/sparql  
http://127.0.0.1:8890/conductor

| User Name | Default Password | Usage                                                                                                       |
| :-------- | :--------------- | :---------------------------------------------------------------------------------------------------------- |
| dba       | dba              | Default Database Administrator account.                                                                     |
| dav       | dav              | WebDAV Administrator account.                                                                               |
| vad       | vad              | WebDAV account for internal usage in VAD (disabled by default).                                             |
| demo      | demo             | Default demo user for the demo database. This user is the owner of the Demo catalogue of the demo database. |
| soap      | soap             | SQL User for demonstrating SOAP services.                                                                   |
| fori      | fori             | SQL user account for 'Forums' tutorial application demonstration in the Demo database.                      |

Problem: Virtuoso 37000 Error SP031: SPARQL compiler: Blank node '\_:b0' is not allowed in a constant clause  
https://github.com/openlink/virtuoso-opensource/issues/126

Go to the Virtuoso administration UI, i.e., http://host:port/conductor

- Log in as user dba
- Go to System Admin → User Accounts → Users
- Click the Edit link
- Set User type to SQL/ODBC Logins and WebDAV
- From the list of available Account Roles, select SPARQL_UPDATE and click the >> button to add it to the right-hand list
- Click the Save button

## Code quality

Run black and flake8 if you modified the Python code before commiting.

You can do it with tox if you have it installed:

```bash
tox -e black-run
tox -e flake8
```

Or manually if you do not have tox installed:

```bash
black .
flake8
```

Some tests have been developed to test the API's behaviour.
We invite you to modify the tests if you change the behaviour and add
new tests if you develop new features.

```bash
pytests tests
```
