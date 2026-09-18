# Codex Implementation Instruction — System Characteristics Base (Slice M)

Status: Approved for implementation, 2026-09-04. This is the first implementation drawn from two prior review/decision documents: `OpenFMEA_SystemHierarchy_ArchitectureReview.md` (proposing a self-referential `System` model, Decisions 1–5) and `OpenFMEA_ClassificationScheme_ArchitectureDecision.md` (proposing `ClassificationScheme`/`ClassificationTerm` wired to `ProductCharacteristic`). Both are adopted here at their narrowest stated scope, per DNA rule 8. This slice makes `System` and classification real and browsable — it is a foundational-entity slice, the same role Engineering Context (Slice C) played for `Product`/`Process`. It does **not** deliver Mockup 8's full dashboard: no Organizations stat card, no multi-org, no donut charts, no Characteristics Flow diagram, no force-directed anything. Those all remain separately gated, unbuilt scope.

## 0. Decisions for this slice

1. **Build `System` exactly as `OpenFMEA_SystemHierarchy_ArchitectureReview.md` proposed, adopted in full for this slice.** Self-referential `parent` (nullable FK to self), fields `name`, `description`, `code`, `status`. `status` uses the review's own proposed minimal value set (`active`/`inactive` choices) — this slice adopts that proposal rather than leaving it open again. Add a nullable `system` FK to both `Product` and `Process` (`related_name="products"`/`"processes"` on `System`, `on_delete=SET_NULL`) — existing rows keep `system=None`, no backfill. No direct `FMEA`→`System` FK (the review's Decision 5/6 territory — not needed for this slice's read-only list view).
2. **Build `ClassificationScheme`/`ClassificationTerm` exactly as `OpenFMEA_ClassificationScheme_ArchitectureDecision.md` proposed, wired to `ProductCharacteristic` only.** `ProductCharacteristic.primary_classification` FK to `ClassificationTerm`, `on_delete=SET_NULL`. Seed one scheme ("Product Characteristic Classification (default)") with four terms (Legal, Safety, Functional, Decorative) via `seed_classification_scheme`, mirroring `seed_cause_category_scheme`'s idempotent pattern. No change to `ProcessCharacteristic`.
3. **New page: a simple System list/tree, route `/systems/` (`fmea:system_list`).** Table/tree columns: name, code, status, parent (name, linked), child count (`system.children.count()`), linked-Product count and linked-Process count (`system.products.count()` / `system.processes.count()`). Grouping by parent is a simple indented list (parent row, then its direct children indented once) — not a collapsible JS tree widget, not a force-directed graph. This is the whole of the new page: no stat cards beyond what's listed here, no "Linked to FMEA" aggregate beyond the two counts named, no Organizations card, no donut/pie chart.
4. **Simple create/edit form for `System`.** Fields: `name`, `description`, `code`, `parent` (dropdown of existing `System` rows, excluding self on edit), `status` (dropdown of the two choices). No image/attachment upload, no owner field (`OpenFMEA_MockupSpecifications_GUIWireframeArchitecture.md`'s `owner`/image fields for `System` are separately unapproved — do not add them here).
5. **Explicitly excluded from this slice:** Importance scale, Monitoring status, Nominal Value/Target/Unit fields on any characteristic (all seen in Mockup 8, none approved by either grounding document), any chart (Chart.js or otherwise), any Organizations/tenancy concept, the Characteristics Flow diagram (separate mockup/slice, needs its own instruction), circular-parent-reference prevention beyond a basic "cannot set a System as its own ancestor" validation on save (full cycle-detection UI/tooling is not required — a straightforward walk-up-the-parent-chain check is sufficient).

## 1. Exact Scope

1. `System` model: self-referential `parent` (nullable FK to self, `related_name="children"`, `on_delete=SET_NULL`), `name`, `description`, `code`, `status` (choices `active`/`inactive`, default `active`). `StableModel` subclass, same conventions as every other entity in this codebase.
2. `Product.system` / `Process.system`: nullable FK to `System`, `on_delete=SET_NULL`, `related_name="products"` / `related_name="processes"`.
3. `ClassificationScheme` (`name`, `description`) and `ClassificationTerm` (`scheme` FK `related_name="terms"` `on_delete=CASCADE`, `name`, `description`, `order`), both `StableModel` subclasses.
4. `ProductCharacteristic.primary_classification`: nullable FK to `ClassificationTerm`, `on_delete=SET_NULL` (migration repurposes the existing dormant `primary_classification_id` field — do not leave a second, unused field behind).
5. `seed_classification_scheme` management command: idempotent, creates the one scheme and its four terms (Legal, Safety, Functional, Decorative; `order` 1–4) if and only if they don't already exist.
6. `GET /systems/` (`fmea:system_list`): indented list of all `System` rows (top-level systems first, each followed by its direct children indented once — one level of nesting is sufficient for this slice's data volume; do not build recursive-depth rendering beyond what a simple template `{% for %}` over `system.children.all()` produces naturally), showing name, code, status, parent name (linked to that parent's row if scrolled elsewhere on the same page, no separate anchor-scroll JS needed), child count, linked-Product count, linked-Process count.
7. `GET /systems/new/` and `GET /systems/<stable_id>/edit/` (`fmea:system_create` / `fmea:system_edit`): the create/edit form from Decision 4. `POST` to the same routes saves; on save, validate that `parent` is not the system itself and not a descendant of itself (walk `parent` chain upward from the proposed parent; if the system being edited appears in that chain, reject with a clear error).
8. `ProductCharacteristic` create/edit form: add a `primary_classification` `<select>` populated from the seeded scheme's `ClassificationTerm` rows (ordered by `order`), including a blank/"Unclassified" option.
9. Wherever `ProductCharacteristic` is already rendered — the worksheet table in `fmea_detail.html` and the Engineering Context page's Product panel, if that panel already lists `ProductCharacteristic` rows — add a read-only "Classification" column showing `primary_classification.name` or a blank/"—" when unset.
10. Sidebar: add one link to `/systems/` under the same nav group Engineering Context lives in (or the nearest equivalent grouping already in `_sidebar.html`) — no new nav group, no sub-items.

## 2. Exact Allowed / New Files

```text
django_app/fmea_app/models.py                                    # System, ClassificationScheme, ClassificationTerm; Product.system, Process.system, ProductCharacteristic.primary_classification
django_app/fmea_app/migrations/000X_system_classification.py     # new migration(s) — separate migration per model group if that's this codebase's existing convention, check recent migration files
django_app/fmea_app/admin.py                                      # register System, ClassificationScheme, ClassificationTerm
django_app/fmea_app/management/commands/seed_classification_scheme.py  # new, mirrors seed_cause_category_scheme.py
django_app/fmea_app/views.py                                      # system_list, system_create, system_edit views only; add primary_classification handling to the existing ProductCharacteristic form view
django_app/fmea_app/urls.py                                       # three new routes
django_app/fmea_app/forms.py                                      # SystemForm; add primary_classification field to the existing ProductCharacteristic form
django_app/fmea_app/templates/fmea_app/system_list.html           # new
django_app/fmea_app/templates/fmea_app/system_form.html           # new
django_app/fmea_app/templates/fmea_app/fmea_detail.html           # add Classification column to the existing worksheet table only
django_app/fmea_app/templates/fmea_app/engineering_context.html   # add Classification column, only if this template already renders ProductCharacteristic rows
django_app/fmea_app/templates/fmea_app/_sidebar.html              # add the one link, nothing else

tests/test_system_model.py                                        # new
tests/test_classification_scheme.py                               # new
tests/test_system_characteristics_base_views.py                   # new
```

If any existing file not listed above turns out to need a change to make this work, stop and report why before touching it.

## 3. Required Validation and Explicit Exclusions

- No Importance field, no Monitoring-status field, on `System`, `ClassificationTerm`, or `ProductCharacteristic` — not even as an unused/dormant field. Both remain still-uncommitted-to concepts; do not lay groundwork for them "since you're in the model anyway."
- No Nominal Value/Target/Unit fields anywhere in this diff.
- No chart, no Chart.js usage, no SVG/canvas diagram — `system_list.html` is a plain HTML table/list.
- No Organizations/tenancy model or field, no "Sources" stat card.
- No Characteristics Flow diagram or any relationship-graph rendering.
- No hierarchy (`parent_term_id`) on `ClassificationTerm`, no `secondary_classification_ids` on `ProductCharacteristic` — flat scheme, single classification, per `OpenFMEA_ClassificationScheme_ArchitectureDecision.md` Decision 1–2.
- No `ProcessCharacteristic` change of any kind.
- No scheme/term management UI (create/edit/delete a `ClassificationScheme` or `ClassificationTerm` from the GUI) — the one scheme is seed-only in this slice.
- No image/attachment/owner field on `System`.
- Circular-parent validation is the one required guard beyond basic field validation — do not skip it, and do not build more than the walk-up-the-chain check described in Section 1.7.

## 4. Required Tests

`tests/test_system_model.py`:
- Creating a `System` with a `parent` succeeds; `parent.children` includes it.
- Setting a `System`'s `parent` to itself is rejected with a clear validation error.
- Setting a `System`'s `parent` to one of its own descendants (a grandchild, two levels deep) is rejected with a clear validation error.
- A `Product`/`Process` with `system=None` continues to save and display correctly (no forced backfill).

`tests/test_classification_scheme.py`:
- Running `seed_classification_scheme` creates exactly one `ClassificationScheme` and four `ClassificationTerm` rows (Legal, Safety, Functional, Decorative) with `order` 1–4.
- Running `seed_classification_scheme` twice does not create duplicate schemes or terms (idempotent, mirrors the `CauseCategoryScheme` seed test).
- A `ProductCharacteristic` with `primary_classification` set to a seeded term round-trips correctly; one with `primary_classification=None` displays as unclassified, not as an error.

`tests/test_system_characteristics_base_views.py`:
- `GET /systems/` returns 200 and lists every `System` row, with each top-level system's direct children rendered under it.
- The child-count, linked-Product-count, and linked-Process-count shown for a given `System` match its actual `children`/`products`/`processes` querysets.
- `GET /systems/new/` and posting a valid form creates a `System`; posting a form with `parent` set to a value that would create a cycle is rejected and no `System` is modified.
- The response body of `/systems/` contains no "Organizations" label, no "Importance" or "Monitoring" column header, and no chart/canvas markup (locks in the Section 3 exclusions the same way `test_process_flow_view.py` locks in its own slice's exclusions).
- `fmea_detail.html`'s worksheet renders a "Classification" column for `ProductCharacteristic` rows showing the seeded term's name when set, and a blank/"—" placeholder when `primary_classification` is `None`.

## 5. Commands to Run

```powershell
python -B manage.py check
python -B manage.py makemigrations --check --dry-run
python -B -m pytest
```

## 6. Acceptance Criteria

1. `System` exists, self-referential, with the exact field set from Section 1.1, and is not hardcoded/bypassed anywhere a real hierarchy query is needed.
2. `Product.system` and `Process.system` exist as nullable FKs; no existing `Product`/`Process` row requires a value to keep working.
3. `ClassificationScheme`/`ClassificationTerm` exist, seeded via an idempotent management command, with exactly the four terms named in Section 1.5 — not hardcoded as Python constants anywhere reachable by application logic.
4. `ProductCharacteristic.primary_classification` is a real FK to `ClassificationTerm`, settable via the existing create/edit form, and displayed read-only wherever `ProductCharacteristic` already appears.
5. `/systems/` renders a real, queryable list of `System` rows with the exact columns named in Section 1.6 — no more, no fewer.
6. A `System` cannot be made its own ancestor; the validation is enforced on save, not just in the UI.
7. `ProcessCharacteristic` does not appear anywhere in this slice's diff.
8. No Importance, Monitoring-status, Nominal Value/Target/Unit, Organizations, chart, or Characteristics-Flow-diagram code appears anywhere in this slice's diff.
9. `manage.py check`, `makemigrations --check --dry-run`, and the full test suite all pass.

## 7. Explicit Exclusions (restated for emphasis)

Importance scale, Monitoring status, Nominal Value/Target/Unit fields, any chart or diagram (Chart.js, canvas, SVG relationship graph), Organizations/multi-tenancy, the Characteristics Flow diagram, `ClassificationTerm` hierarchy (`parent_term_id`), `ProductCharacteristic.secondary_classification_ids`, any change to `ProcessCharacteristic`, any scheme/term management UI, and any `System` field beyond name/description/code/parent/status (no owner, no image/attachment). This slice makes `System` and `ClassificationScheme` real and browsable as foundational entities — it is explicitly not Mockup 8's full dashboard. If you believe any of this needs to change to deliver a working slice, stop and report — do not silently expand scope.
