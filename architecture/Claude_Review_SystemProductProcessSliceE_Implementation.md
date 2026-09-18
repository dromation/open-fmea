# Claude Review — System / Product / Process (Slice E) Implementation

**Author:** Claude (this session) · **Date:** 2026-09-05
**Instruction:** `Codex_Instruction_SystemProductProcess_SliceE.md` (from the new `instructions/` batch, "make them all ready for implementation" round)

## 1. What was built

New `System` model (`django_app/fmea_app/models.py`), extending `StableModel`: `name`, `description`, `code` (matching `Process.process_code`'s exact `CharField(max_length=128, blank=True)` shape), self-referential nullable `parent` FK (`related_name="children"`, `on_delete=SET_NULL`), `status` (`active`/`inactive`, default `active`). One additive migration (`0006_system_process_system_product_system.py`) also adds nullable `system` FKs to `Product` (`related_name="products"`) and `Process` (`related_name="processes"`) — confirmed non-colliding with `FMEA`'s own `related_name="products"`/`"processes"` since those reverse accessors live on `FMEA`, not `System`.

New pages: `/systems/` (flat list, sorted `parent__name, name`, columns Name/Code/Status/Parent/Product count/Process count, both counts computed at query time via `annotate(Count(..., distinct=True))`), `/systems/<stable_id>/` (own fields + linked Products/Processes/child Systems), `/systems/new/` and `/systems/<stable_id>/edit/` (shared `SystemForm`/`system_form.html`). One new sidebar link, "System / Product / Process", appended under the existing `CONTEXT` group (after "Engineering Context") — the group header and its two prior links are untouched.

`SystemForm`'s `parent` queryset excludes the instance being edited (full queryset offered on create), which blocks the one-hop self-parent cycle per Decision 9 — verified both at the form level (`test_system_form_rejects_setting_itself_as_its_own_parent`) and via the queryset itself (`test_system_form_parent_queryset_excludes_self_but_offers_others_on_create`).

## 2. Two grounding findings from real code, not assumed

**Finding 1 — Decision 10 / Exact Scope item 6 does not apply as written.** The instruction assumes an existing `ProductForm`/`ProcessForm` (or an inline form construction in `views.py`) that only needs one field added. Grepping the actual codebase before writing anything: zero matches for `ProductForm` or `ProcessForm` anywhere, zero `Product`/`Process` routes in `urls.py`, zero Product/Process view functions in `views.py`. There is no create/edit GUI for `Product` or `Process` anywhere in this app today — they are populated only via ORM/fixtures/seed data. Building new Product/Process CRUD views, forms, and templates was not authorized by this instruction (its allowed-file list has no `product_form.html`/`process_form.html` or new Product/Process routes), so I did not invent one. I built the part of Decision 10 that is real and unambiguous — the model-level `system` FK itself (Exact Scope item 2) — and adapted the corresponding required test to verify that FK persists via direct model creation/reload (`test_product_and_process_system_fk_persists`) rather than fabricating a test for a GUI that doesn't exist. This needs the concurrent architecture session's attention: either confirm no Product/Process GUI is wanted here (in which case Decision 10 should be retired) or write a follow-up instruction that actually authorizes building that GUI.

**Finding 2 — no "edit" view pattern exists anywhere in this app to copy.** The instruction's item 5 says to match "the pattern used by, e.g., the Process or Product create/edit views" for `system_edit` — but (per Finding 1) no Process/Product views exist at all, and a broader grep (`_edit\b|edit(request`) turns up zero "edit" views anywhere in the app for any entity — every existing entity is create-only (`new_X`/`add_X`) plus read. `system_edit` is therefore this app's first edit view. I built it as the obvious minimal extension of the existing create pattern: same `SystemForm`, same `system_form.html` template shared between create and edit (toggling label/action by whether `system` is `None` in the template context), same redirect-to-detail-on-success convention as `new_process_characteristic`. Flagging this as a judgment call, not a silent assumption.

## 3. One required, minimal fix to a pre-existing test (not in this slice's allowed-file list, but necessary)

Adding the new sidebar link means the shared `_sidebar.html` (rendered on every page via `base.html`) now legitimately contains the word "System". Slice C's `test_engineering_context.py::test_page_stays_within_narrowed_scope` asserted the *entire rendered response* — sidebar included — never contains "System", so it started failing the moment the new link existed, for the exact reason the original test's own comment already anticipated for a different case (the shared header's two theme-toggle `<svg>` icons had needed the same narrowing when Slice C was first written). Fixed by scoping that test's exclusion check to the page's own `<main class="content-shell">` region instead of the full response — the correct reading of what that test was always meant to assert (no System-hierarchy *content on the Engineering Context page itself*), not "the literal word System may never appear on any page including the global nav." No other assertion in that file changed.

## 4. Test coverage

New `tests/test_system_product_process.py`, 8 tests: list-page rows/counts/parent-linking correctness, detail-page linked Products/Processes/children with correct FMEA links, the self-parent rejection (both at the form-validation level and via the excluded queryset), full create→edit round-trip through the real views (POST, redirect-to-detail, persisted field values), the model-level Product/Process `system` FK persistence (Finding 1's substitute test), the regression check that Products/Processes with no System assigned still render correctly in Engineering Context / `fmea_detail` / `/systems/` itself, and the sidebar link assertion.

## 5. Verification

Fresh venv, live shell, both repos:

| Check | `open_fmea` | `open_fmea_training_set` |
|---|---|---|
| `manage.py check` | clean | clean |
| `makemigrations --check --dry-run` | "No changes detected" (after generating `0006`) | "No changes detected" |
| `test_system_product_process.py` (isolated) | 8/8 | — |
| `test_engineering_context.py` (isolated, post-fix) | 4/4 | — |
| Full suite | **140/140** | **140/140** |

140 = the prior 132 (Slices A/B/C/D, all previously independently confirmed) plus the 8 new tests here — arithmetic checked, not just asserted.

Diff surface confirmed via `git status --short`: on top of the already-uncommitted prior slices, Slice E's own footprint is exactly `models.py`, `views.py`, `urls.py`, `forms.py` (all further modified), migration `0006` (new), `system_list.html`/`system_detail.html`/`system_form.html` (new), `_sidebar.html` (further modified — confirmed by diff to be exactly one new `<a>` line under `CONTEXT`), `test_system_product_process.py` (new) — matching the instruction's allowed-file list — plus the one flagged, necessary fix to `test_engineering_context.py` (Section 3 above). Nothing else touched. Grepped the new templates/views/models/forms for every excluded term the instruction names (`ClassificationScheme`, `ClassificationTerm`, `<canvas`, `Control Plan`, `Reaction Plan`) — zero matches.

Mirrored to `open_fmea_training_set` and byte-diffed (`diff -q`, not size/mtime): all 11 changed/new files identical. Full suite re-run there independently: 140/140.

## 6. Scope discipline

No `FMEA.system` field anywhere. No backfill migration, no default/"Unassigned" System row, no change to any existing Product/Process row's data — confirmed by the migration content itself (purely additive: one `CreateModel`, two `AddField`) and by the regression test. No Type/Category/Importance/Monitoring-status field on `System`. No chart/graph/canvas rendering of the hierarchy — `system_list.html`/`system_detail.html` are plain tables. No `fmea_detail.html`, `engineering_context.html`, `process_flow.html`, `dfmea_worksheet.html`/`pfmea_worksheet.html`, or Risk Matrix template changes.

## 7. Still open

- `.git/index.lock` still needs a manual delete in `open_fmea`. Nothing committed — everything above sits uncommitted alongside the rest of today's work, per "build first, commit later."
- Finding 1 (Section 2) needs a decision from the concurrent architecture session before any future slice assumes a Product/Process GUI exists.
- Remaining slices from the 2026-09-05 "make them all ready for implementation" batch — F (Evidence & Tests), G (FMEA Elements standalone pages), H (Process Control Characteristics), I (Change Impact), J (Risk Trajectory & Propagation), K (Consolidated Home), L (Characteristics Flow), M (System Characteristics Base, depends on this slice) — not yet read in full or implemented.
