# Codex Implementation Instruction — Slice P: Product Characteristic Register (New Standalone Read-Only Page)

Status: **Instruction, 2026-09-06** — implements `OpenFMEA_ProductCharacteristicRegisterPage_ArchitectureDecision.md` exactly as decided there. Do not add, reinterpret, or "improve" anything beyond what is written below; if something here seems to conflict with the live code, stop and report back rather than guessing. **This page is strictly read-only — the single most important constraint in this instruction.**

## 0. Decisions for this slice (restated from the architecture decision doc — do not re-derive)

1. New standalone page (new route, new view, new template) — there is no existing `ProductCharacteristic` list/detail page to extend.
2. Table columns: ID, Characteristic, Category (`primary_classification.name` or "Unclassified"), System/Product (derived via `requirement.function.product` or `requirement.function.operation.process`, rendered as the resolved name or an explicit "—" when the chain dead-ends anywhere), Links (`CharacteristicLink` count, either direction), Status (rendered as "Special"/"Standard" from the real `is_special` boolean — **not** a fabricated lifecycle status).
3. Four KPI tiles: Total, Special Characteristics (`is_special=True`), Unclassified (`primary_classification` null), Linked (`Links > 0`). **No "Monitoring Status" tile** — no field anywhere supports it.
4. Three filters: `classification`, `is_special`, `system` (the `system` filter uses a real queryset `Q` filter across the derived FK chain, not a post-hoc Python filter over an unbounded queryset). Plain GET-form reload.
5. Right-docked read-only detail panel: `?selected=<stable_id>&tab=general|classification|links`. The Links tab links out to the existing `characteristic_link_list`/detail machinery rather than duplicating link-editing controls.
6. Bottom Coverage Summary panel: three plain counts (unclassified, unlinked, no-resolved-System/Product-chain) over the filtered set. No composite score.
7. **No create, edit, or delete capability anywhere on this page for `ProductCharacteristic`.** No form, no POST-handling view, no "Add Characteristic"/"Edit"/"Delete" control of any kind.

## 1. Exact Scope

