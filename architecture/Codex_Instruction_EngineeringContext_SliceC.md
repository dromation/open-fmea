# Codex Implementation Instruction — Engineering Context Page (Slice C, narrowed)

Status: Approved for implementation, 2026-09-04. Picked as the next slice after Projects+Team and Slice A (both built and independently verified). This is **not** the full Slice C from `Codex_Instruction_GUI_Mockup_Implementation_Preparation.md` (mockups 02/07/08/09/21) — that scope was checked against `OpenFMEA_DNA_CoreReference.md`'s own mockup audit and found to stack three separately-gated dependencies on top of each other. Narrowed to the one part that's genuinely Tier A/B: real data with no top-level page yet.

Grounded directly in the real model/view code before writing this (`models.py`, `views.py`, `fmea_detail.html`) — not assumed from the mockups.

## 0. Decisions for this slice

1. **Scope is Product + Process browsing only — no System, no Characteristics Flow diagram, no Process Control Characteristics.** The full Slice C in the prep doc bundles mockups 02 (Engineering Context), 07 (System/Product/Process), 08 (System Characteristics Base), 09 (Characteristics Flow/Diagram), and 21 (Process Control Characteristics). Per the DNA reference's own per-mockup audit:
   - Mockup 08 needs a `System` hierarchy (doesn't exist) and `ClassificationScheme` (explicitly not approved) — excluded.
   - Mockup 09 hard-depends on Mockup 08, needs a new relationship/edge entity, and a charting/graph library (every prior slice has explicitly excluded charting) — excluded.
   - Mockup 21 is the Control Plan concept, specifically gated by DNA rule 7 ("Approved Control Plans are never silently modified... any Control Plan change is a reviewed, human-approved workflow") — excluded.
   - What's left — Mockup 02's real content (already-approved per `Codex_Instruction_ProductProcessCharacteristic_Linking_Slice.md` Section 6) and the Product/Process (not System) part of Mockup 07 — is what this instruction actually builds.
2. **No `System` entity or tab.** `Product`/`Process`/`Operation` are real; a hierarchical `System` above them is not, and isn't invented here.
3. **No new Product detail page.** A `Product`'s characteristics are reachable indirectly today (`Product` -> `Function.product` -> `Requirement` -> `ProductCharacteristic`) and are already rendered in that product's owning FMEA's worksheet (`fmea_detail.html`'s Functions/Product Characteristics section). Don't duplicate that display in a new template — link a Product row straight to its FMEA's detail page instead.
4. **Processes link to the existing `fmea:process_flow` view — nothing new there.** That view (with its Process Characteristics + linked Product Characteristics panel) is already built and already correct per the DNA audit; this slice only makes it reachable from a top-level page instead of only from inside one specific FMEA's worksheet.
5. **No Type/Criticality/classification columns anywhere** — that's the still-not-approved `ClassificationScheme`/`ClassificationTerm` territory, excluded from every slice so far and excluded here too.

## 1. Exact Scope

1. New view + template, route `/context/` (`fmea:engineering_context`): two panels —
   - **Products** table: Name, Part Number, owning FMEA (name, linking to `fmea:fmea_detail`), Function count (`product.functions.count()`, computed at render time, not stored).
   - **Processes** table: Name, Process Code, owning FMEA (name, linking to `fmea:fmea_detail`), Operation count (`process.operations.count()`), each row also linking to `fmea:process_flow` for that process.
   Both tables span all FMEAs/projects — this is a cross-cutting browse page, not scoped to one FMEA. Use `select_related`/`prefetch_related` appropriately (existing views in this codebase already follow this pattern — match it).
2. `_sidebar.html`: add "Engineering Context" as a second real link under the existing `CONTEXT` group (added by Slice A), above or below "Process Characteristics" — either order is fine, just don't create a new group.

## 2. Exact Allowed / New Files

```text
django_app/fmea_app/views.py                                   # new engineering_context view only
django_app/fmea_app/urls.py                                     # one new route
django_app/fmea_app/templates/fmea_app/engineering_context.html # new
django_app/fmea_app/templates/fmea_app/_sidebar.html             # add the one link under CONTEXT, nothing else

tests/test_engineering_context.py                                # new
```

Nothing else. No `models.py`, `forms.py`, or migration changes — every field used here already exists.

## 3. Required Validation and Explicit Exclusions

- No `System` model, no System tab, no System column.
- No `ClassificationScheme`/`ClassificationTerm`/Type/Criticality anywhere.
- No new Product detail page/route — Product rows link to `fmea:fmea_detail`, not a new page.
- No changes to `fmea:process_flow` itself (view, template, or logic) — only linked to.
- No Characteristics Flow diagram, no chart/graph library, no SVG relationship diagram of any kind.
- No Process Control Characteristics / Control Plan content (Reaction Plan, Control Type enum, Process Control Flow diagram) anywhere.
- `_sidebar.html` diff is exactly one new `<a class="nav-link">` line under the existing `CONTEXT` group — the group header itself, and every other group, stay exactly as Slice A left them.

## 4. Required Tests

`tests/test_engineering_context.py`:
- Render `/context/` and assert both panel headings are present, plus at least one real Product row (name + part number) and one real Process row (name + process code), each linking to the correct real URL (`fmea:fmea_detail` for the product's/process's owning FMEA, `fmea:process_flow` for the process row).
- Assert Function count and Operation count render correctly for a fixture Product/Process with a known number of each.
- Assert the page contains no "System", "Classification", "Control Plan", or chart/canvas markup — a quick negative check consistent with `test_gui_navigation_scope.py`'s existing pattern.
- Full existing suite re-run with no unrelated assertion changes.

## 5. Commands to Run

```powershell
python -B manage.py check
python -B manage.py makemigrations --check --dry-run
python -B -m pytest
```

## 6. Acceptance Criteria

1. `/context/` renders real Products and Processes across all FMEAs, with correct counts and correct links.
2. `_sidebar.html` gains exactly one new link under the existing `CONTEXT` group; no other nav change.
3. No model/migration changes anywhere in the diff.
4. No System/ClassificationScheme/Control-Plan/charting content anywhere.
5. Full test suite passes, `manage.py check` clean, zero new migrations.
6. Mirrored into `open_fmea_training_set` per the standing discipline (byte-diffed, not just size/mtime, per the last two slices' practice).

## 7. Explicit Exclusions (restated for emphasis)

No `System` entity or hierarchy. No `ClassificationScheme`/`ClassificationTerm`. No Characteristics Flow/relationship diagram. No charting/graph library. No Process Control Characteristics / Control Plan content. No new Product detail page. No changes to the existing `process_flow` view/template beyond linking to it. If any of this seems to need changing to deliver a working slice, stop and report — do not silently expand scope.
