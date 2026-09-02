# Cause Influence and Ishikawa Review

This document records the implemented boundaries for the first Ishikawa backend slice.

## Entities

`CauseCategoryScheme` is a configurable taxonomy container. The default seeded scheme is `cause-category-scheme:ishikawa-5me-default`.

`CauseCategory` stores the scheme terms. The default seed creates `Man`, `Machine`, `Material`, `Method`, `Measurement`, and `Environment`.

`CauseInfluence` is a governed cause edge. In this slice, the allowed source and target types are intentionally narrow:

- Source: `FailureCause` or `FailureMechanism`
- Target: `FailureMode` or `FailureCause`

The category belongs to the influence edge, not to the source object. The same `FailureCause` or `FailureMechanism` can participate in different causal paths with different categories.

## Status Rules

The closed status vocabulary is:

- `suspected`
- `possible`
- `correlated`
- `experimentally_supported`
- `confirmed_root_cause`
- `rejected`

Progression is forward-only: `suspected -> possible -> correlated -> experimentally_supported -> confirmed_root_cause`.

`rejected` is terminal and requires a `review_note`. `confirmed_root_cause` is terminal and requires a `review_note`.

Skipping intermediate statuses requires a `review_note`. Moving backward is not allowed.

An influence cannot reach `confirmed_root_cause` while targeting a `FailureMode`. Confirmation from a `FailureMode` target must atomically retarget the influence to a real `FailureCause` belonging to that same failure mode.

`experimentally_supported` requires either supporting `evidence_ids` or a `review_note`.

## GUI

The implemented GUI is list-form only:

- `/cause-influences/` lists and filters cause influences.
- `/cause-influences/new/` creates a new suspected influence.
- `/cause-influences/<stable_id>/` reviews one influence and applies explicit status transitions.
- `/failure-modes/<stable_id>/ishikawa-board/` groups cause influences by category for one failure mode.

The visual fishbone diagram is deliberately not part of this slice.

## AI Boundary

AI classification for Ishikawa categories is not wired in this slice. When added later, AI may suggest a `CauseCategory`, but it must not create a `CauseInfluence`, change status, confirm root cause, reject a candidate, or bypass human review.

## Man Category Boundary

`Man` means human work-system factors: training, staffing, instructions, handoffs, ergonomics, and similar process factors. It must not store subjective personal, health, demographic, blame-oriented, or disciplinary data.