Create:
- One new view function in `django_app/fmea_app/views.py` (name it consistently with this app's existing conventions, e.g. `product_characteristic_list`) — GET only. Do not add a POST branch, do not add `@require_POST` anywhere in this view, do not import or reference a form for this model.
- One new template, `django_app/fmea_app/templates/fmea_app/product_characteristic_list.html`, extending the same `base.html` every other list page extends.
- One new route in `django_app/fmea_app/urls.py`, e.g. `path("product-characteristics/", views.product_characteristic_list, name="product_characteristic_list")`. Exactly one route — no separate detail-page route; the detail panel is a `?selected=` GET param on this same route, per Decision 5.

Modify:
- `django_app/fmea_app/templates/fmea_app/_sidebar.html` — add exactly one new nav link to this new page, in whichever existing nav group already holds the other FMEA-elements standalone pages (Failure Modes, Causes, Effects, etc., from Slice G) — do not create a new nav group for one link.
- `django_app/fmea_app/static/fmea_app/css/*.css` — additive classes only, if any new visual pattern is needed beyond what `.stat-tile`/`.panel`/`.grid`/`.table-shell` already provide.

Do not touch: `models.py` (no migration — every value used already exists), `forms.py` (do not add a `ProductCharacteristicForm`), `system_list`/`system_detail` (Slice E), `characteristic_link_list`/`_create`/`_delete` (Slice L) beyond linking to them, any `ClassificationScheme`/`ClassificationTerm` view (Slice M), `app.js`.

## 2. Exact Allowed-New Files

- `django_app/fmea_app/templates/fmea_app/product_characteristic_list.html` — the only new file. The view function and route are additions to existing files (`views.py`, `urls.py`), not new files.

## 3. Required Validation and Explicit Exclusions

- **Grep the finished diff for any of**: `ProductCharacteristicForm`, a `product_characteristic_create`/`_edit`/`_delete` function name, a `<form method="post"` inside the new template, an `@require_POST` decorator anywhere touching this model, an `<a>`/`<button>` labeled Add/Edit/Delete/New in the new template. **Any match is a defect — this page must ship with zero of them.**
- The System/Product derived-chain column and filter must be implemented as a single real queryset expression (annotate/filter via the actual FK path), not a Python loop that manually walks `.function.product`/`.function.operation.process` per row after fetching — use `select_related`/`Q` so the page doesn't do a query per row.
- The System/Product column must render an explicit "—" (or equivalently explicit placeholder) when the chain dead-ends at any hop — grep to confirm this isn't rendered as an empty string indistinguishable from a real-but-blank value.
- "Status" must render from `is_special` only ("Special"/"Standard" or equivalent) — grep to confirm no new field, migration, or hardcoded per-row lifecycle string was introduced.
- The Links column/count and the detail panel's Links tab must use the same query shape `characteristic_link_list` (`views.py:1472`) already uses for its `characteristic` filter (`Q(from_characteristic__pk=...) | Q(to_characteristic__pk=...)`) — reuse it, don't reimplement it differently.
- `?selected=` on a nonexistent id must not 500 (graceful response, consistent with Slices N/O's equivalent handling). `?tab=` defaults to `general` for missing/unrecognized values.
- No AJAX/`fetch`/`XMLHttpRequest`, no client-side tab framework.
- No new CDN reference, no new charting library (this page has no chart per the decision doc — confirm none was added speculatively).

## 4. Required Tests

Add a new test module (or extend the existing `fmea_app` test file covering Slice G/L/M's standalone pages, whichever this project's convention prefers — check first, follow existing convention):
1. Table renders real `ProductCharacteristic` rows with correct Category/Links/Status values for a small fixed fixture set, including at least one row with `primary_classification=None` (renders "Unclassified") and one with `is_special=True` (renders "Special").
2. System/Product column: one characteristic whose chain fully resolves (`requirement→function→product→system`), one whose chain dead-ends partway (e.g. `function.product` is null and `function.operation` is also null), and one with `requirement=None` — assert the first renders the resolved name and the other two render the explicit dead-end placeholder, not a blank cell and not a 500.
3. KPI tiles: assert Total/Special/Unclassified/Linked counts match a known fixture set exactly.
4. Filters: `classification`, `is_special`, and `system` each narrow the rendered rows correctly; the `system` filter specifically must correctly match a characteristic via the Process-side chain (`function.operation.process.system`) as well as the Product-side chain (`function.product.system`).
5. **Negative test, required**: POST to the new route (and to `?selected=<id>` with a POST) returns 405 or is otherwise rejected — not a silent no-op that could be mistaken for a working write. If the view is written GET-only via Django's normal dispatch, a POST naturally 405s; assert that explicitly rather than assuming it.
6. Full existing test suite for this app still passes (regression).

## 5. Commands to Run

```
python manage.py test fmea_app
```
Run in both `open_fmea` and `open_fmea_training_set` per this project's established practice; report the exact before/after test count.

## 6. Acceptance Criteria

- All new tests from Section 4 pass, including the required negative (read-only) test; full existing suite still passes with no regressions; report the exact before/after test count.
- `git diff` touches exactly: one new template, `views.py` (one new function), `urls.py` (one new route line), `_sidebar.html` (one new link), and the test file — nothing else, no migration.
- The completion report explicitly confirms, by grep, the absence of every item listed in Section 3's first bullet.

## 7. Explicit Exclusions (restated)

No create/edit/delete for `ProductCharacteristic` anywhere — no form, no POST view, no UI control. No new migration. No fabricated "Monitoring Status" or lifecycle field. No composite coverage score. No AJAX or client-side tab-swap. No new charting library. No changes to `system_list`/`system_detail`, `characteristic_link_list`/`_create`/`_delete`, or any `ClassificationScheme`/`ClassificationTerm` view beyond linking out to them. No new nav group in the sidebar — one link into the existing FMEA-elements group.
