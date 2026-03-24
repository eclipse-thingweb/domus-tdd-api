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

import pytest
from tdd.sparql import sanitize_sparql_uri
from tdd.errors import IncorrectlyDefinedParameter


class TestSanitizeURI:
    """Test SPARQL URI sanitization"""

    def test_sanitize_simple_uri(self):
        # Returns the raw string – template supplies the angle brackets.
        result = sanitize_sparql_uri("urn:uuid:12345")
        assert result == "urn:uuid:12345"

    def test_sanitize_http_uri(self):
        result = sanitize_sparql_uri("http://example.com/thing")
        assert result == "http://example.com/thing"

    def test_sanitize_uri_already_wrapped(self):
        # Outer angle brackets are stripped so the template doesn't double-wrap.
        result = sanitize_sparql_uri("<urn:uuid:12345>")
        assert result == "urn:uuid:12345"

    def test_sanitize_uri_strips_whitespace(self):
        result = sanitize_sparql_uri("  urn:uuid:12345  ")
        assert result == "urn:uuid:12345"

    def test_sanitize_uri_reject_opening_angle_bracket(self):
        # < inside the URI content (not wrapping) must be rejected.
        with pytest.raises(IncorrectlyDefinedParameter):
            sanitize_sparql_uri("urn:test<malicious")

    def test_sanitize_uri_reject_angle_brackets_in_content(self):
        with pytest.raises(IncorrectlyDefinedParameter):
            sanitize_sparql_uri("urn:test<malicious>value")

    def test_sanitize_uri_reject_quotes(self):
        with pytest.raises(IncorrectlyDefinedParameter):
            sanitize_sparql_uri('urn:test"malicious"')

    def test_sanitize_uri_reject_braces(self):
        with pytest.raises(IncorrectlyDefinedParameter):
            sanitize_sparql_uri("urn:test{malicious}")

    def test_sanitize_uri_reject_pipe(self):
        with pytest.raises(IncorrectlyDefinedParameter):
            sanitize_sparql_uri("urn:test|malicious")

    def test_sanitize_uri_produces_valid_sparql_when_interpolated(self):
        # The sanitized value must not produce double angle brackets when the
        # template wraps it in <...>.
        sanitized = sanitize_sparql_uri("urn:uuid:12345")
        interpolated = f"SELECT ?s WHERE {{ ?s <urn:p> <{sanitized}> }}"
        assert "<<" not in interpolated
        assert ">>" not in interpolated


