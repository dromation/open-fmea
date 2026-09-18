# Claude Review — Change Impact (Slice I) Implementation

**Author:** Claude (this session) · **Date:** 2026-09-05
**Instruction:** `Codex_Instruction_ChangeImpact_SliceI.md`

## 1. What was built

New `Change` model (`django_app/fmea_app/models.py`), placed after `ValidationTest` and before `Evidence` (both `FailureMode` and `ResponsibleRole` are already defined earlier in the file). Fields exactly per Section 1.1: `title`, `change_type`/`impact_level`/`status` (plain `choices` tuples matching `FMEAProject.PROJECT_STATUS_CHOICES`'s own precedent, not a `fmea_domain` enum or a `CauseCategoryScheme`-style configurable taxonomy — per Decision 2), `source`/`reason`/`description` (free text), `owner` (nullable FK to `ResponsibleRole`, `related_name="changes"`, `SET_NULL`), `target_date`, `affected_failure_modes` (plain `ManyToManyField(FailureMode, blank=True, related_name="affecting_changes")`, Django's default implicit through-table — no new join model). `status` defaults to `"under_analysis"`. `__str__` returns `self.title`. **No `to_domain()`, no `fmea_domain` entity or enum** — confirmed by grep that `domain/fmea_domain/entities.py` and `__init__.py` are completely untouched by this slice (matching `FMEAProject`/`ProjectMembership`'s own no-domain-pairing precedent, per Decision 1).

One additive migration. The instruction names it `0006_change.py`, but that number is long since taken (migrations 0006–0010 already exist from Slices E/M/F/G/H) — generated the real next sequential migration, `0011_change.py`, exactly one `CreateModel` operation, per the instruction's own explicit renumbering allowance ("renumber if a later migration already exists").

`ChangeForm(forms.ModelForm)` covers all ten fields including `affected_failure_modes` as the default `ModelMultipleChoiceField` multi-select (`forms.SelectMultiple` widget, no AJAX/search-as-you-type — per Decision 4), `owner`/`affected_failure_modes` both `required=False`, `owner` queryset ordered by name, `affected_failure_modes` queryset ordered by `fmea__name, name` for a stable, readable option list.

Four views following this app's established create/edit/detail/list conventions exactly: `change_list` (GET filters `change_type`/`impact_level`/`status`, same server-side-reload `.filter(...)` pattern as `process_characteristic_list`/`validation_test_list` — no AJAX anywhere), `new_change`/`edit_change` (sharing one `ChangeForm` and one `change_form.html`, toggling label/action/button text by whether `change` is `None` in context — the exact pattern `system_create`/`system_edit` established in Slice E, this app's only prior edit-view precedent), `change_detail` (renders every field read-only, plus a read-only linked-`FailureMode` table with an "Edit" button pointing to `edit_change` — no inline add/remove control on the detail page itself, per Section 1.4). DFMEA/PFMEA labeling is computed in the view (`_fmea_type_label` helper: `"DFMEA"` when `fmea_type == "design"`, `"PFMEA"` when `== "process"`, else `get_fmea_type_display()`) rather than in the template, matching this codebase's existing convention of view-level data shaping for anything beyond a single field lookup (e.g. `_latest_risk_result`, `_fmea_type_breakdown`).

Four routes added to `urls.py`: `/changes/`, `/changes/new/`, `/changes/<str:stable_id>/edit/`, `/changes/<str:stable_id>/`. Three new templates: `change_list.html` (filter form + `.table-shell`/`<table>`, Title/Type/Impact Level/Status/Owner/Target Date columns, title linking to detail), `change_form.html` (shared create/edit, hand-rolled field labels matching `system_form.html`/`validation_test_form.html`'s own convention), `change_detail.html` (Details panel + Identity panel matching `validation_test_detail.html`'s two-column layout, plus a separate "Affected Failure Modes (N)" section with the linked-FailureMode table).

## 2. Sidebar placement — grounding correction from a stale instruction assumption

Decision 6 / Section 1.5 says to add the "Change Impact" link to "the existing sidebar's primary nav group (the same group already containing 'FMEA Projects,' 'Process Characteristics,' 'Risk Matrix')." Reading the actual, current `_sidebar.html` in full before writing anything: no such group exists. These three items live in three separate groups today — "FMEA Projects" under `WORKSPACE`, "Process Characteristics" under `CONTEXT`, "Risk Matrix" under `RISK` — a structure that predates Slice A's nav restyle and that this instruction's text evidently wasn't updated to reflect.

