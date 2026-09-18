# Codex Implementation Instruction — Standalone DFMEA / PFMEA Worksheet Pages (Slice D)

Status: Approved for implementation, 2026-09-04. Picked as the next slice after Projects+Team, Slice A (nav restyle), and Slice C (Engineering Context) — all built and independently verified. This answers the "DFMEA" / "PFMEA" items from the user's requested build order, immediately after the "mandatory" foundation (System/Product/Process, FMEA Project, FMEA Team, Failures, Causes, Effects, Preventions, Detections, Actions) — which, per independent verification against the real code, is **already built and working today** (see the accompanying status note); this slice does not rebuild any of that.

This is a narrowed slice of Mockups 11 (DFMEA) and 12 (PFMEA) from `OpenFMEA_DNA_CoreReference.md` Section 10 — **Tier A/B content only**: the real worksheet data, shown as its own cross-cutting page per FMEA type, instead of only inside one FMEA's detail page. Every Tier C/D item those two mockups also showed (per-factor Severity/Occurrence/Detection banding, Structure Tree, Interface Matrix, Parameter Diagram, RPN trend/donut charts, Control Plan Link) is explicitly excluded — each needs its own decision or review that hasn't happened yet.

Grounded directly in the real code before writing this: `views.py`'s `fmea_detail`, `_build_worksheet_rows`, `_worksheet_row` (read in full), `models.py`'s `FMEA.FMEA_TYPE_CHOICES` and `RiskEvaluation`.

## 0. Decisions for this slice

1. **"DFMEA" = every FMEA whose `fmea_type` is NOT `"process"`; "PFMEA" = every FMEA whose `fmea_type` IS `"process"`.** The real `FMEA_TYPE_CHOICES` are `design`/`process`/`product`/`software`/`system` — there is no `"preventive"` value (confirmed absent) and no separate "DFMEA" value; `design`/`product`/`software`/`system` all read naturally as design-side analyses, so they group together on the DFMEA page. **This is a stated judgment call, not a hidden one** — flag clearly in your report if this grouping looks wrong once real data is in front of you, so it can be corrected rather than silently kept.
2. **Reuse `_build_worksheet_rows`/`_worksheet_row` completely unchanged.** Do not fork, duplicate, or refactor them. Call the existing helper once per FMEA in the type-filtered queryset and concatenate the results; attach the owning `fmea` to each row dict at the call site (e.g. `row["fmea"] = fmea` after calling the helper) rather than modifying the helper itself, since `fmea_detail.html` depends on its current return shape and must not change.
3. **No inline edit forms on these two new pages.** Every create/edit form for Function/FailureMode/Effect/Cause/Prevention/Detection/RiskEvaluation/Action already exists and stays exactly where it is, in `fmea_detail.html`. These two pages are read-only cross-cutting views with a link per row into the owning FMEA's real worksheet (`fmea:fmea_detail`) for any editing. Duplicating seven forms across three pages is not in scope.
4. **One "Actions" column: open count and overdue count, computed at render time.** For each row, sum `failure_mode.recommended_actions.count()` (only for the "no cause" rows, to avoid double-counting) plus `cause.recommended_actions.count()` (for cause rows) — matching how `fmea_detail.html` itself already separates "actions on a cause" from "actions not tied to a cause." "Overdue" = `due_date` is set, in the past, and `status` is not `completed`/`verified`/`cancelled`. This is a simple aggregate over existing fields (Tier B, per the Mockup 11 audit) — no new field, no new model.
5. **No charting/canvas of any kind.** The mockups' RPN-trend line chart and Actions-by-status donut are both excluded — RPN history is already visible via the built Risk Matrix, and an Actions view already exists at `fmea:action_detail` (a full Actions list page is a separate, later, optional slice — not this one).
6. **No Structure Tree, Interface Matrix, Parameter Diagram, or Control Plan Link tab.** All four are genuinely new concepts with zero backing in the codebase today (Structure Tree needs the same missing `System` hierarchy as Mockup 7; Interface Matrix and Parameter Diagram have no entity anywhere; Control Plan Link is specifically gated by DNA rule 7). This slice is a single table per page, not a six-tab page.
7. **No per-factor Severity/Occurrence/Detection "Rating + Class" banding.** Show the raw `severity`/`occurrence`/`detection` integers and the already-computed `result`/`result_class` exactly as `_worksheet_row` returns them today (RPN + classification, or AP priority + classification, depending on the evaluation method) — unchanged from how `fmea_detail.html` already displays them.
8. **No "Element / Part" column.** No such `FailureMode` field exists. Use `function`/`requirement` exactly as `_worksheet_row` already provides them — same as the existing worksheet.
9. **This is the first real content under a new "FMEA ANALYSIS" sidebar group.** Slice A explicitly left this group out because it had zero real pages behind it at the time (its Section 0.1). That condition no longer holds once this slice ships — add the group now, with exactly these two links, per Slice A's own stated rule ("no navigation for anything not built yet" — now there is something built).

## 1. Exact Scope

1. Two new views, each filtering `FMEA.objects` by `fmea_type` per decision 1, then calling `_build_worksheet_rows` per FMEA and concatenating (with `fmea` attached to each row per decision 2):
   - `dfmea_worksheet` — route `/dfmea/`, name `fmea:dfmea_worksheet`. FMEAs where `fmea_type != "process"`.
   - `pfmea_worksheet` — route `/pfmea/`, name `fmea:pfmea_worksheet`. FMEAs where `fmea_type == "process"`.
