"""Deterministic no-network regression tests for the biweekly reviewer."""
from __future__ import annotations
import datetime as dt
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import biweekly_review as r


class ReviewTests(unittest.TestCase):
    def test_calendar_anchor(self):
        self.assertFalse(r.next_due(dt.date(2026, 10, 14)))
        self.assertTrue(r.next_due(dt.date(2026, 10, 21)))
        self.assertTrue(r.next_due(dt.date(2026, 10, 28)))
        self.assertTrue(r.next_due(dt.date(2026, 11, 4)))

    def test_strict_filter_conditions(self):
        sample = """||ads.example^\n||sub.ads.example^$third-party\n||safe.example^$domain=site.com\n||path.example/ad^\n@@||bank.example^\n||a.example^\n||*.wild.example^\n||dns.example^$document\n"""
        self.assertEqual(r.parse_domains(sample), {"ads.example", "a.example"})
        self.assertEqual(r.parse_exceptions(sample), {"bank.example"})

    def test_suffix_exact_and_parent_conflicts(self):
        self.assertTrue(r.is_covered("ads.example.com", ("DOMAIN-SUFFIX", "example.com")))
        self.assertFalse(r.is_covered("notexample.com", ("DOMAIN-SUFFIX", "example.com")))
        self.assertFalse(r.is_covered("sub.example.com", ("DOMAIN", "example.com")))
        self.assertTrue(r.is_guard_conflict("example.com", ("DOMAIN", "api.example.com")))
        self.assertTrue(r.is_guard_conflict("api.example.com", ("DOMAIN-SUFFIX", "example.com")))
        self.assertFalse(r.is_guard_conflict("ad.example", ("DOMAIN", "elsewhere.example")))

    def test_static_and_awa(self):
        module = "DOMAIN-SUFFIX,guard.com,DIRECT\nDOMAIN,ads.example.com,REJECT\nRULE-SET,https://x,REJECT\n"
        self.assertEqual(r.parse_static(module, "DIRECT"), {("DOMAIN-SUFFIX", "guard.com")})
        self.assertEqual(r.parse_static(module, "REJECT"), {("DOMAIN", "ads.example.com")})
        self.assertEqual(r.parse_awa("DOMAIN-SUFFIX,example.org\nDOMAIN,cdn.example.net\n# comment\n"), {("DOMAIN-SUFFIX", "example.org"), ("DOMAIN", "cdn.example.net")})

    def test_exceptions(self):
        self.assertEqual(r.exception_conflicts("example.com", {"app.example.com", "elsewhere.com"}), ["app.example.com"])
        self.assertEqual(r.exception_conflicts("child.example.com", {"example.com"}), ["example.com"])

    def test_no_empty_and_invalid_domains(self):
        self.assertFalse(r.valid_domain("singlelabel"))
        self.assertFalse(r.valid_domain("example..com"))
        self.assertFalse(r.valid_domain("-bad.example"))
        self.assertFalse(r.valid_domain("bad-.example"))


if __name__ == "__main__":
    unittest.main()
