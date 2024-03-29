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
from rdflib import Graph
from rdflib.compare import graph_diff
from tdd.td import clear_expired_td

from tdd.tests.conftest import (
    DATA_PATH,
    add_registration_to_td,
    assert_only_on_known_errors,
)


def test_tdd_route(test_client):
    tdd_response = test_client.get("/")
    assert tdd_response.status_code == 200
    assert tdd_response.content_type == "application/td+json"
    with open(DATA_PATH / "tdd-description.json") as fp:
        assert tdd_response.json == json.load(fp)


def test_GET_thing_OK(test_client, mock_sparql_with_one_td):
    td_id = "urn:uuid:55f01138-5c96-4b3d-a5d0-81319a2db677"
    with open(DATA_PATH / "smart-coffee-machine.td.jsonld") as fp:
        already_present_td = json.load(fp)
        add_registration_to_td(already_present_td)
    get_response = test_client.get(f"/things/{td_id}")
    assert get_response.status_code == 200
    td = get_response.json
    td["registration"] = already_present_td[
        "registration"
    ]  # use the proper registration since this test does not test this
    diff = Compare().check(already_present_td, td)
    assert_only_on_known_errors(diff)


def test_GET_expired_thing(test_client, mock_sparql_with_one_expired_td):
    td_id = "urn:uuid:55f01138-5c96-4b3d-a5d0-81319a2db677"
    get_response = test_client.get(f"/things/{td_id}")
    assert get_response.status_code == 200
    clear_expired_td()
    get_response = test_client.get(f"/things/{td_id}")
    assert get_response.status_code == 404


def test_GET_thing_content_negociation(test_client, mock_sparql_with_one_td):
    td_id = "urn:uuid:55f01138-5c96-4b3d-a5d0-81319a2db677"
    for mime_type, file_extension in [
        ("text/turtle", "ttl"),
        ("application/rdf+xml", "xml"),
        ("text/n3", "n3"),
    ]:
        with open(DATA_PATH / f"smart-coffee-machine.{file_extension}") as fp:
            already_present_td = fp.read()
        get_response = test_client.get(
            f"/things/{td_id}", headers={"Accept": mime_type}
        )
        assert get_response.status_code == 200
        td = get_response.get_data()
        g_expected = Graph()
        g_expected.parse(data=already_present_td, format=mime_type)
        g = Graph()
        g.parse(data=td, format=mime_type)

        in_both, only_expected, only_got = graph_diff(g, g_expected)
        assert len(in_both) == len(g)
        assert len(only_expected) == 0
        assert len(only_got) == 0