class TestSPARQLQueryValidation:
    """Test SPARQL query validation in sparql_query function"""

    # --- Blocked operations ---

    def test_sparql_query_blocks_drop(self, test_client):
        response = test_client.get(
            "/search/sparql?query=DROP%20GRAPH%20%3Curn:tdd:metadata%3E"
        )
        assert response.status_code == 400

    def test_sparql_query_blocks_delete(self, test_client):
        response = test_client.get(
            "/search/sparql?query=DELETE%20WHERE%20%7B%3Fs%20%3Fp%20%3Fo%7D"
        )
        assert response.status_code == 400

    def test_sparql_query_blocks_insert(self, test_client):
        response = test_client.get(
            "/search/sparql?query=INSERT%20DATA%20%7B%3Cs%3E%20%3Cp%3E%20%3Co%3E%7D"
        )
        assert response.status_code == 400

    def test_sparql_query_blocks_update(self, test_client):
        response = test_client.get(
            "/search/sparql?query=UPDATE%20%3Curn:test%3E%20SET"
        )
        assert response.status_code == 400

    def test_sparql_query_blocks_clear(self, test_client):
        response = test_client.get(
            "/search/sparql?query=CLEAR%20GRAPH%20%3Curn:tdd:metadata%3E"
        )
        assert response.status_code == 400

    # --- Allowed operations ---

    def test_sparql_query_allows_select(self, test_client, mock_sparql_with_one_td):
        response = test_client.get(
            "/search/sparql?query=SELECT%20%3Fs%20WHERE%20%7B%3Fs%20a%20%3Fo%7D"
        )
        assert response.status_code == 200

    def test_sparql_query_allows_select_with_prefix(
        self, test_client, mock_sparql_with_one_td
    ):
        # PREFIX declarations before SELECT must not be rejected.
        response = test_client.get(
            "/search/sparql?query="
            "PREFIX%20td%3A%20%3Chttps%3A%2F%2Fwww.w3.org%2F2019%2Fwot%2Ftd%23%3E"
            "%20SELECT%20%3Fs%20WHERE%20%7B%3Fs%20a%20td%3AThing%7D"
        )
        assert response.status_code == 200

    def test_sparql_query_allows_describe(
        self, test_client, mock_sparql_with_one_td
    ):
        response = test_client.get(
            "/search/sparql?query=DESCRIBE%20%3Curn:test%3E"
        )
        # Validator must pass it (not 400); mock may return 500 for graph results.
        assert response.status_code != 400

    def test_sparql_query_allows_ask(self, test_client, mock_sparql_with_one_td):
        response = test_client.get(
            "/search/sparql?query=ASK%20WHERE%20%7B%3Fs%20a%20%3Fo%7D"
        )
        assert response.status_code == 200

    def test_sparql_query_allows_construct(
        self, test_client, mock_sparql_with_one_td
    ):
        response = test_client.get(
            "/search/sparql?query=CONSTRUCT%20%7B%3Fs%20%3Fp%20%3Fo%7D"
            "%20WHERE%20%7B%3Fs%20%3Fp%20%3Fo%7D"
        )
        # Validator must pass it (not 400); mock may return 500 for graph results.
        assert response.status_code != 400

    def test_sparql_query_select_with_clear_in_uri_is_allowed(
        self, test_client, mock_sparql_with_one_td
    ):
        # A valid SELECT whose URI happens to contain "clear" must not be blocked.
        response = test_client.get(
            "/search/sparql?query=SELECT%20%3Fs%20WHERE%20"
            "%7B%3Fs%20%3Chttp%3A%2F%2Fexample.org%2Fclear-graph%3E%20%3Fo%7D"
        )
        assert response.status_code == 200


class TestURIInjectionInThingOperations:
    """Test that URI injection is prevented in Thing operations"""

    def test_delete_thing_with_quote_injection(self, test_client):
        malicious_id = "urn:test%22malicious%22"
        response = test_client.delete(f"/things/{malicious_id}")
        assert response.status_code == 400

    def test_delete_thing_with_brace_injection(self, test_client):
        malicious_id = "urn:test%7Bmalicious%7D"
        response = test_client.delete(f"/things/{malicious_id}")
        assert response.status_code == 400

    def test_delete_thing_with_angle_bracket_injection(self, test_client):
        malicious_id = "urn:test%3Cmalicious%3E"
        response = test_client.delete(f"/things/{malicious_id}")
        assert response.status_code == 400

    def test_delete_thing_error_detail_is_informative(self, test_client):
        malicious_id = "urn:test%22malicious%22"
        response = test_client.delete(f"/things/{malicious_id}")
        error_data = response.get_json()
        assert "Invalid characters" in error_data.get("detail", "")


class TestPostRequestInjection:
    """Test SPARQL injection via POST requests"""

    def test_post_sparql_query_blocks_drop(self, test_client):
        response = test_client.post(
            "/search/sparql",
            data="DROP GRAPH <urn:tdd:metadata>",
            content_type="application/sparql-query",
        )
        assert response.status_code == 400

    def test_post_sparql_query_blocks_insert(self, test_client):
        response = test_client.post(
            "/search/sparql",
            data="INSERT DATA { <s> <p> <o> }",
            content_type="application/sparql-query",
        )
        assert response.status_code == 400

    def test_post_sparql_query_allows_select(
        self, test_client, mock_sparql_with_one_td
    ):
        response = test_client.post(
            "/search/sparql",
            data="SELECT ?s WHERE { ?s a ?o }",
            content_type="application/sparql-query",
        )
        assert response.status_code == 200

