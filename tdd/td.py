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

import concurrent.futures
from copy import copy
from datetime import datetime
from importlib import resources
import json
from jsonschema import Draft7Validator
import uuid
from rdflib import Graph, RDF
from rdflib.exceptions import ParserError
import pyshacl


from tdd.context import (
    get_context,
    convert_context_to_array,
    get_all_contexts,
    overwrite_thing_context,  # not possible to remove it yet,
    #  because of hasSecurityConfiguration framing
    overwrite_discovery_context,
)
from tdd.errors import (
    FusekiError,
    IDMismatchError,
    JSONDecodeError,
    JSONSchemaError,
    OrderbyError,
    RDFValidationError,
)
from tdd.utils import (
    uri_to_base,
    DEFAULT_THING_CONTEXT_URI,
    DEFAULT_DISCOVERY_CONTEXT_URI,
    TD,
    create_binded_graph,
)
from tdd.registration import (
    validate_ttl,
    yield_registration_triples,
    update_registration,
    delete_registration_information,
    get_registration_dict,
)
from tdd.sparql import (
    DELETE_GRAPHS,
    GET_EXPIRED_TD_GRAPHS,
    GET_URI_BY_ONTOLOGY,
    GET_NUMBER,
    GET_TD_CREATION_DATE,
    query,
)
from tdd.config import CONFIG
from tdd.common import (
    put_json_in_sparql,
    put_rdf_in_sparql,
    frame_nt_content,
    get_id_description,
)


with resources.open_text("tdd.data", "td-json-schema-validation.json") as fp:
    schema = json.load(fp)

validator = Draft7Validator(schema=schema)

TYPE = "https://www.w3.org/2019/wot/td#Thing"
ONTOLOGY = {"prefix": "td", "base": "https://www.w3.org/2019/wot/td"}


def sanitize_td(ld_content):
    ld_content = copy(ld_content)
    if "id" not in ld_content:
        ld_content["id"] = f"urn:uuid:{uuid.uuid4()}"

    convert_context_to_array(ld_content)  # Force context to be an array
    # add the default context definition since it must be present for all TDs import
    if DEFAULT_THING_CONTEXT_URI not in ld_content["@context"]:
        ld_content["@context"].append(DEFAULT_THING_CONTEXT_URI)
    if DEFAULT_DISCOVERY_CONTEXT_URI not in ld_content["@context"]:
        ld_content["@context"].append(DEFAULT_DISCOVERY_CONTEXT_URI)

    return ld_content


def use_custom_context(ld_content):
    """Add @base and overwrite context, ld_content must already be sanitized"""
    ld_content = copy(ld_content)
    # Add a base_url so that ids which are not URIs can be transformed into URIs
    base_url = uri_to_base(ld_content["id"])
    ld_content["@context"].insert(0, {"@base": base_url})

    # replace thing context uri with the fixed thing context
    # No need for now, since the published context is up to date
    overwrite_thing_context(ld_content)

    # replace discovery context uri witht the fixed discovery context
    overwrite_discovery_context(ld_content)

    return ld_content


def validate_td(td, id=None, check_schema=CONFIG["CHECK_SCHEMA"]):
    try:
        ld_content = json.loads(td)
    except json.decoder.JSONDecodeError as exc:
        raise JSONDecodeError(exc)

    if id is not None:
        if "id" in ld_content:
            if id != ld_content["id"]:
                raise IDMismatchError(ld_content["id"], id)
        else:
            ld_content["id"] = id

    validate_ttl(ld_content, CONFIG["MANDATE_TTL"])

    if check_schema:
        validated, errors = validate_td_json_schema(ld_content)
        if not validated:
            raise JSONSchemaError(errors, td_id=id)

    return ld_content


def validate_td_json_schema(td):
    errors = list(validator.iter_errors(td))
    if errors:
        return False, errors
    return True, None


