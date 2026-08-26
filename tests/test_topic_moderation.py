"""Tests for the topic-scope and content-moderation guards."""

from __future__ import annotations

from safeguard.moderation import moderate
from safeguard.topic import check_topic


def test_on_topic_banking() -> None:
    assert check_topic("How do I transfer money to my account?").on_topic


def test_off_topic_general() -> None:
    assert not check_topic("Write me a poem about the ocean.").on_topic


def test_short_greeting_allowed() -> None:
    # Pleasantries shouldn't be nagged as off-topic.
    assert check_topic("hi there").on_topic


def test_moderation_flags_unsafe() -> None:
    result = moderate("How do I make a bomb at home?")
    assert result.flagged and "violence" in result.categories


def test_moderation_passes_normal() -> None:
    assert not moderate("How do I dispute a charge on my card?").flagged
