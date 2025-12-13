"""PII (Personally Identifiable Information) redaction operation."""

import re
from typing import Optional, Set

from ..refiner import Refiner


class RedactPII(Refiner):
    """Redact sensitive information from text using regex patterns."""

    # Default regex patterns for common PII types
    PATTERNS = {
        "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        "phone": r"\b(?:\+?1[-.]?)?\(?([0-9]{3})\)?[-.]?([0-9]{3})[-.]?([0-9]{4})\b",
        "ip": r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b",
        "credit_card": r"\b(?:\d{4}[-\s]?){3}\d{4}\b",
        "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
        "url": r"https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&/=]*)",
    }

    # Replacement tokens for each PII type
    REPLACEMENTS = {
        "email": "[EMAIL]",
        "phone": "[PHONE]",
        "ip": "[IP]",
        "credit_card": "[CARD]",
        "ssn": "[SSN]",
        "url": "[URL]",
    }

    def __init__(
        self,
        redact_types: Optional[Set[str]] = None,
        custom_patterns: Optional[dict[str, str]] = None,
        custom_keywords: Optional[Set[str]] = None,
    ):
        """
        Initialize the PII redaction operation.

        Args:
            redact_types: Set of PII types to redact (default: all)
                Options: "email", "phone", "ip", "credit_card", "ssn", "url"
            custom_patterns: Dictionary of custom regex patterns to apply
                Format: {"name": "regex_pattern"}
            custom_keywords: Set of custom keywords to redact (case-insensitive)
        """
        self.redact_types = redact_types or set(self.PATTERNS.keys())
        self.custom_patterns = custom_patterns or {}
        self.custom_keywords = custom_keywords or set()

    def process(self, text: str) -> str:
        """
        Redact PII from the input text.

        Args:
            text: The input text

        Returns:
            Text with PII redacted
        """
        result = text

        # Apply standard PII patterns
        for pii_type in self.redact_types:
            if pii_type in self.PATTERNS:
                pattern = self.PATTERNS[pii_type]
                replacement = self.REPLACEMENTS.get(pii_type, "[REDACTED]")
                result = re.sub(pattern, replacement, result)

        # Apply custom patterns
        for name, pattern in self.custom_patterns.items():
            replacement = f"[{name.upper()}]"
            result = re.sub(pattern, replacement, result)

        # Apply custom keywords (case-insensitive)
        for keyword in self.custom_keywords:
            # Use word boundaries to avoid partial matches
            pattern = rf"\b{re.escape(keyword)}\b"
            result = re.sub(pattern, "[REDACTED]", result, flags=re.IGNORECASE)

        return result
