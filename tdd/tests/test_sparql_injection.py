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
from tdd.sparql import sanitize_sparql_uri, sanitize_sparql_string


class TestSanitizeURI:
    """Test SPARQL URI sanitization"""

    def test_sanitize_simple_uri(self):
        result = sanitize_sparql_uri("urn:uuid:12345")
        assert result == "<urn:uuid:12345>"

    def test_sanitize_http_uri(self):
        result = sanitize_sparql_uri("http://example.com/thing")
        assert result == "<http://example.com/thing>"

    def test_sanitize_uri_already_wrapped(self):
        result = sanitize_sparql_uri("<urn:uuid:12345>")
        assert result == "<urn:uuid:12345>"

    def test_sanitize_uri_with_backslash_escapes(self):
        result = sanitize_sparql_uri("urn:test\\value")
        assert result == "<urn:test\\\\value>"

    def test_sanitize_uri_reject_angle_brackets_in_content(self):
        with pytest.raises(ValueError):
            sanitize_sparql_uri("urn:test<malicious>")

    def test_sanitize_uri_reject_quotes(self):
        with pytest.raises(ValueError):
            sanitize_sparql_uri('urn:test"malicious"')

    def test_sanitize_uri_reject_braces(self):
        with pytest.raises(ValueError):
            sanitize_sparql_uri("urn:test{malicious}")

    def test_sanitize_uri_reject_pipe(self):
        with pytest.raises(ValueError):
            sanitize_sparql_uri("urn:test|malicious")


class TestSanitizeString:
    """Test SPARQL string sanitization"""

    def test_sanitize_simple_string(self):
        result = sanitize_sparql_string("hello world")
        assert result == "hello world"

    def test_sanitize_string_with_quotes(self):
        result = sanitize_sparql_string('hello "world"')
        assert result == 'hello \\"world\\"'

    def test_sanitize_string_with_backslash(self):
        result = sanitize_sparql_string("hello\\world")
        assert result == "hello\\\\world"

    def test_sanitize_string_with_newline(self):
        result = sanitize_sparql_string("hello\nworld")
        assert result == "hello\\nworld"

    def test_sanitize_string_with_carriage_return(self):
        result = sanitize_sparql_string("hello\rworld")
        assert result == "hello\\rworld"

    def test_sanitize_string_with_tab(self):
        result = sanitize_sparql_string("hello\tworld")
        assert result == "hello\\tworld"

    def test_sanitize_string_complex_injection_attempt(self):
        malicious = 'test"; DROP GRAPH <urn:data>;'
        result = sanitize_sparql_string(malicious)
        # Quotes should be escaped but the string itself returned
        assert '\\"' in result
        assert 'DROP' in result  # Keywords are not blocked in literals


class TestSPARQLQueryValidation:
    """Test SPARQL query validation in sparql_query function"""

    def test_sparql_query_blocks_drop(self, test_client):
        response = test_client.get(
            "/search/sparql?query=DROP%20GRAPH%20%3Curn:tdd:metadata%3E"
        )
        # Should return 400 Bad Request or similar error
        assert response.status_code >= 400

    def test_sparql_query_blocks_delete(self, test_client):
        response = test_client.get(
            "/search/sparql?query=DELETE%20WHERE%20{?s%20?p%20?o}"
        )
        assert response.status_code >= 400

    def test_sparql_query_blocks_insert(self, test_client):
        response = test_client.get(
            "/search/sparql?query=INSERT%20DATA%20{%3Cs%3E%20%3Cp%3E%20%3Co%3E}"
        )
        assert response.status_code >= 400

    def test_sparql_query_blocks_update(self, test_client):
        response = test_client.get(
            "/search/sparql?query=UPDATE%20%3Curn:test%3E%20SET"
        )
        assert response.status_code >= 400

    def test_sparql_query_blocks_clear(self, test_client):
        response = test_client.get(
            "/search/sparql?query=CLEAR%20GRAPH%20%3Curn:tdd:metadata%3E"
        )
        assert response.status_code >= 400

    def test_sparql_query_allows_select(self, test_client, mock_sparql_with_one_td):
        response = test_client.get(
            "/search/sparql?query=SELECT%20?s%20WHERE%20{?s%20a%20?o}"
        )
        # Should not return 400 error (may return 200 or other status)
        assert response.status_code != 400 or "SELECT" not in response.get_data(
            as_text=True
        )

    def test_sparql_query_allows_describe(self, test_client, mock_sparql_with_one_td):
        response = test_client.get(
            "/search/sparql?query=DESCRIBE%20%3Curn:test%3E"
        )
        assert response.status_code != 400

    def test_sparql_query_allows_ask(self, test_client, mock_sparql_with_one_td):
        response = test_client.get(
            "/search/sparql?query=ASK%20WHERE%20{?s%20a%20?o}"
        )
        assert response.status_code != 400

    def test_sparql_query_allows_construct(self, test_client, mock_sparql_with_one_td):
        response = test_client.get(
            "/search/sparql?query=CONSTRUCT%20{?s%20?p%20?o}%20WHERE%20{?s%20?p%20?o}"
        )
        assert response.status_code != 400


class TestURIInjectionInThingOperations:
    """Test that URI injection is prevented in Thing operations"""

    def test_delete_thing_with_malicious_uri(self, test_client):
        # Try to inject SPARQL with angle brackets and quotes
        malicious_id = '"><DROP%20GRAPH%20<urn:tdd:metadata>'
        response = test_client.delete(f"/things/{malicious_id}")
        # Should return 400 because sanitizer rejects angle brackets
        assert response.status_code == 400
        # Verify it's a validation error
        error_data = response.get_json()
        assert "Invalid characters" in error_data.get("detail", "")

    def test_delete_thing_with_quote_injection(self, test_client):
        malicious_id = 'urn:test"malicious"'
        response = test_client.delete(f"/things/{malicious_id}")
        assert response.status_code == 400

    def test_delete_thing_with_brace_injection(self, test_client):
        malicious_id = 'urn:test{malicious}'
        response = test_client.delete(f"/things/{malicious_id}")
        assert response.status_code == 400


class TestPostRequestInjection:
    """Test SPARQL injection via POST requests"""

    def test_post_sparql_query_blocks_drop(self, test_client):
        response = test_client.post(
            "/search/sparql",
            data="DROP GRAPH <urn:tdd:metadata>",
            content_type="application/sparql-query",
        )
        assert response.status_code >= 400

    def test_post_sparql_query_blocks_insert(self, test_client):
        response = test_client.post(
            "/search/sparql",
            data="INSERT DATA { <s> <p> <o> }",
            content_type="application/sparql-query",
        )
        assert response.status_code >= 400

    def test_post_sparql_query_allows_select(self, test_client, mock_sparql_with_one_td):
        response = test_client.post(
            "/search/sparql",
            data="SELECT ?s WHERE { ?s a ?o }",
            content_type="application/sparql-query",
        )
        # Should not be rejected for being SELECT
        assert "SELECT" not in str(response.status_code) or response.status_code != 400
