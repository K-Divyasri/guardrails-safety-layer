---
title: Guardrails Safety Layer
emoji: 🛡️
colorFrom: blue
colorTo: indigo
sdk: streamlit
app_file: app.py
pinned: false
---

# Guardrails Safety Layer — live demo

A support bot for the fictional Northwind Bank, wrapped in input/output guardrails:
prompt-injection defence, PII redaction, topic scoping, content moderation, and
output-schema validation.

Type a message in the "Try a message" tab and watch which guards fire. The
"Red-team report" tab runs 19 documented attacks live and shows the pass rate
(currently 19/19).

Runs fully offline by default — no API key needed. Tick "use LLM classifier" in
the sidebar only if this Space has a `GEMINI_API_KEY` secret set.

Source: see the project this Space was built from for the full learning path
(notebooks, labs, and the tested `safeguard` package).
