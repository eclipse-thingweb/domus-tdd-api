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
from unittest.mock import patch
from tdd.errors import ExternalDependencyError
from tdd.td import frame_td_nt_content
from tdd.common import frame_nt_content


# Test 1: Verify Node.js crash raises ExternalDependencyError
@patch("tdd.common.subprocess.Popen")
def test_frame_nt_content_subprocess_failure(mock_popen):
    """Test that subprocess failure raises ExternalDependencyError with 502 status"""
    # Mock subprocess failure
    mock_process = mock_popen.return_value
    mock_process.communicate.return_value = ("", "Error parsing custom context")
    mock_process.returncode = 1

    with pytest.raises(ExternalDependencyError) as exc_info:
        frame_nt_content(
            '<http://example.org/thing> <http://example.org/prop> "value" .', {}
        )

    # Generic error message without exposing internal details
    assert "JSON-LD framing process failed" in str(exc_info.value.message)
    assert exc_info.value.status_code == 502


# Test 2: Verify empty string is safely intercepted
@patch("tdd.td.frame_nt_content")
def test_frame_td_nt_content_empty_response(mock_frame_nt):
    """Test that empty response from frame_nt_content raises ExternalDependencyError"""
    # Mock lower-level function returning empty string
    mock_frame_nt.return_value = "   \n"

    with pytest.raises(ExternalDependencyError) as exc_info:
        frame_td_nt_content(
            "urn:dev:ops:32473-123",
            "dummy_nt_content",
            ["https://www.w3.org/2019/wot/td/v1"],
        )

    assert "Received empty response" in str(exc_info.value.message)
    assert exc_info.value.status_code == 502


# Test 3: Verify malformed JSON is safely intercepted
@patch("tdd.td.frame_nt_content")
def test_frame_td_nt_content_malformed_json(mock_frame_nt):
    """Test that malformed JSON output raises ExternalDependencyError"""
    # Mock lower-level function returning truncated JSON
    mock_frame_nt.return_value = '{"@context": "http'

    with pytest.raises(ExternalDependencyError) as exc_info:
        frame_td_nt_content(
            "urn:dev:ops:32473-123",
            "dummy_nt_content",
            ["https://www.w3.org/2019/wot/td/v1"],
        )

    # Generic error message without exposing JSON parsing details
    assert "Invalid JSON output" in str(exc_info.value.message)
    assert exc_info.value.status_code == 502


# Test 4: Verify valid response is processed correctly
@patch("tdd.td.frame_nt_content")
def test_frame_td_nt_content_valid_response(mock_frame_nt):
    """Test that valid JSON response is processed correctly"""
    mock_frame_nt.return_value = '{"@type": "Thing", "id": "urn:test:thing"}'

    result = frame_td_nt_content(
        "urn:test:thing",
        "<urn:test:thing> a <http://www.w3.org/ns/td#Thing> .",
        ["https://www.w3.org/2019/wot/td/v1"],
    )

    assert result["@type"] == "Thing"
    assert result["id"] == "urn:test:thing"
    assert "registration" in result
    assert "retrieved" in result["registration"]


# Test 5: Verify subprocess with zero exit code succeeds
@patch("tdd.common.subprocess.Popen")
def test_frame_nt_content_subprocess_success(mock_popen):
    """Test that subprocess success returns valid output"""
    # Mock successful subprocess
    mock_process = mock_popen.return_value
    mock_process.communicate.return_value = ('{"@type": "Thing"}', "")
    mock_process.returncode = 0

    result = frame_nt_content(
        "<http://example.org/thing> a <http://www.w3.org/ns/td#Thing> .",
        {"@context": "https://www.w3.org/2019/wot/td/v1"},
    )

    assert result == '{"@type": "Thing"}'


# Test 6: Verify log injection attack is prevented
@patch("tdd.common.subprocess.Popen")
@patch("tdd.common.logging.error")
def test_frame_nt_content_log_injection_prevention(mock_log_error, mock_popen):
    """Test that newlines in stderr are sanitized to prevent log injection"""
    # Mock subprocess failure with malicious stderr containing newlines
    mock_process = mock_popen.return_value
    malicious_stderr = "Error\nFAKE LOG ENTRY: Admin logged in\nAnother line"
    mock_process.communicate.return_value = ("", malicious_stderr)
    mock_process.returncode = 1

    with pytest.raises(ExternalDependencyError):
        frame_nt_content(
            "<http://example.org/thing> a <http://www.w3.org/ns/td#Thing> .", {}
        )

    # Verify that the logged message uses repr() to escape newlines
    mock_log_error.assert_called_once()
    logged_message = mock_log_error.call_args[0][0]
    # The repr() should escape the newlines as \n
    assert "\\n" in logged_message
    # The raw newline should NOT be in the log
    assert "\nFAKE LOG ENTRY" not in logged_message


# Integration Test: Verify ExternalDependencyError returns HTTP 502
def test_external_dependency_error_returns_502(test_client):
    """Integration test: Verify that ExternalDependencyError is properly handled as HTTP 502"""
    from unittest.mock import patch
    from tdd.errors import ExternalDependencyError

    # Patch get_td_description to raise ExternalDependencyError
    with patch("tdd.get_td_description") as mock_get_td:
        mock_get_td.side_effect = ExternalDependencyError(
            "JSON-LD framing process failed."
        )

        # Make GET request to /things/{id}
        response = test_client.get("/things/urn:test:thing")

        # Verify HTTP 502 status
        assert response.status_code == 502

        # Verify Content-Type is application/problem+json
        assert response.content_type == "application/problem+json"

        # Verify error response structure
        error_response = response.json
        assert error_response["title"] == "External Dependency Error"
        assert error_response["status"] == 502
        assert "upstream dependency failed" in error_response["detail"].lower()

        # Verify no internal details are leaked (English message only)
        assert "JSON-LD framing process failed" in error_response["detail"]
        assert "frame-jsonld.js" not in error_response["detail"]
        assert "stderr" not in error_response["detail"]
