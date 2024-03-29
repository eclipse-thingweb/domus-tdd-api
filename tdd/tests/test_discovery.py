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

import json
from jsoncomparison import Compare

from tdd.utils import get_collection_etag

from tdd.tests.conftest import (
    DATA_PATH,
    assert_only_on_known_errors,
)


def assert_etag_in_headers(headers, format_param=None):
    format_str = f"?format={format_param}" if format_param else ""
    assert "Link" in headers
    assert (
        f'</things{format_str}>; rel="canonical"; etag="{get_collection_etag()}"'
        in headers["Link"]
    )


def assert_etag_changed(init_etag, headers, format_param=None):
    format_str = f"?format={format_param}" if format_param else ""
    assert "Link" in headers
    assert (
        f'</things{format_str}>; rel="canonical"; etag="{init_etag}"'
        not in headers["Link"]
    )
    assert (
        f'</things{format_str}>; rel="canonical"; etag="{get_collection_etag()}"'
        in headers["Link"]
    )
    assert init_etag != get_collection_etag()


def test_GET_thing_discovery_array_one_td(test_client, mock_sparql_with_one_td):
    with open(DATA_PATH / "smart-coffee-machine.td.jsonld") as fp:
        expected_tds = [json.load(fp)]
    get_response = test_client.get("/things")
    assert len(get_response.json) == 1
    td = get_response.json[0]
    expected_tds[0]["registration"] = td[
        "registration"
    ]  # use the proper registration since this test does not test this
    diff = Compare().check(expected_tds[0], td)
    assert_only_on_known_errors(diff)
    assert_etag_in_headers(get_response.headers)


def test_GET_thing_discovery_array_no_limit(test_client, mock_sparql_17_things):
    get_response = test_client.get("/things")
    tds = get_response.json
    assert len(tds) == 17
    assert_etag_in_headers(get_response.headers)


def test_GET_thing_discovery_array_with_limit(
    test_client, httpx_mock, mock_sparql_17_things
):
    LIMIT_BATCH = 5
    get_response = test_client.get(f"/things?limit={LIMIT_BATCH}")
    tds = get_response.json
    assert len(tds) == LIMIT_BATCH
    assert_etag_in_headers(get_response.headers)
    assert '</things?offset=5&limit=5>; rel="next"' in get_response.headers["Link"]

    get_response = test_client.get("/things?offset=5&limit=5")
    tds = get_response.json
    assert len(tds) == LIMIT_BATCH
    assert "Link" in get_response.headers
    assert '</things?offset=10&limit=5>; rel="next"' in get_response.headers["Link"]

    get_response = test_client.get("/things?offset=10&limit=5")
    tds = get_response.json
    assert len(tds) == LIMIT_BATCH
    assert "Link" in get_response.headers
    assert '</things?offset=15&limit=5>; rel="next"' in get_response.headers["Link"]

    get_response = test_client.get("/things?offset=15&limit=5")
    tds = get_response.json
    assert len(tds) == 2
    assert_etag_in_headers(get_response.headers)


def test_GET_thing_discovery_collection(test_client, mock_sparql_17_things):
    get_response = test_client.get("/things?format=collection")
    tds = get_response.json
    assert tds["@type"] == "ThingCollection"
    assert tds["total"] == 17
    assert len(tds["members"]) == 15
    assert tds["@context"] == "https://www.w3.org/2022/wot/discovery"
    assert "next" in tds
    assert "etag" in tds
    assert tds["etag"] == get_collection_etag()

    assert_etag_in_headers(get_response.headers, format_param="collection")
    assert tds["next"] == "/things?offset=15&limit=15&format=collection"

    get_response = test_client.get(tds["next"])
    tds = get_response.json
    assert tds["@type"] == "ThingCollection"
    assert tds["total"] == 17
    assert len(tds["members"]) == 2
    assert tds["@context"] == "https://www.w3.org/2022/wot/discovery"
    assert "next" not in tds
    assert tds["etag"] == get_collection_etag()
    assert_etag_in_headers(get_response.headers, format_param="collection")


def test_GET_thing_discovery_collection_sort_parameters(
    test_client, mock_sparql_with_one_td
):
    get_response = test_client.get("/things?format=collection&sort_by=created")
    assert get_response.status_code == 200
    get_response = test_client.get("/things?format=collection&sort_order=desc")
    assert get_response.status_code == 200
    get_response = test_client.get(
        "/things?format=collection&sort_order=desc&sort_by=created"
    )
    assert get_response.status_code == 200


def test_GET_thing_discovery_collection_sort_by_desc(
    test_client, mock_sparql_17_things
):
    # rdflib considers language-tagged literals to be order after plain literals
    # "Hue Sensor"@en comes after "Virtual" in its alphabetical order
    # this error was not detected in Fuseki or other SPARQL endpoints
    get_response = test_client.get(
        "/things?format=collection&sort_by=title&sort_order=desc&limit=2"
    )
    tds = get_response.json
    assert tds["@type"] == "ThingCollection"
    assert tds["total"] == 17
    assert len(tds["members"]) == 2
    assert tds["@context"] == "https://www.w3.org/2022/wot/discovery"
    assert "next" in tds
    assert (
        tds["next"]
        == "/things?offset=2&limit=2&sort_order=desc&sort_by=title&format=collection"
    )


def test_collection_etag_changed_after_DELETE(test_client, mock_sparql_with_one_td):
    td_id = "urn:uuid:55f01138-5c96-4b3d-a5d0-81319a2db677"
    response = test_client.get("/things?format=collection")
    init_etag = get_collection_etag()
    assert_etag_in_headers(response.headers, format_param="collection")
    test_client.delete(f"/things/{td_id}")
    response = test_client.get("/things?format=collection")
    assert_etag_changed(init_etag, response.headers, format_param="collection")


def test_collection_etag_changed_after_PATCH(test_client, mock_sparql_with_one_td):
    td_id = "urn:uuid:55f01138-5c96-4b3d-a5d0-81319a2db677"
    response = test_client.get("/things?format=collection")
    init_etag = get_collection_etag()
    assert_etag_in_headers(response.headers, format_param="collection")
    test_client.patch(f"/things/{td_id}", data=json.dumps({"title": "changed title"}))
    response = test_client.get("/things?format=collection")
    assert_etag_changed(init_etag, response.headers, format_param="collection")


def test_collection_etag_changed_after_PUT(test_client, mock_sparql_with_one_td):
    response = test_client.get("/things?format=collection")
    init_etag = get_collection_etag()
    assert_etag_in_headers(response.headers, format_param="collection")
    with open(DATA_PATH / "smart-coffee-machine.td.jsonld") as fp:
        test_client.put(
            "/things/urn:uuid:55f01138-5c96-4b3d-a5d0-81319a2db677",
            data=fp.read(),
            content_type="application/json",
        )
    response = test_client.get("/things?format=collection")
    assert_etag_changed(init_etag, response.headers, format_param="collection")


def test_collection_etag_changed_after_POST(test_client, mock_sparql_empty_endpoint):
    response = test_client.get("/things?format=collection")
    init_etag = get_collection_etag()
    assert_etag_in_headers(response.headers, format_param="collection")
    with open(DATA_PATH / "smart-coffee-machine.td.jsonld") as fp:
        test_client.post("/things", data=fp.read(), content_type="application/json")
    response = test_client.get("/things?format=collection")
    assert_etag_changed(init_etag, response.headers, format_param="collection")
