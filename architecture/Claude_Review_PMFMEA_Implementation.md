# Review — PM-FMEA (Mockup 3) First Increment Implementation

**Scope**: implements `OpenFMEA_PMFMEA_ArchitectureDecision.md`, lifting the standing hold on Mockup 3 (Preventive FMEA / PM-FMEA) per explicit user instruction on 2026-09-12 ("nadaljuj, tako da bodo vsi mockupi vključeni, velja", with an explicit confirmation to lift the PM-FMEA hold specifically). This also closes out the last open item in `OpenFMEA_MockupReadinessTracker.md` — see Section 6 below for the tracker correction this review carries.

## 1. What was built

- `models.FMEA.FMEA_TYPE_CHOICES` gains `("preventive", "Preventive FMEA (PM-FMEA)")` — every existing choice is untouched; the existing generic `create_fmea`/`FMEAForm` already makes it selectable with no further code.
- New `models.Asset` (`StableModel`): `name`, `asset_code`, `location`, `status` (Operational/Down/Under Maintenance via new `AssetStatus` choices class), `notes`. Four new standalone pages mirroring `System`'s pattern exactly: `asset_list`, `asset_create`, `asset_detail`, `asset_edit` (routes `/assets/`, `/assets/new/`, `/assets/<id>/`, `/assets/<id>/edit/`).
- New `models.FailureMode.asset` — nullable FK to `Asset`, `on_delete=SET_NULL`, optional on every FMEA type (not gated to `preventive`, consistent with how `RiskEvaluation.failure_scenario` is optional-everywhere from the FMEA-MSR work).
- New `pmfmea_worksheet` view/route/template (`/pmfmea/`), mirroring `dfmea_worksheet`/`pfmea_worksheet` exactly, filtered to `fmea_type="preventive"`, plus one PM-FMEA-specific "Asset / Machine" column matching the mockup's own "Top High Risk Maintenance Items" table shape.
- `dfmea_worksheet` corrected to `exclude(fmea_type__in=["process", "preventive"])` (previously excluded only `"process"`) — now that a third category exists, PM-FMEAs must not fall into the DFMEA bucket by default. No existing FMEA is reclassified by this change.
- Sidebar: "Preventive FMEA (PM-FMEA)" added under "FMEA ANALYSIS" (after PFMEA); new "MAINTENANCE" nav group with one link, "Assets & Equipment" — both exactly as `OpenFMEA_MockupGUICodingRequirements.md` itself proposed for this mockup.
- `fmea_detail.html`: the "Add Failure Mode" form gains an optional "Asset (PM-FMEA)" field; a failure mode's worksheet row shows its linked asset as a sub-line when present (no new column, no colspan change).
- Domain layer: `fmea_domain.Asset` (`NamedEntity` — `asset_code`/`location`/`status`/`notes`) and `FailureMode.asset_id: str | None`, exported from `fmea_domain/__init__.py`, mirroring the Django model.
- `seed_demo.py`: one demo `Asset` ("Injection Molding Machine 03" / `IMM-03`, the mockup's own example) and one demo Preventive FMEA with a linked failure mode ("Spindle bearing wear").
- `admin.py`: `AssetAdmin` registered, mirroring `SystemAdmin`.
- One migration: `0016_asset_alter_fmea_fmea_type_failuremode_asset.py`.

## 2. Decisions made (see the architecture decision doc for full reasoning)

**A real, grounded first increment, not the full mockup.** The mockup specs classify almost everything else in Mockup 3 as Tier D (no backing entity anywhere): WorkOrder, MaintenancePlan, PM Compliance/Overdue-WO/Next-PM metrics, the Assets-Covered donut, the maintenance-lifecycle Validation Trajectory, Baseline/History versioning, a Reviews entity, and Open-EQMS links. This increment builds only what's real and groundable — PM-FMEA existing as a working `fmea_type` with an Asset a failure mode can reference — the same scoping discipline used for Mockup 7 (System, Slice E) and Mockup 8 (ProductCharacteristic register, Slice P).

**`FailureMode.asset` optional everywhere, not gated by `fmea_type`.** Simpler than branching template/form logic by type, and consistent with this project's precedent (`RiskEvaluation.failure_scenario`).

**The Engineering Context drawer's "Linked Asset for Step 30" (an `Operation`→`Asset` link) was NOT built.** That's a different relationship than `FailureMode`→`Asset`, tied to the Process-step drawer rather than a failure mode, and is its own not-yet-decided design question — left for a future increment if wanted.

## 3. A stale-tracker correction folded into this review

While researching Mockup 3, direct inspection of the live code (routes, views, test counts) showed that `OpenFMEA_MockupReadinessTracker.md`'s rows for Slices N, O, P, and Q — last written 2026-09-10 as "decided, instructed, not yet built" — were stale: all four were already fully implemented and tested (`process_characteristic_list`'s KPI/detail-panel richer page, `failure_mode_list`'s richer page, the `product_characteristic_list` read-only register, and `characteristic_link_list`'s filter/detail-panel enrichment all exist in the live code, confirmed via direct route/view inspection and a 284-passing test run before any PM-FMEA code was written). The tracker is corrected in this update (Section 6 below) rather than left pointing at stale status.