def validate_tds(tds):
    valid_tds = []
    erroneous_tds = {}
    for id, td in enumerate(tds):
        if CONFIG["CHECK_SCHEMA"]:
            validated, errors = validate_td_json_schema(td)
            if not validated:
                id = td.get("id", f"urn:array_id:{id}")
                erroneous_tds[id] = errors
            else:
                valid_tds.append(td)
        else:
            valid_tds.append(td)
    return valid_tds, erroneous_tds


def get_already_existing_td(uri):
    resp = query(
        GET_TD_CREATION_DATE.format(uri=uri),
    )
    if resp.status_code == 200:
        if len(resp.json()["results"]["bindings"]) > 0:
            created_date = resp.json()["results"]["bindings"][0]["created"]["value"]
            return created_date
    return None


def put_td_rdf_in_sparql(
    td_content, mimetype, uri=None, delete_if_exists=True, check_schema=True
):
    g = Graph()
    try:
        g.parse(data=td_content, format=mimetype)
    except (SyntaxError, ParserError):
        raise RDFValidationError(f"The RDF triples are not well formatted ({mimetype})")
    uri, _, _ = next(g.triples((None, RDF.type, TD["Thing"])), (None, None, None))
    if uri is None:
        raise RDFValidationError(f"Did not find any {TD['Thing']}")

    if check_schema:
        ontology_graph = create_binded_graph()
        with resources.path("tdd.data", "td.ttl") as onto_path:
            ontology_graph.parse(location=onto_path, format="turtle")
        with resources.path("tdd.data", "td-validation.ttl") as shacl_path:
            shacl_shapes_graph = create_binded_graph()
            shacl_shapes_graph.parse(location=shacl_path, format="turtle")

        conforms, graph_reports, text_reports = pyshacl.validate(
            g,
            shacl_graph=shacl_shapes_graph,
            ont_graph=ontology_graph,
        )
        if not conforms:
            raise RDFValidationError(
                "The RDF triples are not conform with the SHACL validation : \n"
                f" {text_reports}",
                td_id=uri,
                errors=graph_reports,
                td_graph=g,
            )

    registration = get_registration_dict(uri, g)
    delete_registration_information(uri, g)

    created_date = get_already_existing_td(uri)
    registration = update_registration(registration, created_date, CONFIG["MAX_TTL"])
    for triple in yield_registration_triples(uri, registration):
        g.add(triple)
    put_rdf_in_sparql(
        g,
        uri,
        [DEFAULT_THING_CONTEXT_URI, DEFAULT_DISCOVERY_CONTEXT_URI],
        delete_if_exists,
        ONTOLOGY,
        forced_type=TYPE,
    )
    return (created_date is not None, uri)


def get_td_description(id, content_type="application/td+json", context=None):
    if not content_type.endswith("json"):
        return get_id_description(id, content_type, ONTOLOGY)
    content = get_id_description(id, "application/n-triples", ONTOLOGY)
    if not context:
        context = get_context(id, ONTOLOGY)
    try:
        return frame_td_nt_content(id, content, context)
    except ExpireTDError:
        return ""


def put_td_json_in_sparql(td_content, uri=None, delete_if_exists=True):
    """
    returns:
    - boolean True if the TD inserted already existed
    - uri of the TD
    """
    registration = td_content.get("registration", {})
    td_content = sanitize_td(td_content)
    original_context = copy(td_content["@context"])
    uri = uri if uri is not None else td_content["id"]
    td_content = use_custom_context(td_content)

    created_date = get_already_existing_td(uri)
    td_content["registration"] = update_registration(
        registration, created_date, CONFIG["MAX_TTL"]
    )
    put_json_in_sparql(
        td_content, uri, original_context, delete_if_exists, ONTOLOGY, forced_type=TYPE
    )

    return (created_date is not None, uri)


