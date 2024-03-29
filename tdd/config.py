"""******************************************************************************
 * Copyright (c) 2018 Contributors to the Eclipse Foundation
 *
 * See the NOTICE file(s) distributed with this work for additional
 * information regarding copyright ownership.
 *
 * This program and the accompanying materials are made available under the
 * terms of the Eclipse Public License v. 2.0 which is available at
 * http://www.eclipse.org/legal/epl-2.0, or the W3C Software Notice and
 * Document License (2015-05-13) which is available at
 * https://www.w3.org/Consortium/Legal/2015/copyright-software-and-document.
 *
 * SPDX-License-Identifier: EPL-2.0 OR W3C-20150513
 ********************************************************************************"""

from config import config_from_env, config_from_toml, config_from_dict
from config.configuration_set import ConfigurationSet

from tdd.paths import DATA_PATH

_default_config = {
    "TD_REPO_URL": "http://localhost:5000",
    "SPARQLENDPOINT_URL": "http://127.0.0.1:3030/things",
    "TD_JSONSCHEMA": DATA_PATH / "td-json-schema-validation.json",
    "TD_ONTOLOGY": DATA_PATH / "td.ttl",
    "TD_SHACL_VALIDATOR": DATA_PATH / "td-validation.ttl",
    "ENDPOINT_TYPE": None,
    "LIMIT_BATCH_TDS": 25,
    "CHECK_SCHEMA": False,
    "MAX_TTL": None,
    "MANDATE_TTL": False,
    "PERIOD_CLEAR_EXPIRE_TD": 3600,
    "OVERWRITE_DISCOVERY": False,
}

CONFIG = ConfigurationSet(
    config_from_env(prefix="TDD", interpolate=True),
    config_from_toml("config.toml", read_from_file=True),
    config_from_dict(_default_config),
)

# Remove trailing /
if CONFIG["SPARQLENDPOINT_URL"][-1] == "/":
    CONFIG["SPARQLENDPOINT_URL"] = CONFIG["SPARQLENDPOINT_URL"][:-1]


def check_possible_endpoints():
    POSSIBLE_ENDPOINT_TYPES = {"VIRTUOSO", "GRAPHDB"}
    if CONFIG["ENDPOINT_TYPE"]:
        if CONFIG["ENDPOINT_TYPE"].upper() not in POSSIBLE_ENDPOINT_TYPES:
            raise ValueError(
                f"ENDPOINT_TYPE possible values are {', '.join(POSSIBLE_ENDPOINT_TYPES)}"
            )
        return CONFIG["ENDPOINT_TYPE"].upper()


def _cast_to_boolean(fieldname):
    value = CONFIG[fieldname]
    true_values = ("true", "1", "y")
    false_values = ("false", "0", "n")
    if isinstance(value, str):
        if value.lower() in true_values + false_values:
            return value.lower() not in false_values
        raise ValueError(
            f"{fieldname} must be boolean (true or false), case insensitive"
        )
    elif isinstance(value, bool):
        return value
    raise ValueError(f"{fieldname} must be boolean (true or false), case insensitive")


def _cast_to_int(fieldname):
    value = CONFIG[fieldname]
    if isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            raise ValueError(f"{fieldname} must be integer")
    elif isinstance(value, int):
        return value
    raise ValueError(f"{fieldname} must be integer")


CONFIG["LIMIT_BATCH_TDS"] = _cast_to_int("LIMIT_BATCH_TDS")
CONFIG["CHECK_SCHEMA"] = _cast_to_boolean("CHECK_SCHEMA")
if CONFIG["MAX_TTL"] is not None:
    CONFIG["MAX_TTL"] = _cast_to_int("MAX_TTL")
CONFIG["MANDATE_TTL"] = _cast_to_boolean("MANDATE_TTL")
CONFIG["ENDPOINT_TYPE"] = check_possible_endpoints()
CONFIG["PERIOD_CLEAR_EXPIRE_TD"] = _cast_to_int("PERIOD_CLEAR_EXPIRE_TD")
CONFIG["OVERWRITE_DISCOVERY"] = _cast_to_boolean("OVERWRITE_DISCOVERY")
