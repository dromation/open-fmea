# Claude Review — Evidence & Tests / Validation Trajectory (Slice F) Implementation

**Author:** Claude (this session) · **Date:** 2026-09-05
**Instruction:** `Codex_Instruction_EvidenceTests_SliceF.md`

## 1. What was built

New `ValidationTest` entity, following the field table in Section 0 of the instruction exactly: `name`, `failure_mode` (required FK to `FailureMode`, CASCADE), `recommended_action` (nullable FK to `RecommendedAction`, SET_NULL), `test_type`/`result_status`/`priority`/`lifecycle_gate`/`status` (five closed-vocabulary `CharField`+`choices` fields), `method`/`nominal_target` (free text), `objective`/`acceptance_criteria` (free text, `Textarea`), `planned_date`/`executed_date` (two separate nullable dates), `owner` (nullable FK to `ResponsibleRole`, the placeholder pattern `RecommendedAction.responsible_role` already uses). One additive migration (`0008_validationtest.py`).

Matching framework-free domain layer, per the instruction's explicit requirement that every model in `models.py` has a `DomainX`/`to_domain()` pair: added `ValidationTest(NamedEntity)` plus five new enums (`TestType`, `ValidationResultStatus`, `Priority`, `LifecycleGate`, `ValidationTestStatus`) to `domain/fmea_domain/entities.py`, exported from `fmea_domain/__init__.py`. Checked first for a reusable `Priority`-shaped enum already in `fmea_domain` (none existed) before adding one, per the instruction's own instruction to check.

Three new pages: `/validation-tests/` (table with all ten columns from Section 1.2 — FailureMode linking to `fmea:fmea_detail`, Test Type, Method, Result Status badge, Planned/Executed Date, Priority, Owner, Status badge, Lifecycle Gate — plus GET-form `<select>` filters for `test_type`/`status`/`lifecycle_gate`, each defaulting to "All"), `/validation-tests/new/` (`ValidationTestForm`, all fields, `recommended_action`/`owner` optional), `/validation-tests/<stable_id>/` (full detail, "linked to an action" / "Not linked to an action" display mirroring `action_detail.html`'s existing pattern for its own optional links). New sidebar group `VALIDATION & CHANGE` with exactly one link, "Evidence & Tests" — `_sidebar.html`'s diff is exactly that one group/one link, confirmed by the required flip in `tests/test_gui_navigation_scope.py` (removed `"Evidence & Tests"`/`"VALIDATION & CHANGE"` from the unbuilt-label tuple, added positive assertions for both, kept `"Validation Trajectory"`/`"Change Impact"` in the unbuilt list since neither is built by this slice).

## 2. One minor grounding correction

The instruction says to reuse "the existing `_status_badge.html` component" for the Result Status column. No such file exists anywhere in this codebase — status badges are rendered inline everywhere they appear (`action_detail.html`, `fmea_detail.html`, `cause_influence_detail.html`, etc.) via `<span class="status status-{{ value }}">{{ get_X_display }}</span>`, with no shared include template. Used that actual, real, established pattern instead for both `result_status` and `status` badges on the new pages — a trivial correction, not a scope question, so it didn't warrant stopping.

## 3. Verification of the explicit "leave `Evidence`/`EffectivenessVerification` alone" requirement

Grepped `git diff` for both class bodies after finishing: zero changed lines in either `Evidence` or `EffectivenessVerification`'s class definitions (only context lines from the diff hunk boundary, confirmed by reading the diff directly, not just running a test). The new migration (`0008_validationtest.py`) contains exactly one operation, `CreateModel` for `ValidationTest` — no operation names `evidence` or `effectivenessverification`. Added a regression test (`test_evidence_and_effectiveness_verification_are_untouched`) that creates one of each via the ORM and confirms both still work exactly as before.

## 4. Test coverage

New `tests/test_validation_tests.py`, 7 tests: list-page column correctness and FMEA-detail linking; create-view persists every field including a set `recommended_action`; create-view with `recommended_action` omitted stores null; detail-page shows the action link when set and the "Not linked to an action" message (with no action link rendered) when unset; the three GET filters narrow the list individually and in combination (rows distinguished by their `method` text, since `ValidationTest.name` is not one of the ten spec'd list columns); neither page contains a file-upload marker, `<canvas`, or "Test Plan" text; the `Evidence`/`EffectivenessVerification` regression check.

## 5. Verification

Fresh venv, live shell, both repos:

| Check | `open_fmea` | `open_fmea_training_set` |
|---|---|---|
| `manage.py check` | clean | clean |
| `makemigrations --check --dry-run` | "No changes detected" (after generating `0008`) | "No changes detected" |
| `test_validation_tests.py` + `test_gui_navigation_scope.py` (isolated) | 10/10 | — |
| Full suite | **160/160** | **160/160** |

160 = the prior 153 (Slices A–E, M) plus the 7 new tests here — arithmetic checked. Grepped every changed/new file for every excluded term (`type="file"`, `<canvas`, `Test Plan`/`TestPlan`/`test_plan`) — zero matches.

Diff surface via `git status --short` matches the instruction's allowed-file list exactly: `entities.py`/`__init__.py` (domain layer), `models.py`, `forms.py`, `views.py`, `urls.py`, `_sidebar.html` (all modified/further modified), migration `0008` (new), three new templates, `test_validation_tests.py` (new), `test_gui_navigation_scope.py`'s one intentional flip.

Mirrored to `open_fmea_training_set` and byte-diffed (`diff -q`): all 13 changed/new files identical. Full suite re-run there independently: 160/160.

## 6. Scope discipline

No file/attachment field or upload UI anywhere. No real per-person Owner — `ResponsibleRole` FK only. No dashboard/stat cards, no Chart.js, no `<canvas>`. No `TestPlan` entity or FK. No enforced status-transition logic on `ValidationTest.status` (a plain free-choice dropdown, matching `ActionStatus`'s own no-enforced-transitions precedent). No AI involvement.

## 7. Still open

- `.git/index.lock` still needs a manual delete in `open_fmea`. Nothing committed, per "build first, commit later."
- Remaining slices from the 2026-09-05 batch: G (FMEA Elements standalone pages), H (Process Control Characteristics), I (Change Impact), J (Risk Trajectory & Propagation), K (Consolidated Home), L (Characteristics Flow) — not yet read in full or implemented.