def delete_graphs(ids):
    graph_ids_str = ", ".join([f"<{graph_id}>" for graph_id in ids])
    delete_td_query = DELETE_GRAPHS.format(graph_ids_str=graph_ids_str)
    resp = query(delete_td_query, request_type="update")
    if resp.status_code not in [200, 201, 204]:
        raise FusekiError(resp)

    delete_graphs_query = "\n".join([f"CLEAR GRAPH <{graph_id}>;" for graph_id in ids])
    resp = query(delete_graphs_query, request_type="update")
    if resp.status_code not in [200, 201, 204]:
        raise FusekiError(resp)


class ExpireTDError(Exception):
    pass


def frame_td_nt_content(td_id, nt_content, original_context):
    context = copy(original_context)
    context.append({"@base": uri_to_base(td_id)})

    frame = {
        "@context": context,
        "@type": "Thing",
    }

    # no need since the published context is up to date
    overwrite_thing_context(frame)
    overwrite_discovery_context(frame)
    json_ld_compacted = frame_nt_content(td_id, nt_content, frame)

    jsonld_response = json.loads(json_ld_compacted)
    jsonld_response["@context"] = original_context
    today = datetime.today().astimezone()

    if "registration" not in jsonld_response:
        jsonld_response["registration"] = {}
    jsonld_response["registration"]["retrieved"] = today.isoformat()
    return jsonld_response


def get_total_number():
    resp_nb = query(
        GET_NUMBER.format(ontology=ONTOLOGY["base"]),
    )

    if resp_nb.status_code not in [200, 201, 204]:
        raise FusekiError(resp_nb)

    return int(resp_nb.json()["results"]["bindings"][0]["c"]["value"])


ORDERBY = {
    "title": "?id td:title ?title",
    "baseUri": "?id td:baseUri ?baseUri",
    "created": "?id disco:hasRegistrationInformation/disco:dateCreated ?created",
    "modified": "?id disco:hasRegistrationInformation/disco:dateModified ?modified",
    "ttl": "?id disco:hasRegistrationInformation/disco:ttl ?ttl",
    "expires": "?id disco:hasRegistrationInformation/disco:expires ?expires",
}


def get_paginated_tds(limit, offset, sort_by, sort_order):
    all_tds = []
    tasks = []

    def send_request(id, context):
        td = get_td_description(id, context=context)
        all_tds.append(td)

    contexts = get_all_contexts()

    if sort_by is not None and sort_by not in ORDERBY:
        raise OrderbyError(sort_by)

    resp = query(
        GET_URI_BY_ONTOLOGY.format(
            limit=limit,
            offset=offset,
            ontology=ONTOLOGY["base"],
            orderby_variable=f"?{sort_by}" if sort_by else "?id",
            orderby_sparql=(
                f"""
            OPTIONAL {{ GRAPH ?graph {{
                {ORDERBY[sort_by]}
            }}}}
            """
                if sort_by
                else ""
            ),
            orderby_direction=sort_order if sort_order else "ASC",
        ),
    )
    if resp.status_code not in [200, 201, 204]:
        raise FusekiError(resp)

    results = resp.json()["results"]["bindings"]

    with concurrent.futures.ThreadPoolExecutor() as executor:
        for result in results:
            tasks.append(
                executor.submit(
                    send_request,
                    result["id"]["value"],
                    contexts[result["graph"]["value"]],
                )
            )

    return all_tds


def get_all_tds(sort_by, sort_order):
    last_batch = False
    iter_number = 0
    while not last_batch:
        offset = iter_number * CONFIG["LIMIT_BATCH_TDS"]
        batch_tds = get_paginated_tds(
            CONFIG["LIMIT_BATCH_TDS"], offset, sort_by, sort_order
        )
        for td in batch_tds:
            yield td
        iter_number += 1
        last_batch = len(batch_tds) < CONFIG["LIMIT_BATCH_TDS"]


def clear_expired_td():
    resp = query(GET_EXPIRED_TD_GRAPHS)
    tds_to_clean = [x["graph"]["value"] for x in resp.json()["results"]["bindings"]]
    print("expired tds to clean: ", tds_to_clean)
    delete_graphs(tds_to_clean)
