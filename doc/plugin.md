# TDD-API Plugin

You can find a plugin example here [https://github.com/wiresio/domus-tdd-api-plugin-example](https://github.com/wiresio/domus-tdd-api-plugin-example).

To develop your own plugin, the first thing to do is to create a `setup.py` file
at the root of your new python project containing the usual python project information,
then add the entrypoints needed for TDD-API to consider it as a plugin.

```python
#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name="TDD API plugin Example",
    version="1.0",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "tdd-api",
    ],
    extras_require={
        'dev': [
            'pytest',
            'mock',
        ]
    },
    entry_points={
        "tdd_api.plugins.blueprints": [
            "example=tdd_api_plugin_example:blueprint",
        ],
        "tdd_api.plugins.transformers": [
            "example=tdd_api_plugin_example.example:td_to_example",
        ],
    },
)
```

We have defined two entrypoints. The first one is `tdd_api.plugins.blueprints` which is used to
define where to find the [Flask blueprint](https://flask.palletsprojects.com/en/3.0.x/blueprints/) for
the plugin.
The second one is `tdd_api.plugins.transformers` to specify the function to use to transform a TD to
what you want, here an `example`.

Then you can develop the function for the routes using the blueprint and the transformer feature.

## Blueprint

As we defined in the [`tdd_api_plugin_example/__init__.py`](https://github.com/wiresio/tdd-api-plugin/blob/main/tdd_api_plugin_example/__init__.py) we define the blueprint
as follow:

```python
blueprint = Blueprint("tdd_api_plugin_example", __name__, url_prefix="/example")
```

We can give any name to the variable since the `setup.py` links it to the `tdd_api.plugins.blueprints`.

The first parameter `"tdd_api_plugin_example"` is the name of the blueprint, the second parameter is the
import module (here `__name__` since this is the same module) and we define a `url_prefix` to not redeclare it
on each route.
This `url_prefix` make sure that if we use different plugins, the routes they declare will be unique `/plugin1/route1`, `/plugin2/route1`.
This requires that all plugins have _different prefix_.

This blueprint can be used to define all the routes you want to add to the TDD-API server regarding to
this plugin.
For example to add a `GET` route for the `Example` plugin you can add the route like this:

```python
@blueprint.route("/<id>", methods=["GET"])
def describe_example(id):
    return ...
```

We use the blueprint as decorator to add the route, the path is defined regarding the `url_prefix` and we
specify a dedicated method to match.
You can look at the [`tdd_api_plugin_example/__init__.py`](https://github.com/wiresio/tdd-api-plugin/blob/main/tdd_api_plugin_example/__init__.py) file to see
other examples.

## Transformer

Transformers are functions that will be called each time a thing is created/updated on the /things routes,
you can find the calls to these transformers in the [`tdd/__init__.py`](../tdd/__init__.py) file, in the functions:

- `create_td`
- `update_td`
- `create_anonymous_td`

We have defined a transformer to be sure, each time a TD is uploaded to transform it to our `example` format
and store in the SparqlEndpoint. To do, we declare the function to use in the entrypoint: here
`tdd_api_plugin_example.example:td_to_example` since we use the function `td_to_example` which is defined in the
`tdd_api_plugin_example/example.py` file.

This method is declared like this:

```python
def td_to_example(uri):
    ...
```

The parameter must be only the TD URI as a string since we want to be the most generic as possible. Then the first
thing to do can be fetching the TD content, which can be done with:

```python
content = get_id_description(uri, "application/n-triples", {"prefix": "td"})
```

Using this content we can do whatever is needed to manipulate the data : transform it,
change its format, etc.
Then we can store the result using the helper method `put_json_in_sparql` or `put_rdf_in_sparql` from the
`tdd.common` module.
You can look at the [`tdd_api_plugin_example/example.py`](https://github.com/wiresio/blobl/main/tdd_api_plugin_example/example.py) file to see how it is defined.

## Tests

This example plugin come with some tests example to present how it can be done.
You can find it in the folder [`tdd_api_plugin_example/tests`](https://github.com/wiresio/blobl/main/tdd_api_plugin_example/tests).
`test_example.py` defines some tests for the `example.py` module, where the `test_td_to_example.py`
define tests for the routes.

These tests simulate the existence of a real SparqlEndpoint using a RDFLib Graph abstraction. Then you
can specify a mock SparqlEndpoint prefilled with some data as it is defined with:

```python
@pytest.fixture
def mock_sparql_example_and_td(httpx_mock):
    graph = SparqlGraph("td_example.trig", format="trig", data_path=DATA_PATH)
    httpx_mock.add_callback(graph.custom)
```

Where `DATA_PATH` is where the tests data are stored and `td_example.trig` the data to fill the SparqlEndpoint.

There are some generic mocks defined in the `TDD-API` module. You have to import them to use them in your tests.
You can find for example the `mock_sparql_empty_endpoint` from `tdd.tests.conftest` module. This mock can be used
to simulate an empty SparqlEndpoint at the beginning of your test.
