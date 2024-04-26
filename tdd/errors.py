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

from rdflib import BNode, RDF, SH, URIRef


from tdd.utils import (
    POSSIBLE_MIMETYPES,
    find_blank_node_path,
    construct_describe_graph,
    full_uri_to_prefixed,
)


def jsonschema_error(errors):
    return {
        "validationErrors": [
            {
                "field": error.json_path,
                "description": error.message,
            }
            for error in errors
        ],
    }


def _get_shacl_errors_as_tuples(errors):
    for error_uri, _, _ in errors.triples((None, RDF.type, SH.ValidationResult)):
        path = None
        message = None
        value = None
        node = None
        for _, predicate, object_node in errors.triples((error_uri, None, None)):
            if predicate == SH.resultPath:
                path = object_node
            elif predicate == SH.resultMessage:
                message = object_node
            elif predicate == SH.value:
                value = object_node
            elif predicate == SH.focusNode:
                node = object_node
        yield node, path, message, value


def shacl_validation_error(errors, td_uri, td_graph):
    validationErrors = []
    for node, path, message, value in _get_shacl_errors_as_tuples(errors):
        node = td_uri
        if isinstance(value, BNode):
            path = find_blank_node_path(
                value, td_uri, td_graph, last_node=node, last_predicate=path
            )
            value = construct_describe_graph(value, td_graph).serialize(format="turtle")
        elif value is not None:
            value = value.n3()
        if isinstance(path, URIRef):
            path = full_uri_to_prefixed(path)
        validationErrors.append(
            {
                "field": path,
                "description": message.toPython(),
                "node": node.toPython(),
                "value": value,
            }
        )
    return {"validationErrors": validationErrors}


class AppException(Exception):
    status_code = 400
    title = "Bad Request"
    message = "Something went wrong..."
    message_fr = "Quelque chose n'a pas fonctionné..."
    message_de = "Etwas ist schief gelaufen..."
    td_id = None

    def __init__(
        self,
        message=None,
        message_fr=None,
        message_de=None,
        status_code=None,
        payload=None,
    ):
        super().__init__()
        if message is not None:
            self.message = message
        if message_fr is not None:
            self.message_fr = message_fr
        if message_de is not None:
            self.message_de = message_de
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self, lang):
        rv = dict(self.payload or ())
        rv["title"] = self.title
        if lang == "fr":
            rv["detail"] = self.message_fr
        elif lang == "de":
            rv["detail"] = self.message_de
        else:
            rv["detail"] = self.message
        rv["status"] = self.status_code
        if self.td_id is not None:
            rv["instance"] = self.td_id
        return rv


class JSONSchemaError(AppException):
    message = "The input did not pass the JSON Schema Validation"
    message_fr = "L'entrée n'a pas passé la validation du schéma JSON"
    message_de = "Die Eingabe hat die JSON-Schema-Validierung nicht bestanden"

    def __init__(self, error, td_id=None):
        super().__init__()
        self.td_id = td_id
        self.payload = jsonschema_error(error)


class JSONDecodeError(AppException):
    def __init__(self, error):
        super().__init__(
            f"The input did not pass the JSON Decoding: {str(error)}",
            f"L'entrée n'a pas passé le décodage JSON: {str(error)}",
            f"Die Eingabe hat die JSON-Decodierung nicht bestanden: {str(error)}",
        )


class IDMismatchError(AppException):
    def __init__(self, ld_content_id, param_id):
        super().__init__(
            f"TD id '{ld_content_id}' in json and id in route "
            f"'{param_id}' are not compatible",
            f"TD id '{ld_content_id}' dans le json et id dans la route "
            f"'{param_id}' ne sont pas compatibles",
            f"TD id '{ld_content_id}' in json und id in route "
            f"'{param_id}' sind nicht kompatibel",
        )


class FusekiError(AppException):
    title = "SPARQL Endpoint Error"
    status_code = 500

    def __init__(self, response):
        super().__init__(response.text)


class OrderbyError(AppException):
    title = "Order By Error"
    status_code = 500

    def __init__(self, order_key):
        super().__init__(f"The key {order_key} is not orderable")


class RDFValidationError(AppException):
    title = "RDF triples are not well formatted"

    def __init__(self, text, td_id=None, errors=None, td_graph=None):
        super().__init__(text)
        self.td_id = td_id
        if errors:
            self.payload = shacl_validation_error(
                errors, td_uri=td_id, td_graph=td_graph
            )


class TTLMandatoryError(AppException):
    def __init__(self, ld_content):
        super().__init__(
            f"TD '{ld_content['id'] or 'anonymous'}' does not contain a mandatory TTL"
            " value",
            f"TD '{ld_content['id'] or 'anonymous'}' ne contient pas de valeur TTL obligatoire"
            " ",
            f"TD '{ld_content['id'] or 'anonymous'}' enthält keinen obligatorischen TTL"
            " Wert",
        )


class IDNotFound(AppException):
    title = "ID Not Found"
    status_code = 404


class WrongMimeType(AppException):
    title = "Wrong MimeType"

    def __init__(self, provided_mimetype):
        super().__init__(
            f"Provided mimetype '{provided_mimetype}' is not supported. Only "
            f"{', '.join(POSSIBLE_MIMETYPES)}, application/json are allowed"
        )
