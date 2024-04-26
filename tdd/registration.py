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

import datetime
from copy import copy
from rdflib import URIRef, Literal, XSD, BNode


from tdd.errors import TTLMandatoryError
from tdd.utils import TDD


def validate_ttl(ld_content, mandate_ttl):
    if mandate_ttl and (
        "registration" not in ld_content or "ttl" not in ld_content["registration"]
    ):
        raise TTLMandatoryError(ld_content)


def get_registration_dict(uri, rdf_graph):
    registration_query = (
        "PREFIX discovery: <https://www.w3.org/2022/wot/discovery-ontology#>"
        "SELECT DISTINCT ?created ?modified ?expires ?ttl "
        "WHERE {"
        f"  <{uri}> discovery:hasRegistrationInformation ?reg."
        "   OPTIONAL{?reg discovery:dateCreated ?created}"
        "   OPTIONAL{?reg discovery:dateModified ?modified}"
        "   OPTIONAL{?reg discovery:expires ?expires}"
        "   OPTIONAL{?reg discovery:ttl ?ttl}"
        "}"
    )
    results = [row for row in rdf_graph.query(registration_query)]
    keys = ["created", "modified", "expires", "ttl"]
    if len(results) == 0:
        return {}
    registration = dict(
        zip(keys, [x.value.isoformat() if x is not None else None for x in results[0]])
    )
    for key, value in dict(registration).items():
        if value is None:
            del registration[key]
    return registration


def delete_registration_information(uri, rdf_graph):
    rdf_graph.remove((URIRef(uri), TDD.hasRegistrationInformation, None))
    rdf_graph.remove((None, TDD.dateCreated, None))
    rdf_graph.remove((None, TDD.dateModified, None))
    rdf_graph.remove((None, TDD.expires, None))
    rdf_graph.remove((None, TDD.ttl, None))


def update_registration(registration, created_date=None, max_ttl=None):
    today = datetime.datetime.now().astimezone()
    new_registration = copy(registration)
    if created_date is not None:
        new_registration["created"] = created_date
        new_registration["modified"] = today.isoformat()
    else:
        new_registration["created"] = today.isoformat()
        new_registration["modified"] = today.isoformat()
    if "ttl" in new_registration:
        ttl = new_registration["ttl"]
        if max_ttl is not None and int(ttl) > max_ttl:
            new_registration["ttl"] = max_ttl
        new_registration["expires"] = (
            today + datetime.timedelta(seconds=new_registration["ttl"])
        ).isoformat()
    elif "expires" in new_registration:
        expires = datetime.datetime.fromisoformat(new_registration["expires"])
        if max_ttl is not None:
            max_expires = today + datetime.timedelta(seconds=max_ttl)
            if max_expires < expires:
                new_registration["expires"] = max_expires.isoformat()
            else:
                new_registration["expires"] = expires.isoformat()
        else:
            new_registration["expires"] = expires.isoformat()
    return new_registration


def yield_registration_triples(td_uri, registration):
    registration_uri = BNode()
    yield (
        td_uri,
        TDD["hasRegistrationInformation"],
        registration_uri,
    )
    if "created" in registration:
        yield (
            registration_uri,
            TDD["dateCreated"],
            Literal(registration["created"], datatype=XSD.dateTime),
        )
    if "modified" in registration:
        yield (
            registration_uri,
            TDD["dateModified"],
            Literal(registration["modified"], datatype=XSD.dateTime),
        )
    if "expires" in registration:
        yield (
            registration_uri,
            TDD["expires"],
            Literal(registration["expires"], datatype=XSD.datetTime),
        )
    if "ttl" in registration:
        yield (
            registration_uri,
            TDD["ttl"],
            Literal(registration["ttl"], datatype=XSD.datetTime),
        )
    if "retrieve" in registration:
        yield (
            registration_uri,
            TDD["retrieve"],
            Literal(registration["retrieve"], datatype=XSD.datetTime),
        )
