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
import pytest
from rdflib import Graph

from tdd.errors import TTLMandatoryError
from tdd.registration import (
    delete_registration_information,
    get_registration_dict,
    update_registration,
    validate_ttl,
)
from tdd.tests.conftest import DATA_PATH


def test_get_registration_dict_from_rdf():
    td_id = "urn:uuid:55f01138-5c96-4b3d-a5d0-81319a2db677"
    rdf_graph = Graph().parse(DATA_PATH / "registration-data.ttl", format="ttl")
    registration = get_registration_dict(td_id, rdf_graph)
    assert registration == {
        "created": "2022-03-17T17:03:48.095473+01:00",
        "modified": "2022-03-17T18:03:48.095473+01:00",
    }


def test_delete_registration_information_from_rdf():
    td_id = "urn:uuid:55f01138-5c96-4b3d-a5d0-81319a2db677"
    rdf_graph = Graph().parse(DATA_PATH / "registration-data.ttl", format="ttl")
    delete_registration_information(td_id, rdf_graph)
    assert len(rdf_graph) == 1
    assert (
        "<urn:uuid:55f01138-5c96-4b3d-a5d0-81319a2db677> a"
        " <https://www.w3.org/2019/wot/td#Thing> ."
        == rdf_graph.serialize(format="ttl").strip()
    )


def test_validation_mandatory_ttl_missing_ttl():
    with open(DATA_PATH / "smart-coffee-machine.td.jsonld") as fp:
        ld_content = json.loads(fp.read())

    with pytest.raises(TTLMandatoryError):
        validate_ttl(ld_content, True)


def test_registration_ttl_bigger_than_max_ttl():
    registration = {
        "ttl": 500,
    }

    new_registration = update_registration(registration, max_ttl=10)
    assert new_registration["ttl"] == 10
    assert new_registration["expires"] == "2022-01-01T00:00:10+00:00"


def test_registration_no_created_date():
    registration = {}
    new_registration = update_registration(registration)
    assert new_registration["created"] == "2022-01-01T00:00:00+00:00"
    assert new_registration["modified"] == "2022-01-01T00:00:00+00:00"


def test_registration_modified():
    registration = {}
    new_registration = update_registration(
        registration, created_date="2010-03-17T17:31:50.469472+01:00"
    )
    assert new_registration["created"] == "2010-03-17T17:31:50.469472+01:00"
    assert new_registration["modified"] == "2022-01-01T00:00:00+00:00"


def test_registration_expires_only():
    registration = {"expires": "2022-03-17T17:31:50.469472+01:00"}
    new_registration = update_registration(registration)
    assert new_registration["expires"] == "2022-03-17T17:31:50.469472+01:00"


def test_registration_expires_and_ttl():
    registration = {"expires": "2012-03-17T17:31:50.469472+01:00", "ttl": 10}
    new_registration = update_registration(registration)
    assert new_registration["expires"] == "2022-01-01T00:00:10+00:00"


def test_registration_max_ttl_before_expires():
    registration = {"expires": "2022-03-17T17:31:50.469472+01:00"}
    new_registration = update_registration(registration, max_ttl=10)
    assert new_registration["expires"] == "2022-01-01T00:00:10+00:00"


def test_registration_max_ttl_after_expires():
    registration = {"expires": "2022-03-17T17:31:50.469472+01:00"}
    new_registration = update_registration(registration, max_ttl=10000000)
    assert new_registration["expires"] == "2022-03-17T17:31:50.469472+01:00"


def test_registration_expires_with_timezone():
    registration = {"expires": "2022-01-01T03:00:00+02:00"}
    new_registration = update_registration(registration, max_ttl=7200)
    # now is defined as 2022-01-01T00:00:00+00:00
    # then now + max_ttl = 2022-01-01T02:00:00+00:00
    # now + max_ttl > 2022-01-01T03:00:00+02:00
    # <=> now + max_ttl > 2022-01-01T01:00:00+00:00   set expires as UTC
    assert new_registration["expires"] == "2022-01-01T03:00:00+02:00"
