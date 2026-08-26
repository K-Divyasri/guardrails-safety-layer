"""Tests for PII detection and redaction."""

from __future__ import annotations

from safeguard.pii import find_pii, luhn_ok, redact


def test_finds_each_kind() -> None:
    text = "email a.b@x.com ssn 123-45-6789 card 4111 1111 1111 1111 phone 555-123-4567"
    kinds = {h.kind for h in find_pii(text)}
    assert kinds == {"email", "ssn", "credit_card", "phone"}


def test_redaction_replaces_and_keeps_spacing() -> None:
    red, hits = redact("Is my card 4111 1111 1111 1111 active?")
    assert red == "Is my card [CREDIT_CARD] active?"
    assert len(hits) == 1


def test_luhn_rejects_bad_number() -> None:
    assert luhn_ok("4111111111111111")       # valid Visa test number
    assert not luhn_ok("4111111111111112")   # last digit wrong -> fails checksum


def test_card_needs_luhn() -> None:
    # 16 digits that FAIL Luhn should not be redacted as a card.
    red, hits = redact("reference 1234 5678 9012 3456")
    assert not any(h.kind == "credit_card" for h in hits)


def test_clean_text_has_no_pii() -> None:
    assert find_pii("How do I reset my password?") == []


def test_no_overlapping_matches() -> None:
    # The digits of the SSN must not also be grabbed by the phone rule.
    hits = find_pii("my ssn is 123-45-6789")
    assert [h.kind for h in hits] == ["ssn"]
