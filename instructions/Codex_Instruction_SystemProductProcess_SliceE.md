# Codex Implementation Instruction — System / Product / Process (Slice E)

Status: Approved for implementation, 2026-09-04. Builds `OpenFMEA_SystemHierarchy_ArchitectureReview.md`'s six proposed decisions, now treated as confirmed (per explicit user direction, "make them all ready for implementation," with no objection to any of the six specifics). Picked as part of pushing every remaining mockup toward implementation-readiness, following the same narrow-scope-per-slice pattern as every prior slice in this project (Projects+Team, Slice A, Slice C, Slice D).

Grounded directly in the real code before writing this: `Product`/`Process`/`FMEA`/`StableModel` in `models.py`, the existing `Product`/`Process` forms in `forms.py`, `_sidebar.html`'s `CONTEXT` group (added by Slice A, extended by Slice C).

## 0. Decisions for this slice

1. **`System` is a container above `Product`/`Process`.** Add a nullable `system` FK to each: `system = models.ForeignKey("System", null=True, blank=True, on_delete=models.SET_NULL, related_name="products")` on `Product`, and the equivalent with `related_name="processes"` on `Process`. (`related_name="products"`/`related_name="processes"` are free to reuse here — the existing `FMEA` FK on these models already uses its own distinct `related_name` of `"products"`/`"processes"` *from `FMEA`'s side*; confirm the actual existing `related_name` on `Product.fmea`/`Process.fmea` before naming these, and pick a non-colliding `related_name` such as `"products"`/`"processes"` accessed from `System` — i.e. `system_instance.products.all()` / `system_instance.processes.all()` — adjusting the name only if it collides with something already defined.) This matches the architecture review's Decision 1 verbatim.
2. **Hierarchy shape: self-referential, arbitrary depth.** One `System` model with a nullable `parent` FK to itself (`related_name="children"`). Not a fixed two-level System/Subsystem split — a "Subsystem" is simply a `System` row with `parent` set. Matches Decision 2 verbatim.
3. **This slice does not build the DFMEA/PFMEA "Structure Tree" tab.** That is a separate, later concern (Mockup 11/12), explicitly deferred per Decision 3 of the review. Nothing in this slice precludes reusing this same `System` tree for it later — no design choice here (e.g. no per-FMEA scoping added to `System`) closes that door.
4. **`System` fields, exactly:** `name` (CharField, required), `description` (TextField, blank), `code` (CharField, short identifier, same pattern as `Process.process_code` — required, not unique at the DB level unless `Process.process_code` already enforces uniqueness, in which case match that exactly), `parent` (nullable FK to self, `related_name="children"`), `status` (CharField with `choices`, a simple closed enum: `("active", "Active")` / `("inactive", "Inactive")`, default `"active"`). Matches Decision 4 verbatim. No Type/Category/Importance/Monitoring-status fields — those belong to the still-unapproved `ClassificationScheme` concept and stay out entirely.
5. **`System` extends `StableModel`**, exactly like every other model in this app — gives it `stable_id`, `schema_version`, `revision` for free, and makes it addressable at `/systems/<stable_id>/` the same way every other detail route in this app already works (e.g. `fmea:fmea_detail`).
6. **No forced backfill.** `Product.system` and `Process.system` stay nullable indefinitely. The migration adding them is purely additive — no data migration, no default-System creation, existing rows are completely unaffected and continue to render exactly as they do today everywhere else in the app (Engineering Context, `fmea_detail.html` worksheet, Process Flow). Matches Decision 5 verbatim.
7. **No direct `FMEA.system` FK.** `FMEA` reaches `System` only indirectly, through its `Product`s' and `Process`es' `system` FK. Matches Decision 6 verbatim.
8. **List page is a flat list with a "Parent" column, not a rendered tree widget.** Sort alphabetically by `name` within a simple two-key ORM order (`parent__name`, then `name`) so children of the same parent sort together and root Systems sort together — this is a stated simplification, not an omission: a real indented/collapsible tree widget is a UI investment that isn't justified for a first browsing page over what is likely a small number of System rows. The "Parent" column shows the parent's `name` (or "—" / blank for a root System) and links to that parent's own `fmea:system_detail` page.
9. **Self-parent cycle prevention is a simple form-level check only, not full cycle detection.** The `SystemForm`'s `parent` field queryset excludes the `System` instance being edited (on create, there is no instance yet, so no exclusion is needed — the full queryset is offered). This blocks the one-hop cycle (`A.parent = A`) but does **not** detect or block a longer cycle (e.g. `A.parent = B`, then editing `B.parent = A`) — that is out of scope for this slice, called out here explicitly rather than left as a silent gap. If a future slice needs full cycle detection, it can add it then.
10. **Product/Process form changes are additive only.** Locate the existing `ProductForm`/`ProcessForm` (or equivalent inline form construction) in `forms.py` and add one new optional `system` field (a `ModelChoiceField`/select, `required=False`, queryset `System.objects.all().order_by("name")`) to each, without touching any other field, widget, validation, or `Meta` option already present on those forms.

## 1. Exact Scope

1. **New `System` model** in `models.py`, extending `StableModel`:
   - `name` — `CharField(max_length=200)`, required.
   - `description` — `TextField(blank=True, default="")`.
   - `code` — `CharField(max_length=...)`, matching `Process.process_code`'s exact `max_length` and blank/null settings.
   - `parent` — `ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL, related_name="children")`.
   - `status` — `CharField(max_length=..., choices=STATUS_CHOICES, default="active")` where `STATUS_CHOICES = [("active", "Active"), ("inactive", "Inactive")]`.
   - `__str__` returning `name`, matching this app's convention on other models.
   One migration, additive only.
2. **New nullable `system` FK on `Product` and `Process`** (`null=True, blank=True, on_delete=models.SET_NULL, related_name="products"` / `related_name="processes"` respectively, as in Decision 1 above). Same migration file as the `System` model, or a second migration immediately after it — either is fine as long as `makemigrations` produces exactly these two additive changes with no other side effects.
3. **New page** — view `system_list`, route `/systems/`, name `fmea:system_list`. Queries `System.objects.select_related("parent").annotate(product_count=Count("products", distinct=True), process_count=Count("processes", distinct=True)).order_by("parent__name", "name")`. Template shows one `.table-shell` table: Name (linking to `fmea:system_detail`), Code, Status, Parent (name, linking to that parent's `fmea:system_detail`, or "—" if root), Product count, Process count. Include a "New System" link/button to the create form (see item 5).
4. **New page** — view `system_detail`, route `/systems/<stable_id>/`, name `fmea:system_detail`. Shows the `System`'s own fields (name, code, description, status, parent if any — linking to the parent's own detail page). Three sub-sections:
   - Linked Products: name, `part_number`, owning FMEA (name, linking to `fmea:fmea_detail`).
   - Linked Processes: name, `process_code`, owning FMEA (name, linking to `fmea:fmea_detail`).
   - Child Systems (`system.children.all().order_by("name")`): name, code, status, each linking to its own `fmea:system_detail`.
   Include an "Edit" link to the edit form (see item 5).
5. **Create/edit form for `System`** — `SystemForm` in `forms.py`, fields exactly `name`, `description`, `code`, `parent`, `status`. `parent` is a `ModelChoiceField` (or the model form's default select widget) whose queryset excludes the instance being edited (per Decision 9 above) and is ordered by `name`. Views `system_create` (route `/systems/new/`, name `fmea:system_create`) and `system_edit` (route `/systems/<stable_id>/edit/`, name `fmea:system_edit`), following this app's existing create/edit view pattern (find and match the pattern used by, e.g., the `Process` or `Product` create/edit views — same redirect-on-success-to-detail-page convention, same template-reuse-vs-separate-template convention, whichever this app already does).
6. **Add `system` field to the existing `Product` and `Process` forms.** Locate `ProductForm`/`ProcessForm` (or wherever these are constructed — check `forms.py` first; if built inline in `views.py` instead, add it there) and add one new optional field: `system = forms.ModelChoiceField(queryset=System.objects.all().order_by("name"), required=False)` (or the `ModelForm` `Meta.fields` equivalent if these are `ModelForm`s — add `"system"` to `Meta.fields` and it is optional automatically since the model field is `null=True, blank=True`). Do not change any other field, label, widget, or validation already on these forms. Verify the existing `Product`/`Process` create and edit views already save via `form.save()` (the common case) so the new field persists with no further view change — if either view does something more manual with `cleaned_data`, add the one corresponding line to persist `system` there too.
7. **New sidebar entry.** In `_sidebar.html`, under the existing `CONTEXT` group (which already has "Engineering Context" and "Process Characteristics"), add one new `<a class="nav-link">` for "System / Product / Process" linking to `{% url 'fmea:system_list' %}`. No new group, no reordering of the existing two links — append the new one.

## 2. Exact Allowed / New Files

```text
django_app/fmea_app/models.py                              # new System model; add system FK to Product, Process
django_app/fmea_app/migrations/000X_....py                 # new — additive only
django_app/fmea_app/views.py                                # new system_list, system_detail, system_create, system_edit views
django_app/fmea_app/urls.py                                 # new routes
django_app/fmea_app/forms.py                                # new SystemForm; extend existing Product/Process forms with system field
django_app/fmea_app/templates/fmea_app/system_list.html     # new
django_app/fmea_app/templates/fmea_app/system_detail.html   # new
django_app/fmea_app/templates/fmea_app/system_form.html     # new (create/edit form template — reuse this app's existing form-template pattern; if this app instead reuses one shared generic form template across models, reuse that pattern here too rather than inventing a new convention)
django_app/fmea_app/templates/fmea_app/_sidebar.html         # add the one new link under CONTEXT

tests/test_system_product_process.py                        # new
```

Nothing else. In particular: no changes to `fmea_detail.html`, `engineering_context.html`, `process_flow.html`, `dfmea_worksheet.html`/`pfmea_worksheet.html`, or any Risk Matrix template — this slice adds an optional field these pages don't need to display, and none of them are required to change to keep rendering existing (System-less) data correctly.

## 3. Required Validation and Explicit Exclusions

- No `System Characteristics Base` content of any kind (no characteristic-count-by-System, no "linked to FMEA" characteristic rollups) — that is Slice M, gated on this slice, not built here.
- No `ClassificationScheme`/`ClassificationTerm` — no Type/Category/Importance/Monitoring-status field or column anywhere on `System` or its pages.
- No Characteristics Flow diagram, no relationship/edge entity.
- No chart/graph/canvas rendering of the hierarchy anywhere — `system_list.html` and `system_detail.html` are plain HTML tables/lists only. Confirm neither template contains `<canvas` or any charting-library reference.
- No `FMEA.system` field, column, or migration anywhere.
- No backfill migration, no default/"Unassigned" `System` row created anywhere, no change to any existing `Product`/`Process` row's data.
- Every internal link uses `{% url %}` — no hardcoded paths, no dead anchors. `fmea:system_detail` links resolve by `stable_id`, matching this app's existing detail-route convention (e.g. `fmea:fmea_detail`).
- `_sidebar.html` diff is exactly one new `<a class="nav-link">` line under the existing `CONTEXT` group — the group header, its two existing links, and every other group stay exactly as Slice C left them.
- `Product`/`Process` form diffs add exactly one new field each (`system`) — no other field, label, widget, queryset, or validation on either form changes.
- `manage.py makemigrations --check --dry-run` shows zero additional pending migrations beyond the one(s) this slice adds and commits.

## 4. Required Tests

`tests/test_system_product_process.py`:

- Render `/systems/` with fixture data (at least: two root Systems, one child System under one of them, some Products/Processes assigned to Systems and some not) and assert each System row shows the correct name, code, status, parent (name or "—" for root), and correct Product/Process counts.
- Render `/systems/<stable_id>/` for a System with linked Products, linked Processes, and a child System, and assert all three lists render with correct fields and each Product/Process row links to the correct `fmea:fmea_detail` URL for its owning FMEA, and the child System links to its own `fmea:system_detail`.
- Assert the `System` create form rejects (or the view prevents) setting a System as its own parent — post an edit with `parent` set to the instance's own id/stable_id and assert it is rejected (form invalid, or the choice is simply not offered/not accepted).
- Assert the `Product` and `Process` create/edit forms now render an optional `system` field, and that submitting a value for it persists the FK correctly (reload the saved object and check `.system_id`).
- Assert existing Product/Process rows with no `System` assigned still render correctly with no error, everywhere they already appear — Engineering Context (`/context/`), the `fmea_detail` worksheet, and `/systems/` itself (showing "—" or blank for their Parent-equivalent, i.e. no System assigned) — a regression check, not new functionality.
- Assert `_sidebar.html` contains a "System / Product / Process" link under the `CONTEXT` group, resolving to `fmea:system_list`.

Full existing suite re-run with no unrelated assertion changes.

## 5. Commands to Run

```powershell
python -B manage.py check
python -B manage.py makemigrations --check --dry-run
python -B -m pytest
```

## 6. Acceptance Criteria

1. `/systems/` renders a flat, correctly-sorted list of all Systems with correct name/code/status/parent and correct computed Product/Process counts.
2. `/systems/<stable_id>/` renders one System's own fields plus its linked Products, linked Processes, and child Systems, each linking correctly.
3. The `System` create/edit form works, and rejects a System being set as its own parent.
4. The existing `Product` and `Process` create/edit forms gain the new optional `system` field, and it persists correctly, with no other change to either form.
5. No unrelated model/migration/template changes anywhere in the diff; `_sidebar.html` diff is exactly the one new link.
6. Existing Product/Process rows with no System assigned continue to render correctly everywhere in the app — no regression.
7. Full test suite passes, `manage.py check` is clean, and `makemigrations --check --dry-run` shows no unexpected pending migrations.
8. Mirrored into `open_fmea_training_set` per the standing discipline (byte-diffed, not just size/mtime).

## 7. Explicit Exclusions (restated for emphasis)

No `System Characteristics Base` content (Slice M, which depends on this slice, is not started here). No `ClassificationScheme`/`ClassificationTerm`. No Characteristics Flow diagram or relationship/edge entity. No chart/graph rendering of the hierarchy — a plain list/table is sufficient for this increment. No direct `FMEA.system` link — `FMEA` reaches `System` only indirectly through its Products/Processes. No forced backfill of existing Products/Processes — `system` stays nullable indefinitely and no existing row is touched. No full cycle-detection beyond the simple self-parent check described in Decision 9. If any of this seems to need changing to deliver a working slice, stop and report — do not silently expand scope.