## 4. Explicitly out of scope (unchanged from the architecture decision doc)

WorkOrder/MaintenancePlan and every metric derived from them (PM Compliance %, Overdue WO, Next PM). The Assets-Covered donut, the maintenance-lifecycle Validation Trajectory with its readiness/coverage bars, and the "Top High Risk Maintenance Items" widget as its own dashboard card (the plain worksheet table with an Asset column is the read-only substitute for now). Baseline/History versioning for an FMEA. The Reviews sub-tab. Links (Open-EQMS) and FMEA Workspace Settings. The two-tier tab hierarchy as its own page shell (the existing worksheet page is reused as-is, as it already is for every other `fmea_type`). The Engineering Context drawer's Linked-Asset/Maintenance-Status sections. Mockup 4 (Consolidated Home's PM-FMEA rollup, Operations module, Project Health panel) — unchanged, still cataloged-only.

## 5. Tests

New file `tests/test_pmfmea_first_increment.py`, 21 tests: `Asset` model defaults/`__str__`/domain round-trip (2); `FailureMode.asset` optionality across FMEA types, domain `asset_id` round-trip, `SET_NULL` on Asset deletion (4); the new `preventive` choice coexisting with every pre-existing choice (1); `pmfmea_worksheet`/`dfmea_worksheet`/`pfmea_worksheet` scoping correctness including the linked-asset display (4); the four new `asset_*` pages (4); `FailureModeForm`'s new field (1); `add_failure_mode` saving/not-requiring an asset (2); the two new sidebar links and `fmea_detail`'s new form field/worksheet-row display (3).

Two pre-existing tests needed a one-line update, not a behavior change: `test_dashboard_view.py::test_response_excludes_out_of_scope_sections` and `test_risk_trajectory.py::test_pages_have_no_canvas_and_no_propagation_chain_content` both used the bare string `"PM-FMEA"` as a canary for "nothing about preventive maintenance has leaked into this page," written when PM-FMEA had zero backing anywhere. Now that "Preventive FMEA (PM-FMEA)" is a real, permanent sidebar label on every page (the same way "DFMEA"/"PFMEA" already are), that specific canary is stale, not a sign of a defect — both were updated to check for `"Maintenance Readiness"` instead, a phrase specific to the still-unbuilt maintenance-dashboard vision, preserving exactly the scope guarantee those tests existed to enforce.

284 → 305 tests, all passing (`/tmp/openfmea_venv/bin/python -m pytest tests/`). `manage.py makemigrations --check --dry-run`: no changes pending. Fresh `migrate` + `seed_demo` run twice (idempotency check) both succeed. `manage.py check`: no issues.

Grep-confirmed absent from the diff: `WorkOrder`, `MaintenancePlan`, `PM Compliance`/`pm_compliance`, `Baseline` as a model/field/entity (the only hits are the new code's own comments naming them as *not* built, and one pre-existing, unrelated "baseline design" phrase in AIAG & VDA Severity criteria text from Part A).

## 6. Mockup Readiness Tracker update

`OpenFMEA_MockupReadinessTracker.md` is updated alongside this review: rows for Mockups 9, 15, 21 (Slices Q, O, N) and 8 (Slice P) are corrected from "instructed, not yet built" to "built" (confirmed live in code, not merely reported), and Mockup 3's row moves from "Not ready — standing hold" to "Built (first increment)" with this document and the architecture decision doc referenced. With this update, **all 23 mockups now have at least their grounded, real-data portion built** — the project's original "make them all ready for implementation" mandate, and now this session's "vsi mockupi vključeni" instruction, are both satisfied to the extent any of them can be without inventing ungrounded new modules (Operations, full Maintenance-management, versioning/Baseline, Reviews-scheduling) that no source document has yet specified in buildable detail.
