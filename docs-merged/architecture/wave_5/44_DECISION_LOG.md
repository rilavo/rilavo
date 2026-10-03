# Rilavo Protocol — Decision Log (P-44)

**Tree:** Protocol
**Wave:** 5 — Governance & Institutionalization
**Status:** Decided (practice and format below), ongoing
**Depends on:** Every document in both trees
**Closes when:** Never — it is the record itself, not a document that reaches a finished state.

## What this document specifies

Not a list of decisions — those already live inside every individual document, each one marked **Decision**, **Open**, **Deferred**, or **Rejected**. This document specifies the *format* a compiled, chronological log entry takes once one is assembled, and the discipline for keeping it current.

## Entry format

| Field | Purpose |
|---|---|
| Decision ID | Traceable to a specific document (e.g., P-06, E-15) |
| Date | When the decision was recorded |
| Status | Decided / Open / Deferred / Rejected |
| Decision | The actual call, stated in one line |
| Rationale | Why, in brief — the source document carries the full reasoning |
| What would change it | The falsifiability condition already required in every document across this project |

## Why this matters for AI-assisted development specifically

Every document in this project already ends with a "what would change this decision" section — that discipline exists precisely so an AI coding agent, or a new human contributor, has a single, current source of truth to check a proposed change against, rather than needing to infer intent from scattered prose or, worse, from a previous agent's possibly-outdated summary of it (Question Bank, solo-founder and AI-agent governance sections). This log is the compiled index into that discipline, not a replacement for it.

## What already exists, and what doesn't yet

Every **Decision** and **Rejected** line across all documents generated so far already constitutes this log's raw content. What doesn't yet exist is the single compiled, chronological file pulling them together — a genuinely separate undertaking, since it requires reviewing every document produced across every wave and extracting its decision points in date order, not something this format specification does on its own.

## What would change this decision

Nothing about the format. The compiled log itself should be regenerated whenever a source document's status changes — Open becoming Decided, or a Decided item reopening — so the log never drifts out of sync with the documents it's supposed to index.
