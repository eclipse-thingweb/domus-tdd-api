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

from tdd.tests.conftest import (
    DATA_PATH,
)


def test_PUT_thing_bad_content_type(test_client):
    with open(DATA_PATH / "smart-coffee-machine.td.jsonld") as fp:
        put_response = test_client.put(
            "/things/urn:test:coucou",
            data=fp.read(),
            content_type="text/poulet-xml",
        )
        assert put_response.status_code == 400
        assert "Wrong MimeType" in put_response.json["title"]


def test_PUT_thing_bad_json(test_client):
    with open(DATA_PATH / "bad-json.td.jsonld") as fp:
        put_response = test_client.put(
            "/things/urn:test:coucou",
            data=fp.read(),
            content_type="application/json",
        )
        assert put_response.status_code == 400
        assert "validationErrors" not in put_response.json
        assert "JSON Decoding" in put_response.json["detail"]


def test_PUT_thing_bad_json_schema(test_client):
    with open(DATA_PATH / "bad-json-schema.td.jsonld") as fp:
        put_response = test_client.put(
            "/things/urn:uuid:55f01138-5c96-4b3d-a5d0-81319a2db677",
            data=fp.read(),
            content_type="application/json",
        )
        assert put_response.status_code == 400
        assert "validationErrors" in put_response.json
        assert "JSON Schema Validation" in put_response.json["detail"]
        assert put_response.json == {
            "validationErrors": [
                {
                    "field": "$",
                    "description": "'security' is a required property",
                },
                {
                    "field": "$",
                    "description": "'securityDefinitions' is a required property",
                },
            ],
            "instance": "urn:uuid:55f01138-5c96-4b3d-a5d0-81319a2db677",
            "detail": "The input did not pass the JSON Schema Validation",
            "title": "Bad Request",
            "status": 400,
        }


def test_PUT_thing_bad_identifier(test_client):
    with open(DATA_PATH / "smart-coffee-machine.td.jsonld") as fp:
        put_response = test_client.put(
            "/things/urn:test:coucou",
            data=fp.read(),
            content_type="application/json",
        )
        assert put_response.status_code == 400
        assert "validationErrors" not in put_response.json
        assert "not compatible" in put_response.json["detail"]


def test_PUT_thing_ok(test_client, mock_sparql_empty_endpoint):
    with open(DATA_PATH / "smart-coffee-machine.td.jsonld") as fp:
        put_response = test_client.put(
            "/things/urn:uuid:55f01138-5c96-4b3d-a5d0-81319a2db677",
            data=fp.read(),
            content_type="application/json",
        )
        assert put_response.status_code == 201
        assert (
            put_response.headers["Location"]
            == "urn:uuid:55f01138-5c96-4b3d-a5d0-81319a2db677"
        )


def test_PUT_thing_existing_TD(test_client, mock_sparql_with_one_td):
    with open(DATA_PATH / "smart-coffee-machine.td.jsonld") as fp:
        put_response = test_client.put(
            "/things/urn:uuid:55f01138-5c96-4b3d-a5d0-81319a2db677",
            data=fp.read(),
            content_type="application/json",
        )
        assert put_response.status_code == 204


def test_PUT_thing_ttl_shacl_validation_ok(test_client, mock_sparql_empty_endpoint):
    with open(DATA_PATH / "smart-coffee-machine_shacl_ok.ttl") as fp:
        response = test_client.put(
            "/things/urn:uuid:55f01138-5c96-4b3d-a5d0-81319a2db677",
            data=fp.read(),
            content_type="text/turtle",
        )
        assert response.status_code == 201


def test_POST_thing_ttl_shacl_validation_ok(test_client, mock_sparql_empty_endpoint):
    with open(DATA_PATH / "smart-coffee-machine_shacl_ok.ttl") as fp:
        response = test_client.post(
            "/things",
            data=fp.read(),
            content_type="text/turtle",
        )
        assert response.status_code == 201


def test_PUT_thing_ttl_shacl_validation_nok(test_client):
    with open(DATA_PATH / "smart-coffee-machine_shacl_nok.ttl") as fp:
        put_response = test_client.put(
            "/things/urn:uuid:55f01138-5c96-4b3d-a5d0-81319a2db677?check-schema=True",
            data=fp.read(),
            content_type="text/turtle",
        )
        assert put_response.status_code == 400
        assert "validationErrors" in put_response.json
        assert "RDF triples are not well formatted" in put_response.json["title"]
        assert (
            "The RDF triples are not conform with the SHACL validation"
            in put_response.json["detail"]
        )
        assert put_response.json["validationErrors"] == [
            {
                "field": "td:title",
                "description": "Value is not Literal with datatype rdf:langString",
                "node": "urn:uuid:55f01138-5c96-4b3d-a5d0-81319a2db677",
                "value": '"42"^^<http://www.w3.org/2001/XMLSchema#integer>',
            },
            {
                "field": "td:hasSecurityConfiguration",
                "description": (
                    "Less than 1 values on "
                    "<urn:uuid:55f01138-5c96-4b3d-a5d0-81319a2db677>->td:hasSecurityConfiguration"
                ),
                "node": "urn:uuid:55f01138-5c96-4b3d-a5d0-81319a2db677",
                "value": None,
            },
        ]


