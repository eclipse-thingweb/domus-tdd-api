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

from urllib.parse import urljoin
import httpx
from flask import Response
import re


from tdd.config import CONFIG
from tdd.errors import FusekiError


def sanitize_sparql_uri(uri_value):
    """
    Sanitize a URI for use in SPARQL queries.
    
    Validates and escapes URIs to prevent SPARQL injection attacks.
    According to SPARQL spec, URIs must be enclosed in angle brackets
    and certain characters must be escaped.
    
    :param str uri_value: The URI to sanitize
    :returns: Escaped URI safe for SPARQL
    :rtype: str
    :raises ValueError: If URI contains invalid characters
    """
    uri_str = str(uri_value).strip()
    
    # Remove existing angle brackets if present
    if uri_str.startswith('<') and uri_str.endswith('>'):
        uri_str = uri_str[1:-1]
    
    # Check for obviously malicious patterns (after removing angle brackets)
    if re.search(r'[>"{}|^`]', uri_str):
        raise ValueError(f"Invalid characters in URI: {uri_str}")
    
    # Escape backslashes (must be done first)
    uri_str = uri_str.replace('\\', '\\\\')
    
    # Escape quotes
    uri_str = uri_str.replace('"', '\\"')
    
    # Return with angle brackets
    return f"<{uri_str}>"


def sanitize_sparql_string(string_value):
    """
    Sanitize a string literal for use in SPARQL queries.
    
    Escapes special characters in string literals according to SPARQL spec.
    This is used for literal string values in SPARQL, not URIs.
    
    :param str string_value: The string to sanitize
    :returns: Escaped string safe for SPARQL
    :rtype: str
    """
    string_str = str(string_value)
    
    # Escape backslashes first (must be done first)
    string_str = string_str.replace('\\', '\\\\')
    
    # Escape quotes
    string_str = string_str.replace('"', '\\"')
    
    # Escape newlines and other control characters
    string_str = string_str.replace('\n', '\\n')
    string_str = string_str.replace('\r', '\\r')
    string_str = string_str.replace('\t', '\\t')
    
    return string_str

# general queries
CONSTRUCT_FROM_GRAPH = (
    "CONSTRUCT {{ ?s ?p ?o }} WHERE {{ GRAPH <{named_graph}> {{ ?s ?p ?o }} }}"
)

GET_URI_BY_ONTOLOGY = """
    PREFIX td: <https://www.w3.org/2019/wot/td#>
    PREFIX disco: <https://www.w3.org/2022/wot/discovery-ontology#>
    SELECT DISTINCT ?graph ?id WHERE {{
         GRAPH <urn:tdd:metadata> {{
            ?graph <urn:tdd:expressedIn> <{ontology}>.
            ?graph <urn:tdd:describes> ?id.
        }}
        {orderby_sparql}
    }}
    ORDER BY {orderby_direction}({orderby_variable}) LIMIT {limit} OFFSET {offset}
"""

GET_TD_CREATION_DATE = """
    PREFIX disc: <https://www.w3.org/2022/wot/discovery-ontology#>
    PREFIX td: <https://www.w3.org/2019/wot/td#>
    SELECT ?created WHERE {{
        GRAPH <td:{uri}> {{
            <{uri}> a td:Thing.
            <{uri}>
                disc:hasRegistrationInformation/disc:dateCreated
                ?created.
        }}
    }}
"""

GET_NUMBER = """
    SELECT (COUNT(?x) AS ?c) WHERE {{
        GRAPH <urn:tdd:metadata> {{
            ?x <urn:tdd:expressedIn> <{ontology}>.
        }}
    }}
"""

INSERT_GRAPH = """
    INSERT DATA {{
        GRAPH <{uri}> {{
            {content}
        }}
    }}
"""

# This can be removed once Virtuoso 8 is Open Edition
# https://github.com/openlink/virtuoso-opensource/issues/126
if CONFIG["ENDPOINT_TYPE"] == "VIRTUOSO":
    INSERT_GRAPH = """
        INSERT {{
            GRAPH <{uri}> {{
                {content}
            }}
        }}
    """

CLEAR_INSERT_GRAPH = """CLEAR SILENT GRAPH <{uri}>;""" + INSERT_GRAPH


# specific queries
DELETE_GRAPHS = """
    WITH <urn:tdd:metadata> DELETE {{
        ?graph
        <urn:wot:relation:has_context>
        ?context.
    }} WHERE {{
        ?graph
        <urn:wot:relation:has_context>
        ?context.
        FILTER(?graph IN ({graph_ids_str}))
    }};
    WITH <urn:tdd:metadata> DELETE {{
        ?context <urn:wot:relation:context_content> ?content.
    }}  WHERE {{
        ?context <urn:wot:relation:context_content> ?content.
        MINUS {{ ?uri <urn:wot:relation:has_context> ?context }}
    }}
"""

