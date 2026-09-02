# Product and Process Characteristics

This document records the implemented boundaries for the Characteristics-Linking-1 slice.

## ProductCharacteristic

`ProductCharacteristic` replaces the previous `Characteristic` entity name. Its behavior is otherwise unchanged: it may reference a `Requirement`, has `name`, `description`, and `is_special`, and participates in OFEF export/import by `stable_id`.

`primary_classification_id` exists as a nullable reserved field for future classification work. This slice does not populate it, validate it, or provide any classification-assignment UI.

Existing stable IDs are preserved during the rename. A stable ID containing the older generic word is still a stable identity and must not be rewritten casually.

## ProcessCharacteristic

`ProcessCharacteristic` is instance-level only. It belongs to one `Operation` through `operation_id`/`operation`; it is not a reusable library item.

Fields:

- `name`
- `description`
- `operation_id`
- `cause_category_id`
- `attributes`

`cause_category_id` may hold a default cause category, but this slice does not implement inheritance or reconciliation between a process characteristic category and a `CauseInfluence` category.

`attributes` is an open JSON object for values such as nominal, observed, limit, unit, or state-like information. It has no fixed schema in this slice.

## CauseInfluence Types

Allowed `CauseInfluence` source types:

- `FailureCause`
- `FailureMechanism`
- `ProcessCharacteristic`

Allowed `CauseInfluence` target types:

- `FailureMode`
- `FailureCause`
- `ProductCharacteristic`

`ProcessCharacteristic -> ProductCharacteristic` is a valid governed influence edge.

`confirmed_root_cause` still requires `target_type == "FailureCause"`. A `CauseInfluence` targeting `ProductCharacteristic` can progress only up to `experimentally_supported`; trying to confirm it as root cause is rejected.

## GUI

Implemented process-characteristic endpoints:

- `/process-characteristics/`
- `/process-characteristics/new/`
- `/process-characteristics/<stable_id>/`

The cause-influence creation screen can select `ProcessCharacteristic` as a source and `ProductCharacteristic` as a target.

## Explicit Non-Goals

This slice does not implement:

- product classification schemes or terms
- classification assignment UI
- process-characteristic reusable libraries
- category inheritance from `ProcessCharacteristic` to `CauseInfluence`
- visual fishbone diagram UI
- AI classification wiring
- coverage metrics
- lessons learned
- Control Plan hooks
