from __future__ import annotations

import logging
import unittest

from seo_os.security import REDACTED, SafeFormatter, SafeLogFilter, redact_mapping, redact_text, scan_text


class SecurityTests(unittest.TestCase):
    def test_mapping_redacts_secret_values(self) -> None:
        result = redact_mapping({"api_key": "sensitive-value", "property_id": "123"})  # synthetic-secret-fixture
        self.assertEqual(REDACTED, result["api_key"])
        self.assertEqual("123", result["property_id"])

    def test_text_redacts_bearer_and_email(self) -> None:
        result = redact_text("Bearer abcdefghijklmnopqrstuvwxyz user@example.com")  # synthetic-secret-fixture
        self.assertNotIn("abcdefghijklmnopqrstuvwxyz", result)
        self.assertNotIn("user@example.com", result)

    def test_scanner_finds_high_confidence_secret(self) -> None:
        findings = scan_text("client_secret='abcdefghijklmnop'", "fixture.txt")  # synthetic-secret-fixture
        self.assertEqual(1, len(findings))
        self.assertEqual("credential-assignment", findings[0].rule_id)

    def test_empty_environment_example_is_not_secret(self) -> None:
        self.assertEqual((), scan_text("AHREFS_API_KEY=\n"))

    def test_safe_formatter_redacts_after_formatting(self) -> None:
        record = logging.LogRecord(
            "seo_os", logging.INFO, __file__, 1, "Bearer abcdefghijklmnopqrstuvwxyz", (), None  # synthetic-secret-fixture
        )
        output = SafeFormatter("%(message)s").format(record)
        self.assertNotIn("abcdefghijklmnopqrstuvwxyz", output)

    def test_log_filter_preserves_argument_formatting(self) -> None:
        record = logging.LogRecord(
            "seo_os", logging.INFO, __file__, 1, "Values: %s %s", ("safe", "user@example.com"), None
        )
        SafeLogFilter().filter(record)
        output = SafeFormatter("%(message)s").format(record)
        self.assertIn("Values: safe", output)
        self.assertNotIn("user@example.com", output)


if __name__ == "__main__":
    unittest.main()