Resolved this by cross-referencing Slice F's own instruction text, which explicitly describes the DNA reference's canonical group structure placing "Evidence & Tests" under a `VALIDATION & CHANGE` group "alongside 'Validation Trajectory' and 'Change Impact.'" That group already exists (built by Slice F) and already contains exactly the sibling item ("Evidence & Tests") this same canonical structure names alongside "Change Impact." Added the one new `<a class="nav-link">` line there instead of inventing a new group — this is also the only reading consistent with Decision 6's own explicit constraint, "Do not invent a new nav group for this slice." The sidebar diff is exactly one new line, confirmed via a marker-anchored programmatic replace (single-match assertion) rather than free-form editing, and by the required test (`test_sidebar_has_exactly_one_new_change_impact_link_and_other_unbuilt_labels_stay_absent`) counting exactly one occurrence of the string "Change Impact" in the rendered response.

## 3. Test coverage

New `tests/test_change_impact.py`, 7 tests, fixture spanning a `design`-type and a `process`-type FMEA throughout: create via `ChangeForm`/POST with a full field set including M2M selection, asserting redirect-to-detail and correct persistence of every field including `affected_failure_modes`; list-page column correctness across two fixture rows with different `change_type`/`impact_level`/`status`; the three GET filters narrowing the list individually and in combination; detail-page rendering of linked FailureModes spanning both FMEA types with correct "DFMEA"/"PFMEA" labels and correct parent-FMEA links; an edit that removes one linked FailureMode and adds another, confirming the detail page reflects exactly the new set afterward; a negative check across all four pages for `<canvas`/"Impact Matrix"/"Action Plan"/"Change History"; the sidebar assertion (exactly one "Change Impact" occurrence, correct link target, all previously-asserted-absent labels still absent).

`tests/test_gui_navigation_scope.py` — the required, intentional flip: `"Change Impact"` moved from the unbuilt-label negative tuple to a positive assertion (placed alongside the existing `"Evidence & Tests"` assertion under the `VALIDATION & CHANGE` checks). No other assertion in that file changed.

## 4. Verification

Fresh venv (persisted from prior slices this session), live shell, both repos:

| Check | `open_fmea` | `open_fmea_training_set` |
|---|---|---|
| `manage.py check` | clean | clean |
| `makemigrations --check --dry-run` | "No changes detected" (after generating `0011`) | "No changes detected" |
| `test_change_impact.py` + `test_gui_navigation_scope.py` (isolated) | 10/10 | — |
| Full suite | **186/186** | **186/186** |

186 = the prior 179 (Slices A–H, M) plus the 7 new tests here — arithmetic checked. Grepped `domain/fmea_domain/entities.py`/`__init__.py` for "Change" — zero matches (confirms Decision 1). Grepped the three new templates for every excluded term (`Impact Matrix`, `Action Plan`, `Change History`, `<canvas`, `donut`, `approve`/`approval workflow`) — zero matches.

Diff surface via `git status --short` matches Slice I's allowed-file list exactly: `models.py`, `forms.py`, `views.py`, `urls.py`, `_sidebar.html` (all further modified), migration `0011` (new, correctly renumbered from the instruction's stale `0006` placeholder), three new templates, `test_change_impact.py` (new), `test_gui_navigation_scope.py`'s one intentional flip. No `fmea_domain/` file touched.

Mirrored to `open_fmea_training_set` and byte-diffed (`diff -q`, not size/mtime): all 11 changed/new files identical. Full suite re-run there independently: 186/186.

## 5. Scope discipline

No new join-model for `Change`↔`FailureMode` — Django's default implicit M2M through-table only. No AJAX/search-as-you-type widget anywhere. No enforced status-transition rule (`fmea_domain/rules.py` untouched, confirmed alongside the rest of `fmea_domain/`). No `ResponsibleRole` CRUD. No Impact Matrix, Affected FMEA Items tab, Action Plan tab, or Change History tab/page/route — the detail page's read-only table is the only surface for the affected-FailureMode data, exactly as Section 1.4/7 specify. No `<canvas>`, no chart/graph library reference. No approval/review workflow or confirmation step beyond the plain create/edit form. No AI-assisted suggestion of any field.

## 6. Still open

- `.git/index.lock` still needs a manual delete in `open_fmea`. Nothing committed, per "build first, commit later."
- Remaining slices from the 2026-09-05 batch: J (Risk Trajectory & Propagation), K (Consolidated Home), L (Characteristics Flow) — not yet read in full or implemented.
