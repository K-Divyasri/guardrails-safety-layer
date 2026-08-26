"""Tests for the output-schema guard."""

from __future__ import annotations

from safeguard.schema import validate_output


def test_valid_output() -> None:
    result = validate_output('{"answer": "hi", "category": "card", "escalate": false}')
    assert result.valid and result.data["category"] == "card"


def test_not_json() -> None:
    result = validate_output("this is not json at all")
    assert not result.valid and "json" in result.error.lower()


def test_bad_enum_value() -> None:
    result = validate_output('{"answer": "hi", "category": "weather", "escalate": false}')
    assert not result.valid and "category" in result.error


def test_extra_field_rejected() -> None:
    result = validate_output('{"answer": "hi", "category": "card", "escalate": false, "x": 1}')
    assert not result.valid


def test_missing_field_rejected() -> None:
    result = validate_output('{"answer": "hi", "category": "card"}')
    assert not result.valid