GET_EXPIRED_TD_GRAPHS = """
    PREFIX td: <https://www.w3.org/2019/wot/td#>
    PREFIX schema: <http://schema.org/>
    PREFIX discovery: <https://www.w3.org/2022/wot/discovery-ontology#>
    SELECT ?graph WHERE {
        GRAPH ?graph {
            ?td a td:Thing.
            ?td discovery:hasRegistrationInformation/discovery:expires ?expires_date.
        }
        FILTER (?expires_date <= NOW())
    }
"""

GET_CONTEXT = """
    SELECT ?context WHERE {{
        GRAPH <urn:tdd:metadata> {{
            <{uri}>
            <urn:wot:relation:has_context>/<urn:wot:relation:context_content>
            ?context
        }}
    }}
"""

GET_ALL_CONTEXTS = """
    SELECT DISTINCT ?id ?context WHERE {
        GRAPH <urn:tdd:metadata> {
            ?id
            <urn:wot:relation:has_context>/<urn:wot:relation:context_content>
            ?context
        }
    }
"""

GET_NAMED_GRAPHS = """
SELECT DISTINCT ?namedGraph WHERE {{
    GRAPH <urn:tdd:metadata> {{
        ?namedGraph <urn:tdd:describes> <{uri}>.
    }}
}}
"""

DELETE_METADATA = """
    WITH <urn:tdd:metadata> DELETE {{
        ?namedGraph <urn:tdd:describes> <{uri}>.
        ?namedGraph ?predicate ?object.
    }}
    WHERE {{
        ?namedGraph <urn:tdd:describes> <{uri}>.
        ?namedGraph ?predicate ?object.
    }};
    WITH <urn:tdd:metadata> DELETE {{
        ?context <urn:wot:relation:context_content> ?content.
    }} WHERE {{
        ?context <urn:wot:relation:context_content> ?content.
        MINUS {{ ?uri <urn:wot:relation:has_context> ?context }}
    }};
"""


def sparql_query(sparqlquery):
    """Query SPARQL endpoint.
    
    Validates user-provided SPARQL queries to prevent injection attacks.
    Only allows SELECT queries for safety - no UPDATE, INSERT, DELETE allowed.

    :param str sparqlquery: SPARQL query

    :returns: HTTP response
    :rtype: Response
    :raises ValueError: If query is invalid or potentially malicious
    """
    # Basic validation: only allow SELECT queries from user
    query_upper = sparqlquery.strip().upper()
    
    # Whitelist allowed query types
    allowed_prefixes = ('SELECT', 'DESCRIBE', 'ASK', 'CONSTRUCT')
    
    if not any(query_upper.startswith(prefix) for prefix in allowed_prefixes):
        raise ValueError(
            "Only SELECT, DESCRIBE, ASK, or CONSTRUCT queries are allowed. "
            "UPDATE/DELETE operations are not permitted."
        )
    
    # Additional check: block dangerous keywords
    dangerous_keywords = ('DROP', 'DELETE', 'INSERT', 'UPDATE', 'CLEAR')
    if any(keyword in query_upper for keyword in dangerous_keywords):
        raise ValueError(
            f"Query contains forbidden operations: {', '.join(dangerous_keywords)}"
        )
    
    resp = query(sparqlquery)
    return Response(
        status=resp.status_code,
        response=resp.text,
        content_type=resp.headers["content-type"],
    )


def query(
    querystring,
    route="",
    request_type="query",  # query or update
    headers={"Accept": "application/json, application/ld+json"},
    status_codes=(200, 201, 204),
):
    """Query SPARQL endpoint (type of query depends on route).

    :param str querystring: SPARQL query
    :param str route: route

    :returns: HTTP response
    :rtype: Response
    """
    sparqlendpoint = CONFIG["SPARQLENDPOINT_URL"]

    if route != "":
        sparqlendpoint = urljoin(f"{sparqlendpoint}/", route)
    if request_type == "query":
        with httpx.Client() as client:
            resp = client.post(
                sparqlendpoint,
                data={"query": querystring},  # TODO take care of SPARQL INJECTION
                headers=headers,
            )
    if request_type == "update":
        if CONFIG["ENDPOINT_TYPE"] == "GRAPHDB":
            sparqlendpoint = urljoin(f"{sparqlendpoint}/", "statements")
        with httpx.Client() as client:
            resp = client.post(
                sparqlendpoint,
                data={"update": querystring},
            )

    if resp.status_code not in status_codes:
        raise FusekiError(resp)
    return resp


def delete_named_graph(named_graph):
    query(f"DROP SILENT GRAPH <{named_graph}>", request_type="update")
