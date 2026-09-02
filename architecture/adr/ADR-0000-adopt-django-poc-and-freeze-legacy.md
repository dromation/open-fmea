# ADR-0000: Adopt Django PoC and Freeze Legacy Prototype

Status: Approved

Date: 2026-08-30

## Context

The architecture and portability report identifies Open-FMEA as a recognized Open-EQMS product direction while also confirming that the Rust Open-EQMS Runtime is not yet consumable from Python/Django. The current Open-FMEA repository contains a Tkinter/SQLite prototype on `beta-v01` and no Django implementation.

The Project Manager approved starting implementation after the Section 19 decisions in `OpenFMEA_Architecture_and_Portability_Report.md`.

## Decision

Open-FMEA Phase B will proceed in the existing `dromation/open-fmea` repository.

The implementation stack is Django with optional Django REST Framework, SQLite for local PoC execution, and PostgreSQL-compatible model choices where practical.

The new implementation starts from framework-free domain code in `domain/fmea_domain/`. Django models and views must remain persistence and delivery adapters around that domain model.

The current Tkinter/SQLite prototype is frozen under `legacy/tkinter-prototype/`. It remains a reference and candidate seed-data source, not the active implementation for new product features.

The initial evaluation-method scope is classic RPN plus a configurable Action Priority calculator variant for PoC use.

Legacy CSV/SQLite content is preserved for a later explicit import milestone rather than silently loaded as approved production seed content.

## Consequences

New feature work should target the Django/domain implementation.

The PoC must not claim integration with Open-EQMS Runtime components until a ratified cross-language integration contract exists.

Portable identity uses opaque `stable_id` values and monotonic per-entity revisions. Django primary keys are internal persistence details and must not appear in Open-FMEA Exchange Format documents.
