# Claude Review — Functions + Actions GUI Slice: Implementation, Scope-Pull Correction, Training-Set Mirror

Status: independent review/record, written by the implementing session itself (not a separate reviewer) — kept per the project's standing per-slice documentation discipline (see e.g. `Claude_Review_RiskMatrix_Implementation_TrainingSetMirror.md`).

Date: 2026-09-03

Scope: `Codex_Instruction_FunctionsActionsEvidence_GUIGap_Slice.md`, as narrowed the same day.

---

## 1. What was built

`Function` and `RecommendedAction` ("Actions") — both pre-existing Phase B Django models with zero prior GUI surface — are now reachable and editable from the FMEA worksheet page (`fmea_detail.html`) and a new `action_detail.html` sub-page, per the Tier B gap identified in `OpenFMEA_DNA_CoreReference.md` Section 10 (Mockups 5–8 audit).

- `FunctionForm` (`forms.py`): `name`, `description`, plus `product`/`operation` as FMEA-scoped optional fields with a `clean()` guard requiring at least one.
- `FailureModeForm`: gained an optional `function` field, scoped to the current FMEA via `Q(product__fmea=fmea) | Q(operation__process__fmea=fmea)`.
- `RecommendedActionForm`: `name`, `description`, `responsible_role`, `status`, `due_date`.
- Views: `add_function`, `add_action_to_cause`, `add_action_to_failure_mode` (each explicitly sets exactly one of `failure_cause`/`failure_mode` and nulls the other), `action_detail`.
- URLs: 4 new paths, no nav/sidebar change (matches the "worksheet sub-section, not standalone nav page" pattern already established for Failure Modes/Effects/Causes/Controls — see the DNA doc's Mockup 5–11 "Useful structural clarification" note).
- Templates: a new "Functions" section and two new "Actions" sections (one for causes, one for failure-mode-level actions not tied to a cause) added to `fmea_detail.html`; new `action_detail.html`.
- Tests: `tests/test_functions_actions_gui.py`, 7 tests.

## 2. Deliberate deviation from the instruction's literal text — and why

The instruction specified `FunctionForm(name, description)` only, describing `Function` as "parented to the FMEA... mirrors the existing Process/Operation pattern." Direct inspection of `models.py` shows this is factually incorrect: `Function` has FKs only to `Product` (nullable) and `Operation` (nullable) — never to `FMEA`. Implementing the literal spec would create `Function` records with no path back to any FMEA, invisible on the very page the slice is meant to populate.

Fix: `product` and `operation` were added to `FunctionForm` as optional fields (both pre-existing model fields — no migration), scoped to the current FMEA via the `fmea=` constructor kwarg, with a `clean()` guard raising `ValidationError` if neither is set. This is the minimum change that makes the form actually produce FMEA-visible `Function` records, and is documented inline in `forms.py` as a deliberate correction, not a silent expansion of scope.

## 3. Scope-pull caught mid-implementation

The instruction originally covered Evidence and EffectivenessVerification GUI as well (per its pre-narrowing title and body). A first implementation pass built `EvidenceForm`/`EffectivenessVerificationForm`, `add_evidence`/`add_effectiveness_verification` views and URLs, and matching template sections and tests, against that version.

Before committing, a routine `git status --short` re-check surfaced a new file, `OpenFMEA_EvidenceTests_ArchitectureReview.md`, and a re-read of the instruction showed it had been narrowed the same day: Mockup 10 ("Evidence & Tests") revealed that "Evidence & Tests" is really a materially richer, not-yet-designed Test-Plan/`ValidationTest` entity (own status workflow, Test Type, Method, Acceptance Criteria, file attachments, a real Owner, direct `FailureMode` link) — not a thin wrapper around the existing `Evidence`/`EffectivenessVerification` models. The narrowed instruction's Acceptance Criteria #4 explicitly forbids any `Evidence`/`EffectivenessVerification` view, URL, template, or form appearing in the diff.

Correction applied before any commit:

- Removed `EvidenceForm`/`EffectivenessVerificationForm` from `forms.py`.
- Removed `add_evidence`/`add_effectiveness_verification` views, and the evidence/verification prefetch and context keys, from `views.py`'s `action_detail`.
- Removed the two corresponding URL patterns.
- Rewrote `action_detail.html` to show only the action's own fields (Status, Responsible, Due Date, Linked-to Cause/Failure Mode) — no Evidence or Effectiveness Verification sections.
- Deleted `tests/test_functions_actions_evidence_gui.py` and replaced it with `tests/test_functions_actions_gui.py` (the instruction's required filename), containing only the 7 still-in-scope tests.

Verified zero remaining trace with `git diff | grep -i "evidence\|effectiveness"` (empty) and `grep -il "evidence\|effectiveness"` across every changed/new code, template, and test file (empty) — confirmed again independently at commit time. `OpenFMEA_EvidenceTests_ArchitectureReview.md` itself (status: NOT YET READY, three open decisions — file attachments, Owner, `ValidationTest` vs. `EffectivenessVerification` relationship) was committed as a reference document only, not acted on.

## 4. Verification (re-run independently, not trusted from any status report)

- `manage.py check`: clean in both `open_fmea` and `open_fmea_training_set`.
- `manage.py makemigrations --check --dry-run`: "No changes detected" in both — confirms the `FunctionForm` deviation needed no migration, as claimed.
- Full test suite: **106/106 passing independently in both `open_fmea` and `open_fmea_training_set`** (72 + 34 dot-groups per `pytest -q`, exit code 0 in both; test collection counted to exactly 106 across all 26 test modules).
- Source parity: every changed/new file (`forms.py`, `urls.py`, `views.py`, `fmea_detail.html`, `action_detail.html`, `test_functions_actions_gui.py`, plus the three architecture docs) confirmed byte-identical between `open_fmea` and `open_fmea_training_set` via `diff -q`.

## 5. Cross-repository context reviewed (Open-EQMS)

The user connected `D:\Dromation\org\apps\open_eqms` this session as reference context. Two documents there are directly relevant to Open-FMEA and were read in full:

- `Claude_OpenFMEA_Architecture_and_Portability_Report.md` (2026-08-30) — the original grounding report that authorized the Django rebuild in the first place (same document referenced in this repo's own `architecture/README.md` as `OpenFMEA_Architecture_and_Portability_Report.md`, under "Foundational architecture"). Its Section 13 ("Open-EQMS Future Integration Map") and Section 2 findings confirm: **none of Open-EQMS's Runtime capabilities (Object Runtime, Event Engine, Transaction Engine, Query Engine, Security) are consumable by Open-FMEA today**, because no Python↔Rust integration mechanism exists yet, and the two components any real integration would need first (Security, Query Engine execution) are the least mature parts of Open-EQMS itself.
- `architecture/product/PRS-000-master-product-vision.md` Section 21, "OPEN-FMEA" — the north-star statement: Open-FMEA "must not become an isolated spreadsheet clone," should eventually operate over shared Open-EQMS objects (Product, Function, Requirement, Characteristic, Failure Mode, Effect, Cause, Controls, Action, Evidence, Measurement, Complaint, 8D, CAPA, Audit Finding, Lesson Learned), and describes the same closed-loop (Real Problem → Analysis → Failure Mode → ... → Recurrence Monitoring) already quoted in Open-FMEA's own architecture material. Explicitly **not implementation authorization** by itself (Open-EQMS's own `AGENTS.md` rule 13, restated in the portability report's header).

**Conclusion for current work: nothing changes.** This confirms, from the Open-EQMS side, that every "Open-EQMS integration" element already flagged and deliberately deferred in Open-FMEA's own mockup audits (the System/Product/Process context switcher, the "Open-EQMS Maintenance" node in the Characteristics Flow mockup, any cross-system badge) was correctly deferred — there is no integration path to build against yet, and building one now would violate Open-EQMS's own governance (`AGENTS.md` rules 1, 15, 19, 20) as much as it would violate Open-FMEA's own rule against building ahead of an approved review. Open-FMEA's domain model (entity list, `stable_id`/`revision` shape, portable-domain package split) already matches the object list and identity strategy the portability report proposed and PRS-000 Section 21 ratifies as north star — this is a favorable alignment finding, not a new obligation.

## 6. Training-set mirror and packaging

All changed/new files mirrored to `open_fmea_training_set` (Section 4 above). No static assets or packaging-relevant files changed in this slice (GUI-only, reusing the existing theme/design system), so no training-EXE rebuild is strictly required by this change alone. The rebuild remains the standing environment-blocked manual step (PyInstaller cannot cross-compile a Windows EXE from this Linux bridge shell):

```
cd D:\Dromation\org\apps\open_fmea_training_set
powershell -File packaging\build_exe.ps1
```

## 7. Operational note — device bridge

This review was written, and this slice's architecture-doc updates were finished, during a period when the local FUSE bridge (`device_bash`'s `~/mnt/open_fmea` view) was unavailable for part of the session (all three connected folders — `open_fmea`, `open_fmea_training_set`, and the newly-connected `open_eqms` — failed to mount in the bridge shell, while `device_list_dir`/`device_stage_files`/`device_commit_files` continued to work against the same folders by their device paths throughout). This is a new instance of the operational-risk category already tracked in `OpenFMEA_DNA_CoreReference.md` Section 7 (alongside the recurring `.git/index.lock` issue) — both are FUSE-bridge reliability symptoms, not root-caused by the user, and both have so far always self-resolved without data loss.
