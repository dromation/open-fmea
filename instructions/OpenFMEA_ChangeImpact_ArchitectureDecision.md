# Open-FMEA Architecture Decision — Change Impact (Mockup 13)

Status: **Decision, 2026-09-05** — proposing a firm, narrow default for the user to approve or correct, per this project's standing house rule (no feature is built ahead of its own review's approval, and the approved scope is the narrowest one stated, not the full ambition of the mockup). This is a decision document, not an implementation instruction — no code changes yet.

Author: Claude, acting as Open-FMEA Technical Architect.

## 1. What's genuinely new here

I checked the actual domain/model code before writing this, not just the mockup. No `Change`-type entity exists anywhere in `domain/fmea_domain/entities.py` or `django_app/fmea_app/models.py`. The closest existing things are `FMEARevision`/`FMEALifecycle` (`fmea_app/models.py`), which track revisions of one FMEA *document's own lifecycle state* (draft → reviewed → approved, etc.) — a different relationship shape from an external design/supplier/regulatory/process/material change that ripples outward and affects `FailureMode`s across potentially many FMEAs. Building `Change` needs one new entity, one new relationship, and a small amount of new GUI — it does not need a new domain rule, a new taxonomy scheme, or any change to `RiskEvaluation`/`FailureMode`/`FMEARevision`.

## 2. Proposed `Change` model

A new `Change(StableModel)` in `fmea_app/models.py`, following this project's own most recent precedent for a new GUI-facing entity that doesn't need cross-database/OFEF interchange semantics yet: `FMEAProject.status`/`ProjectMembership.role` (Phase 2a) are plain Django `choices` tuples defined directly on the model, with no mirrored `fmea_domain` enum and no `to_domain()` obligation for those fields. `Change` follows that same pattern — a Django-app-layer model, not mirrored into the portable domain package for this increment (no requirement anywhere in this project currently calls for `Change` to round-trip through OFEF export/import; that can be added later, non-breaking, if a real need appears).

Fields:

- `title` — `CharField(max_length=255)`.
- `change_type` — `CharField` with `choices`: Design / Supplier / Regulatory / Process / Material. A plain Django-choices enum, not a `CauseCategoryScheme`-style configurable taxonomy — this is a closed, structural classification of *where a change originates*, not an organization-specific vocabulary an org would legitimately redefine (rule 6's own distinction).
- `source` — `CharField(max_length=255, blank=True)`, free text (e.g. "Customer Request," "Internal Design Review") — the mockup shows this as descriptive text, not a controlled list; no existing catalog fits it, and inventing one is out of scope.
- `reason` — `TextField(blank=True)`, free text.
- `description` — `TextField(blank=True)`.
- `impact_level` — `CharField` with `choices`: Critical / High / Medium / Low. Same closed-enum reasoning as `change_type`.
- `status` — `CharField` with `choices`: Under Analysis / In Progress / Open / Closed, default `"under_analysis"`. Closed, structural, free-choice (no enforced transitions) — matching this project's own explicit precedent for `ActionStatus` and `CauseInfluenceStatus`: a plain Python/Django enum is correct for a closed vocabulary that isn't organization-configurable (rule 6), and this project only builds enforced transition rules when a specific reason calls for it (`CauseInfluence` has one because of its connection-logic spec; `RecommendedAction.status` and `FMEAProject.status` do not, and nothing about `Change` calls for one either).
- `owner` — `ForeignKey(ResponsibleRole, null=True, blank=True, on_delete=SET_NULL, related_name="changes")`. **Not** a new person/user field. This mirrors the exact recommendation already made and standing for "Owner" in `OpenFMEA_EvidenceTests_ArchitectureReview.md` Section 4, Decision 2: "reuse the existing `ResponsibleRole` catalog … rather than inventing a second, redundant 'just a name' field — keeps one owner/role concept in the app instead of two, and upgrades cleanly to a real per-person account later without a rename." `django.contrib.auth` remains essentially unused for domain ownership anywhere in this app; `Change.owner` should not be the first place that changes.
- `target_date` — `DateField(null=True, blank=True)`. `created_at` is not a new field — `StableModel` already gives every entity an auto-set `created_at`/`updated_at`; no separate "Date" field is needed beyond that plus the explicit `target_date`.

## 3. Linkage: `Change` ↔ `FailureMode`

`Change.affected_failure_modes = models.ManyToManyField(FailureMode, related_name="affecting_changes", blank=True)`.

A plain M2M field, not a new join-model with extra per-link fields (no "why this failure mode is affected," no per-link impact sub-rating, no per-link status). The mockup's "linked to counts of affected DFMEA/PFMEA items" is satisfiable entirely by `change.affected_failure_modes.count()` plus grouping by `failure_mode.fmea.fmea_type` (`"design"` reads as DFMEA, `"process"` as PFMEA — both real, existing `FMEA.fmea_type` values) computed at render time — no new field or aggregation table needed. A richer per-link relationship (e.g. "this change affects this failure mode's Severity specifically") is a real, separate modeling question if it's ever wanted — not assumed into this first increment.

Widget: a plain multi-select (`ModelMultipleChoiceField`'s default `<select multiple>` rendering) on the edit form — not a search-as-you-type/AJAX picker. This app has no AJAX anywhere (standard house convention); a plain multi-select is consistent with every other relationship-editing widget in the app today (e.g. `ProcessCharacteristicForm`'s FK selects) and is an acceptable increment even as the `FailureMode` count grows — if it becomes unwieldy later, that's a usability refinement, not a blocker to shipping this narrow first version.

## 4. Scope for the first increment

1. `Change` model + migration.
2. `Change Log` list page: table of all changes (Title / Type / Impact Level / Status / Owner / Date), filterable by type/impact-level/status via the standard server-side GET-form `<select>` pattern this app uses everywhere else (no AJAX).
3. A create/edit form (one `ChangeForm`, reused for both).
4. A detail page: one `Change`'s fields, plus its linked `FailureMode`s as a **read-only** list (name, parent FMEA, FMEA type) — added/removed only via the edit form's M2M widget, not inline on the detail page.
5. One new sidebar link, "Change Impact," in the pattern already used by every shipped GUI slice (Risk Matrix, Engineering Context, Process Characteristics) — exactly one line added, no new nav group invented if an existing suitable group is already present at implementation time; otherwise placed alongside the other top-level entries.

## 5. Explicitly out of scope for this increment

- **Impact Matrix tab** — a cross-tabulation of changes against affected items/severity is a real, separate display/aggregation design, not a byproduct of the model above.
- **Affected FMEA Items tab as its own tab** — the read-only linked-`FailureMode`s list on the detail page (Section 4.4) covers the same underlying data without inventing a second page/tab shape; a distinct tab with its own filtering/sorting is a later refinement, not required to make the core entity useful.
- **Action Plan tab** — this needs a `Change` → `RecommendedAction` linkage, which is a separate modeling decision (does an action attach to the `Change` directly, or only indirectly via an affected `FailureMode`'s existing actions?) — not decided here, not assumed.
- **Change History / audit trail** — no field-level change-history/versioning model exists anywhere in this app today (the same gap already flagged in the Risk Matrix mockup's "History (Last 3 Changes)" panel and the Evidence & Tests review's "Created/Last Updated/by <name>" fields) — out of scope here for the same reason it's out of scope everywhere else, not a `Change`-specific omission.
- **Any donut/line chart, any "Top Affected Areas" analytics** — `Chart.js` (the charting-library decision) covers line/bar/donut in general, but adopting the library does not by itself authorize a specific chart on a specific page; charting for this page is deferred to a later increment once the core entity exists and has real data to chart.
- **Any approval/review workflow for `Change` records.** Nothing in this project's standing rules (rule 4's human-review gate applies to ingestion/AI/bulk-import output; rule 7's approval-workflow requirement is specific to Control Plans) requires one for `Change` specifically, and none is invented here. A `Change` is created/edited the same way every other plain-CRUD entity in this app is (`ProcessCharacteristic`, `FMEAProject`, `RecommendedAction`) — an ordinary human-driven form, unguarded, per the same DNA correction already recorded for Mockup 21.
- **Any AI-assisted impact analysis** ("which failure modes does this change likely affect") — a real, unspecced AI capability with no prompt design, no confidence-scoring design, and no human-review-gate design (same category already flagged and declined for Mockup 9's "Auto Link" and Mockup 15's "Similar Failure Modes (AI)"). Not proposed here.

## 6. What this decision does not propose

No change to `FMEARevision`/`FMEALifecycle`, `RiskEvaluation`, `FailureMode`'s existing fields, or any other model beyond adding the new `Change` model and its M2M. No new domain entity in `fmea_domain/` (Section 2) — this stays a Django-app-layer model, consistent with `FMEAProject`/`ProjectMembership`'s own precedent for GUI-facing fields that don't yet need portable-domain/OFEF interchange. No file/attachment storage (not shown in the narrowed mockup scope above, and this app has no file-storage subsystem anywhere yet — a foundational gap, not something to solve incidentally here). No per-project scoping mechanism.

## Recommendation

**Recommendation: READY FOR IMPLEMENTATION.**