2. Two new templates, each one dense table (reuse the existing `table-shell`/`table` CSS classes already used by Risk Matrix and Engineering Context — no new CSS), columns: FMEA (name, linking to `fmea:fmea_detail`), Function/Requirement, Failure Mode (name + description), Effects, Cause (name + description, or "No cause"), Severity, Occurrence, Prevention Controls, Detection Controls, Detection rating, Result (RPN/priority + classification, exactly as `_worksheet_row` returns), Actions (open count / overdue count per decision 4).
3. `_sidebar.html`: add a new `FMEA ANALYSIS` group (same `.nav-group`/`.nav-group-title` markup as every other group), with two links — `DFMEA` -> `{% url 'fmea:dfmea_worksheet' %}` and `PFMEA` -> `{% url 'fmea:pfmea_worksheet' %}` — placed after the existing `RISK` group and before `Import & Review`.

## 2. Exact Allowed / New Files

```text
django_app/fmea_app/views.py                                    # two new views + one small shared helper only; _build_worksheet_rows/_worksheet_row/fmea_detail untouched
django_app/fmea_app/urls.py                                      # two new routes
django_app/fmea_app/templates/fmea_app/dfmea_worksheet.html      # new
django_app/fmea_app/templates/fmea_app/pfmea_worksheet.html      # new
django_app/fmea_app/templates/fmea_app/_sidebar.html              # add the new FMEA ANALYSIS group, nothing else changed

tests/test_dfmea_pfmea_worksheets.py                              # new
tests/test_gui_navigation_scope.py                                # one required update — see Section 4
```

Nothing else. No `models.py`, `forms.py`, or migration changes — every field used here already exists and is already read the same way in `fmea_detail.html`.

## 3. Required Validation and Explicit Exclusions

- No new model, no new migration.
- `_build_worksheet_rows` and `_worksheet_row` are unchanged (diff them explicitly against the current file before finishing — zero lines changed in either function).
- No inline create/edit form appears on either new page — both are read-only, with a link into `fmea:fmea_detail` for editing.
- No chart/canvas/SVG diagram of any kind on either page.
- No "Structure Tree", "Interface Matrix", "Parameter Diagram", or "Control Plan" content anywhere on either page.
- No per-factor Rating+Class banding beyond what `_worksheet_row` already computes.
- No "Element / Part" column.
- A `design`/`product`/`software`/`system`-typed FMEA's rows appear only on `/dfmea/`, never on `/pfmea/`; a `process`-typed FMEA's rows appear only on `/pfmea/`, never on `/dfmea/`.
- `_sidebar.html` diff is exactly one new `FMEA ANALYSIS` group with two links — every other group stays exactly as Slice C left it.

## 4. Required Tests

`tests/test_dfmea_pfmea_worksheets.py`:
- Render `/dfmea/` and `/pfmea/`; assert a fixture design-type FMEA's failure mode appears only on `/dfmea/`, and a fixture process-type FMEA's failure mode appears only on `/pfmea/`.
- Assert row content (failure mode name, severity/occurrence/detection integers, the computed RPN/result string, at least one prevention control name and one detection control name) matches the fixture data exactly, for both pages.
- Assert the Actions column shows the correct open/overdue counts for a fixture with a known mix (e.g. one open-not-overdue action and one overdue action).
- Assert neither page contains `<canvas`, `"Structure Tree"`, `"Interface Matrix"`, `"Parameter Diagram"`, or `"Control Plan"`.
- Both pages link each row's FMEA name to the correct `fmea:fmea_detail` URL.

`tests/test_gui_navigation_scope.py` — **one required, intentional change**: Slice A's own test currently asserts `"FMEA ANALYSIS"` does NOT appear in the sidebar (correct at the time, since nothing real existed under it). That condition is now false — update that specific assertion so `"FMEA ANALYSIS"` is asserted **present**, and add assertions that `"DFMEA"` and `"PFMEA"` both appear as real links. Every other existing assertion in that test file (FMEA ELEMENTS/VALIDATION & CHANGE/"FMEA Team" still absent, etc.) stays exactly as-is — this is a one-line flip on one specific assertion, not a rewrite. Call this out explicitly in your report so it reads as an intentional, expected change, not a regression.

Full existing suite re-run with no other unrelated assertion changes.

## 5. Commands to Run

```powershell
python -B manage.py check
python -B manage.py makemigrations --check --dry-run
python -B -m pytest
```

## 6. Acceptance Criteria

1. `/dfmea/` and `/pfmea/` each render real worksheet rows, correctly split by `fmea_type` per decision 1, with correct Actions counts and correct links.
2. `_build_worksheet_rows`/`_worksheet_row` are byte-identical to their current state — confirm with a diff, not just "it still works."
3. `_sidebar.html` gains exactly one new `FMEA ANALYSIS` group with exactly two links; every other group unchanged.
4. No model/migration changes anywhere in the diff.
5. No charting, no Structure Tree/Interface Matrix/Parameter Diagram/Control Plan content anywhere.
6. Full test suite passes (including the one intentional, called-out flip in `test_gui_navigation_scope.py`), `manage.py check` clean, zero new migrations.
7. Mirrored into `open_fmea_training_set` per the standing discipline (byte-diffed, not just size/mtime).

## 7. Explicit Exclusions (restated for emphasis)

No new model or migration. No inline forms on either new page — editing stays in `fmea_detail.html`. No charting/canvas library. No Structure Tree, Interface Matrix, Parameter Diagram, or Control Plan Link. No per-factor S/O/D banding beyond what already exists. No "Element/Part" column. No changes to `_build_worksheet_rows`/`_worksheet_row`/`fmea_detail` themselves. If any of this seems to need changing to deliver a working slice, stop and report — do not silently expand scope.
