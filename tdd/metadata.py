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


from tdd.sparql import DELETE_METADATA, INSERT_GRAPH, query


def insert_metadata(uri, context, ontology):
    context_str = json.dumps(context)
    encoded_context = base64.b64encode(context_str.encode("utf8")).decode("utf8")
    named_graph_uri = f'{ontology["prefix"]}:{uri}'
    content = f"""
        <{named_graph_uri}> <urn:tdd:describes> <{uri}>.
        <{named_graph_uri}> <urn:tdd:expressedIn> <{ontology["base"]}>.
         <urn:wot:context:{encoded_context}>
        <urn:wot:relation:context_content>
        '{context_str}'.

        <{named_graph_uri}>
        <urn:wot:relation:has_context>
        <urn:wot:context:{encoded_context}>.
    """
    query(
        INSERT_GRAPH.format(uri="urn:tdd:metadata", content=content),
        request_type="update",
    )


def delete_metadata(uri):
    query(
        DELETE_METADATA.format(uri=uri),
        request_type="update",
    )
