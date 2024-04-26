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

import os
import uuid
from rdflib import Namespace, Graph


from tdd.config import CONFIG


TDD = Namespace("https://www.w3.org/2022/wot/discovery-ontology#")
TD = Namespace("https://www.w3.org/2019/wot/td#")

DEFAULT_THING_CONTEXT_URI = "https://www.w3.org/2022/wot/td/v1.1"
DEFAULT_DISCOVERY_CONTEXT_URI = "https://www.w3.org/2022/wot/discovery"


def get_collection_etag():
    collection_etag = os.environ.get("COLLECTION_ETAG")
    if collection_etag is None:
        collection_etag = update_collection_etag()
    return collection_etag


def update_collection_etag():
    collection_etag = str(uuid.uuid4())
    os.environ["COLLECTION_ETAG"] = collection_etag
    return collection_etag


POSSIBLE_MIMETYPES = {
    "application/rdf+xml",
    "text/turtle",
    "text/n3",
    "application/n-quads",
    "application/n-triples",
    "application/trig",
    "application/ld+json",
}

TD_PREFIX = {
    "td": "https://www.w3.org/2019/wot/td#",
    "td-jsonschema": "https://www.w3.org/2019/wot/json-schema#",
    "td-discovery": "https://www.w3.org/2022/wot/discovery-ontology#",
    "td-hypermedia": "https://www.w3.org/2019/wot/hypermedia#",
}


def slugify(s):
    """Transforms string into valid filename"""
    return "".join(x if x.isalnum() else "_" for x in s)


def uri_to_base(uri):
    base_url = uri.replace(":uuid:", ":")  # Avoid uuid verification in Fuseki
    return f"{CONFIG['TD_REPO_URL']}/{base_url}/"


def negociate_mime_type(
    request, possible_mimetypes=POSSIBLE_MIMETYPES, default_mimetype="application/json"
):
    accepted_headers_by_weight = sorted(
        request.accept_mimetypes or [], key=lambda h: h[1], reverse=True
    )
    mime_type_negociated = default_mimetype
    for parsed_header in accepted_headers_by_weight:
        accepted_mime_type = parsed_header[0]
        if accepted_mime_type in possible_mimetypes:
            mime_type_negociated = accepted_mime_type
            break
    return mime_type_negociated


def create_binded_graph():
    g = Graph()
    for prefix, uri in TD_PREFIX.items():
        g.bind(prefix, uri)
    return g


def create_link_params(params):
    return "&".join([f"{key}={value}" for key, value in params.items()])


def full_uri_to_prefixed(full_uri):
    for prefix, uri in TD_PREFIX.items():
        if full_uri.startswith(uri):
            return f"{prefix}:{full_uri.replace(uri, '')}"
    return full_uri


def find_blank_node_path(node, td_uri, td_graph, last_node=None, last_predicate=None):
    """Use `triples()` method and not SPARQL since blank nodes are
    not identified in SPARQL but they are in triples method
    """
    for subject, predicate, _ in td_graph.triples((last_node, last_predicate, node)):
        predicate_prefixed_uri = full_uri_to_prefixed(predicate.toPython())
        if subject == td_uri:
            return predicate_prefixed_uri
        sub_path = find_blank_node_path(
            subject, td_uri, td_graph, last_node=None, last_predicate=None
        )
        if sub_path is not None:
            return sub_path + "/" + predicate_prefixed_uri
    return None


def construct_describe_graph(node, td_graph):
    g = create_binded_graph()
    for triple_predicate, triple_object in td_graph.predicate_objects(node):
        g.add((node, triple_predicate, triple_object))
    return g
