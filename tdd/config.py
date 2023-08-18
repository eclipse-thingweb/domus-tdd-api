from config import config_from_env, config_from_toml, config_from_dict
from config.configuration_set import ConfigurationSet


_default_config = {
    "TD_REPO_URL": "http://localhost:5000",
    "SPARQLENDPOINT_URL": "http://127.0.0.1:3030/things",
    "TD_JSONSCHEMA": "./tdd/data/td-json-schema-validation.json",
    "TD_ONTOLOGY": "./tdd/data/td.ttl",
    "TD_SHACL_VALIDATOR": "./tdd/data/td-validation.ttl",
    "VIRTUOSO_ENDPOINT": False,
    "LIMIT_BATCH_TDS": 25,
    "CHECK_SCHEMA": False,
    "MAX_TTL": None,
    "MANDATE_TTL": False,
}

CONFIG = ConfigurationSet(
    config_from_env(prefix="TDD", interpolate=True),
    config_from_toml("config.toml", read_from_file=True),
    config_from_dict(_default_config),
)

# Remove trailing /
if CONFIG["SPARQLENDPOINT_URL"][-1] == "/":
    CONFIG["SPARQLENDPOINT_URL"] = CONFIG["SPARQLENDPOINT_URL"][:-1]


def _cast_to_boolean(value):
    if isinstance(value, str):
        return value.lower() not in ("false", "0", "f")
    elif isinstance(value, bool):
        return value
    return ValueError()


def _cast_to_int(value):
    if isinstance(value, str):
        return int(value)
    elif isinstance(value, int):
        return value
    return ValueError()


CONFIG["LIMIT_BATCH_TDS"] = _cast_to_int(CONFIG["LIMIT_BATCH_TDS"])
CONFIG["CHECK_SCHEMA"] = _cast_to_boolean(CONFIG["CHECK_SCHEMA"])
CONFIG["VIRTUOSO_ENDPOINT"] = _cast_to_boolean(CONFIG["VIRTUOSO_ENDPOINT"])
if CONFIG["MAX_TTL"] is not None:
    CONFIG["MAX_TTL"] = _cast_to_int(CONFIG["MAX_TTL"])
CONFIG["MANDATE_TTL"] = _cast_to_boolean(CONFIG["MANDATE_TTL"])