def test_POST_thing_ttl_shacl_validation_nok(test_client):
    with open(DATA_PATH / "smart-coffee-machine_shacl_nok.ttl") as fp:
        put_response = test_client.post(
            "/things",
            data=fp.read(),
            content_type="text/turtle",
        )
        assert put_response.status_code == 400
        assert "validationErrors" in put_response.json
        assert "RDF triples are not well formatted" in put_response.json["title"]
        assert (
            "The RDF triples are not conform with the SHACL validation"
            in put_response.json["detail"]
        )
        assert put_response.json["validationErrors"] == [
            {
                "field": "td:title",
                "description": "Value is not Literal with datatype rdf:langString",
                "node": "urn:uuid:55f01138-5c96-4b3d-a5d0-81319a2db677",
                "value": '"42"^^<http://www.w3.org/2001/XMLSchema#integer>',
            },
            {
                "field": "td:hasSecurityConfiguration",
                "description": (
                    "Less than 1 values on "
                    "<urn:uuid:55f01138-5c96-4b3d-a5d0-81319a2db677>->td:hasSecurityConfiguration"
                ),
                "node": "urn:uuid:55f01138-5c96-4b3d-a5d0-81319a2db677",
                "value": None,
            },
        ]


def test_PUT_thing_ttl_do_not_shacl_validation_nok(
    test_client, mock_sparql_empty_endpoint
):
    with open(DATA_PATH / "smart-coffee-machine_shacl_nok.ttl") as fp:
        put_response = test_client.put(
            "/things/urn:uuid:55f01138-5c96-4b3d-a5d0-81319a2db677?check-schema=false",
            data=fp.read(),
            content_type="text/turtle",
        )
        assert put_response.status_code == 201


def test_DELETE_thing_ok(test_client, mock_sparql_with_one_td):
    td_id = "urn:uuid:55f01138-5c96-4b3d-a5d0-81319a2db677"
    delete_response = test_client.delete(f"/things/{td_id}")
    assert delete_response.status_code == 204
    get_response = test_client.get(f"/things/{td_id}")
    assert get_response.status_code == 404


def test_PATCH_thing_ok(test_client, mock_sparql_with_one_td):
    td_id = "urn:uuid:55f01138-5c96-4b3d-a5d0-81319a2db677"
    patch_response = test_client.patch(
        f"/things/{td_id}", data=json.dumps({"title": "changed title"})
    )
    assert patch_response.status_code == 204
    get_response = test_client.get(f"/things/{td_id}").json
    assert get_response["title"] == "changed title"


def test_PATCH_thing_patch_format_error(test_client):
    td_id = "urn:uuid:55f01138-5c96-4b3d-a5d0-81319a2db677"
    patch_response = test_client.patch(f"/things/{td_id}", data="non json content")
    assert patch_response.status_code == 400
    content = patch_response.json
    assert "detail" in content
    assert "The input did not pass the JSON Decoding" in content["detail"]


def test_PATCH_thing_JSONSchema_validation_error(test_client, mock_sparql_with_one_td):
    td_id = "urn:uuid:55f01138-5c96-4b3d-a5d0-81319a2db677"
    patch_response = test_client.patch(
        f"/things/{td_id}", data=json.dumps({"title": {"value": "invalid JSONSchema"}})
    )
    assert patch_response.status_code == 400
    content = patch_response.json
    assert "detail" in content
    assert "The input did not pass the JSON Schema Validation" in content["detail"]
    assert "validationErrors" in content
    assert content["validationErrors"] == [
        {
            "field": "$.title",
            "description": "{'value': 'invalid JSONSchema'} is not of type 'string'",
        }
    ]


def test_PATCH_thing_patch_TD_not_found(test_client, mock_sparql_empty_endpoint):
    td_id = "urn:uuid:55f01138-5c96-4b3d-a5d0-81319a2db677"
    patch_response = test_client.patch(
        f"/things/{td_id}", data=json.dumps({"title": "changed title"})
    )
    assert patch_response.status_code == 404
    content = patch_response.json
    assert "title" in content
    assert content["title"] == "ID Not Found"
