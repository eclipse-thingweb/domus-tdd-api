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

import base64
import json


from tdd.paths import DATA_PATH
from tdd.config import CONFIG
from tdd.utils import DEFAULT_THING_CONTEXT_URI, DEFAULT_DISCOVERY_CONTEXT_URI
from tdd.sparql import (
    INSERT_GRAPH,
    GET_CONTEXT,
    GET_ALL_CONTEXTS,
    query,
)


def convert_context_to_array(ld_content):
    if "@context" not in ld_content:
        ld_content["@context"] = []
        return
    if type(ld_content["@context"]) not in (tuple, list):
        ld_content["@context"] = [ld_content["@context"]]


def overwrite_thing_context(ld_content):
    """
    Overwrite a TD's context with a context from the
    tdd/data/fix-ctx.json file
    """
    if "@context" not in ld_content:
        return
    if type(ld_content["@context"]) not in (tuple, list):
        return
    with open(DATA_PATH / "fixed-ctx.json") as fp:
        fixed_ctx = fp.read()
        try:
            index_wot_ctx = ld_content["@context"].index(DEFAULT_THING_CONTEXT_URI)
            ld_content["@context"][index_wot_ctx] = json.loads(fixed_ctx)
        except ValueError:
            pass


def overwrite_discovery_context(ld_content):
    if not CONFIG["OVERWRITE_DISCOVERY"]:
        return
    if "@context" not in ld_content:
        return
    if type(ld_content["@context"]) not in (tuple, list):
        return
    with open(DATA_PATH / "fixed-discovery-ctx.json") as fp:
        fixed_discovery_ctx = fp.read()
        try:
            index_discovery_ctx = ld_content["@context"].index(
                DEFAULT_DISCOVERY_CONTEXT_URI
            )
            ld_content["@context"][index_discovery_ctx] = json.loads(
                fixed_discovery_ctx
            )
        except ValueError:
            pass


def save_contexts(tds):
    content = ""
    for td_id, td in tds.items():
        context_str = json.dumps(td["@context"])
        encoded_context = base64.b64encode(context_str.encode("utf8")).decode("utf8")
        content += f"""
            <urn:wot:context:{encoded_context}>
            <urn:wot:relation:context_content>
            '{context_str}'.
            <{td_id}>
            <urn:wot:relation:has_context>
            <urn:wot:context:{encoded_context}>.
        """
    query(
        INSERT_GRAPH.format(uri="urn:tdd:metadata", content=content),
        request_type="update",
    )


def get_context(uri, ontology):
    resp = query(
        GET_CONTEXT.format(uri=f'{ontology["prefix"]}:{uri}'),
        "",
        status_codes=(200,),
    )
    results = resp.json()["results"]["bindings"]
    # If td URI has multiple context (different input TD) only apply the first result
    return json.loads(results[0]["context"]["value"] if len(results) > 0 else "[]")


def get_all_contexts():
    """Returns a dict of td_id: context as dict"""
    contexts = {}
    resp = query(
        GET_ALL_CONTEXTS,
        status_codes=(200,),
    )  # and this for Virtuoso
    results = resp.json()["results"]["bindings"]
    for result in results:
        id = result["id"]["value"]
        context = result["context"]["value"]
        if id not in contexts:
            contexts[id] = json.loads(context)
    return contexts
