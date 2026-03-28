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
import atexit
from flask import Response

from .config import CONFIG
from .errors import FusekiError
from tdd.validators import validate_uri

# Initialize a globally pooled, secure HTTP client for SPARQL endpoint communication.
# Adheres to enterprise security best practices: bounded resource limits and explicit timeouts.
#
# Security Configurations Documented:
# - trust_env=False: Explicitly disables reading environment variables (e.g., HTTP_PROXY)
#   to prevent potential proxy hijacking or environment variable pollution. Ensures
#   direct connection to the backend graph database.
#
# - follow_redirects=False: Prevents Server-Side Request Forgery (SSRF) vectors if the
#   backend endpoint is spoofed and attempts to redirect traffic to internal domains.
#   INFRASTRUCTURE BEST PRACTICE: The TDD API and SPARQL endpoint should communicate
#   directly via internal networking (e.g., internal DNS/Service Mesh) bypassing external
#   Load Balancers. If an external gateway is introduced that forces HTTP->HTTPS redirects,
#   requests will safely fail with a 3xx status instead of blindly following.
http_client = httpx.Client(
    limits=httpx.Limits(max_keepalive_connections=50, max_connections=100),
    timeout=httpx.Timeout(10.0, connect=5.0),
    trust_env=False,
    follow_redirects=False,
)

# Register a shutdown hook to explicitly close the client on application exit.
# This ensures that open sockets and connections are properly released to the OS,
# preventing resource leaks or warnings instead of relying on garbage collection.
atexit.register(http_client.close)

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

    :param str sparqlquery: SPARQL query

    :returns: HTTP response
    :rtype: Response
    """
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
        # Utilize the global HTTP client for connection pooling.
        resp = http_client.post(
            sparqlendpoint,
            data={"query": querystring},
            headers=headers,
        )
    if request_type == "update":
        if CONFIG["ENDPOINT_TYPE"] == "GRAPHDB":
            sparqlendpoint = urljoin(f"{sparqlendpoint}/", "statements")
        # Utilize the global HTTP client for update operations to maintain low latency.
        resp = http_client.post(
            sparqlendpoint,
            data={"update": querystring},
        )

    if resp.status_code not in status_codes:
        raise FusekiError(resp)
    return resp


def delete_named_graph(named_graph):
    # Upstream validation: Secure the graph URI before executing DROP
    safe_graph = validate_uri(named_graph)
    query(f"DROP SILENT GRAPH <{safe_graph}>", request_type="update")
