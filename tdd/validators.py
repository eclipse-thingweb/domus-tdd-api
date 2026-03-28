"""
Security validation module to prevent SPARQL and RDF injection attacks.
Enforces strict schema compliance and character allowlisting before data reaches the database layer.
"""

import re
import logging
from typing import List, Optional

from .errors import SecurityValidationError

# Initialize module-level logger for security auditing
logger = logging.getLogger(__name__)

# Strict regex for URI validation (RFC 3986 compliant).
# Allows standard URI characters INCLUDING percent-encoding ('%').
# Explicitly rejects structural SPARQL characters ('<', '>', '{', '}', '^', '`', '|', '\\', spaces).
# This ensures attackers cannot break out of the <URI> wrapper in SPARQL queries.
URI_REGEX = re.compile(r"^[a-zA-Z0-9\-._~:/?#\[\]@!$&'()*+,;=%]+$")


def validate_uri(uri: str) -> str:
    """
    Validates a URI string against injection patterns.
    """
    if not isinstance(uri, str) or not URI_REGEX.match(uri):
        logger.warning(f"SECURITY ALERT: Malformed or unsafe URI blocked: {uri}")
        raise SecurityValidationError(f"Malformed or unsafe URI detected: {uri}")
    return uri


def validate_uris(uris: List[str]) -> List[str]:
    """
    Validates a list of URIs.
    """
    if not isinstance(uris, list):
        logger.warning(
            "SECURITY ALERT: Expected a list of URIs, received different type."
        )
        raise SecurityValidationError("Expected a list of URIs.")
    return [validate_uri(u) for u in uris]


def validate_sort_order(sort_order: Optional[str]) -> str:
    """
    Enforces a strict allowlist for sorting order to prevent injection in ORDER BY clauses.
    """
    if sort_order and sort_order.upper() not in ["ASC", "DESC"]:
        logger.warning(f"SECURITY ALERT: Invalid sort order blocked: {sort_order}")
        raise SecurityValidationError("Invalid sort order detected.")
    return sort_order.upper() if sort_order else "ASC"
