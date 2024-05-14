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

from importlib import resources
import subprocess
import json
import re
from flask import Response


from tdd.sparql import (
    CONSTRUCT_FROM_GRAPH,
    CLEAR_INSERT_GRAPH,
    GET_NAMED_GRAPHS,
    delete_named_graph,
    query,
)
from tdd.metadata import insert_metadata, delete_metadata
from tdd.errors import IDNotFound
from tdd.config import CONFIG


def get_check_schema_from_url_params(request):
    check_schema_param = request.args.get("check-schema")
    check_schema = CONFIG["CHECK_SCHEMA"]
    if check_schema_param in ["false", "False", "0"]:
        check_schema = False
    return check_schema


def delete_id(uri):
    resp = query(
        GET_NAMED_GRAPHS.format(uri=uri),
    )
    if resp.status_code == 200:
        results = resp.json()["results"]["bindings"]
        for result in results:
            delete_named_graph(result["namedGraph"]["value"])
    delete_metadata(uri)
    return Response(status=204)


def json_ld_to_ntriples(ld_content):
    with resources.path("tdd.lib", "transform-to-nt.js") as transform_lib_path:
        p = subprocess.Popen(
            [
                "node",
                transform_lib_path,
                json.dumps(ld_content),
            ],
            stdout=subprocess.PIPE,
        )
        nt_content = p.stdout.read()
    return nt_content.decode("utf-8")


def put_in_sparql(content, uri, context, delete_if_exists, ontology):
    if delete_if_exists:
        delete_id(uri)
    insert_metadata(uri, context, ontology)
    query(
        CLEAR_INSERT_GRAPH.format(
            uri=f'{ontology["prefix"]}:{uri}',
            content=content,
        ),
        request_type="update",
    )


def put_json_in_sparql(
    json_content,
    uri,
    context,
    delete_if_exists,
    ontology,
    forced_type=None,
):
    nt_content = json_ld_to_ntriples(json_content)
    if forced_type:
        nt_content += f"<{uri}> a <{forced_type}>."
    put_in_sparql(nt_content, uri, context, delete_if_exists, ontology)


def put_rdf_in_sparql(g, uri, context, delete_if_exists, ontology, forced_type=None):
    nt_content = g.serialize(format="nt")
    if forced_type:
        nt_content += f"<{uri}> a <{forced_type}>."
    put_in_sparql(nt_content, uri, context, delete_if_exists, ontology)


def frame_nt_content(id, nt_content, frame):
    with resources.path("tdd.lib", "frame-jsonld.js") as frame_lib_path:
        p = subprocess.Popen(
            [
                "node",
                frame_lib_path,
                nt_content,
                json.dumps(frame),
            ],
            stdout=subprocess.PIPE,
        )
        json_ld_compacted = p.stdout.read()
    return json_ld_compacted


def get_id_description(uri, content_type, ontology):
    resp = query(
        CONSTRUCT_FROM_GRAPH.format(named_graph=f'{ontology["prefix"]}:{uri}'),
        headers={"Accept": content_type},
    )
    # if no data, send 404
    if not resp.text.strip() or not (
        re.search(r"^[^\#]", resp.text, re.MULTILINE)
    ):  # because some SPARQL endpoint may send "# Empty file" as response
        raise IDNotFound()
    return resp.text
