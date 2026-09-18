# Claude Review — Slice P: Product Characteristic Register (New Standalone Read-Only Page) — Implementation

Status: **Implemented and independently verified, 2026-09-12.** Implements `Codex_Instruction_ProductCharacteristicRegisterPage_SliceP.md` exactly as decided in `OpenFMEA_ProductCharacteristicRegisterPage_ArchitectureDecision.md`. Mirrored byte-identically into `open_fmea_training_set`.

## 1. What was built

A wholly new standalone page — new route, new view, new template — since no `ProductCharacteristic` list/detail page existed before this slice.

1. **Table (four columns per Decision 1)**: ID (`stable_id`), Characteristic (`name`), Category (`primary_classification.name` or "Unclassified"), System/Product (derived chain, see below), Links (`CharacteristicLink` count either direction), Status ("Special"/"Standard" from the real `is_special` boolean only).
2. **System/Product derivation** (`_system_product_label()`): walks `requirement.function.product` first — if it resolves, renders `product.system.name` when the product itself has a `System`, else falls back to `product.name`; otherwise walks `requirement.function.operation.process` the same way (`process.system.name`, else `process.name`); renders the explicit "—" placeholder when the chain dead-ends at `requirement`, `function`, or both `product`/`operation` being unset. Implemented as a single annotated/`select_related` queryset (see Section 3) with all seven FK hops pre-fetched — no per-row query.
3. **Four KPI tiles**: Total, Special Characteristics (`is_special=True`), Unclassified (`primary_classification` null), Linked (`Links > 0`). No "Monitoring Status" tile, matching Decision 2's explicit decline.
4. **Three filters**: `classification` (by `ClassificationTerm.stable_id` — the app's dominant convention; no conflicting precedent exists for this filter), `is_special` (yes/no), `system` (by `System.stable_id`, matched via a real `Q` filter across both the Product-side and Process-side FK chains in one queryset expression — no Python loop).
5. **Right-docked read-only detail panel**: `?selected=<stable_id>&tab=general|classification|links` on the same route. General shows name/description/is_special/system-product label; Classification shows the real `primary_classification` and its parent `ClassificationScheme`; Links lists the real `CharacteristicLink` rows (both directions, same query shape as `characteristic_link_list`) and links out to `characteristic_link_list?characteristic=<pk>` rather than duplicating link-editing controls.
6. **Coverage Summary panel**: three plain counts (unclassified, unlinked, no-resolved-chain) over the filtered set — no composite score.
7. **Zero create/edit/delete surface**: no form, no POST-handling branch, no Add/Edit/Delete/New control anywhere. The view is decorated `@require_GET` (a new but narrow addition — enforces the read-only constraint at the framework level rather than leaving POST silently accepted-but-ignored, which the instruction's own required negative test implies is not acceptable). This is the one deliberate implementation choice beyond a literal reading of the instruction, called out explicitly here per the "stop and report" discipline; it adds no form, no POST branch, and no `@require_POST` — it only rejects POST outright.

No `theme.css` changes were needed — Slice N's `.detail-panel`/`.tab-nav`/`.tab-link`/`.row-selected`/`.related-list` classes were reused as-is, matching the instruction's "additive classes only, if any new visual pattern is needed" clause (none was).

## 2. Required tests (Section 4) — new dedicated test file, per project convention

Checked candidate files first, per the instruction's explicit requirement: `test_characteristic_link.py` and `test_fmea_elements_standalone_pages.py` are each a dedicated file for one standalone page's own view, not a shared catch-all; `test_classification_scheme.py` covers `ClassificationScheme`/`ClassificationTerm` model behavior, not a list-page view. Since this page has no pre-existing test module (it didn't exist before this slice, unlike Slices N/O which extended existing pages), the established convention is a new dedicated file — created `tests/test_product_characteristic_register.py` (`ProductCharacteristicRegisterPageTests`, 15 test methods):

1. `test_table_renders_category_links_and_status_values` — a small fixed fixture set with one `is_special=True` row, one unclassified row, real Category/Status text asserted.
2. `test_system_product_column_renders_resolved_name_or_dead_end_placeholder` — one characteristic resolving fully via `requirement→function→product→system` ("Optical System"), one via `requirement→function→operation→process→system` ("Weld System"), one dead-ending at an unset `function.product`/`function.operation`, one with `requirement=None` — asserts the resolved names render and at least two dead-end placeholders render, with a 200 status (not a 500).
3. `test_kpi_tiles_match_expected_counts` — Total=4, Special=1, Unclassified=2, Linked=2 against the fixture set, read directly from `response.context`.
4. `test_coverage_summary_matches_kpi_derived_facts` — the three Coverage Summary counts asserted against the same fixture-derived facts.
5. `test_classification_filter_narrows_rows`, `test_is_special_filter_narrows_rows`, `test_system_filter_matches_via_product_chain`, `test_system_filter_matches_via_process_chain` — each filter narrows correctly; the `system` filter specifically verified via both the Product-side and the Process-side chain, per Section 4 item 4's explicit requirement.
6. `test_links_tab_links_out_to_characteristics_flow_without_duplicating_controls` — asserts the exact `characteristic_link_list?characteristic=<pk>` href is present and no "New Link" control leaks into this page.
7. `test_unrecognized_tab_defaults_to_general_without_500`, `test_invalid_selected_id_returns_404_not_500` — the two required graceful-failure paths (same convention as Slices N/O).
8. `test_post_to_list_and_selected_are_rejected_not_silently_accepted` — **the mandatory negative test**: POST to the bare route and to `?selected=<id>` both assert `405`.
9. `test_page_has_no_create_edit_delete_controls`, `test_no_speculative_chart_or_ajax_content` — grep-style in-response assertions for every Section 3 exclusion.
10. `test_sidebar_has_a_real_working_product_characteristics_link` — the one new nav link renders and points at the real route.

## 3. Test count

**227 → 242 (+15)**, run via `pytest` (this project's established runner):

```
242 passed in 11.59s
```

`python manage.py makemigrations --check --dry-run` → **"No changes detected"** — `models.py` untouched.

## 4. Exclusions grep-verified (Section 3), not asserted from memory

| Exclusion | Verified |
|---|---|
| `ProductCharacteristicForm` anywhere | grep across `django_app/fmea_app/` — no matches |
| `product_characteristic_create`/`_edit`/`_delete` function names | grep `views.py` — no matches |
| `<form method="post"` in the new template | grep — no matches |
| `@require_POST` touching this model | grep — no matches (the view uses `@require_GET` instead, a narrower, additive guard — see Section 1 item 7) |
| Add/Edit/Delete/New labeled control in the new template | grep — no matches |
| Exactly zero `<canvas>` (no chart per the decision doc) | `grep -c "<canvas"` → 0 |
| No AJAX/fetch/XHR | grep — no matches |
| No new CDN `<script src="http...">` | grep — no matches |
| No migration | `migrations/` still ends at `0013_characteristiclink.py` |

## 5. Diff footprint

Matches the acceptance criterion exactly:
- `django_app/fmea_app/views.py` — one new helper (`_system_product_label`), one new view (`product_characteristic_list`), one import-line addition (`require_GET`); no other function's body touched (spot-checked: `system_list`, `system_detail`, `characteristic_link_list`, `characteristic_link_create`, `characteristic_link_delete` all confirmed unchanged, same line numbers as before this slice).
- `django_app/fmea_app/urls.py` — one new route line.
- `django_app/fmea_app/templates/fmea_app/_sidebar.html` — one new nav link, inside the existing "FMEA ELEMENTS" group (no new group).
- `django_app/fmea_app/templates/fmea_app/product_characteristic_list.html` — the one new template (only new file).
- `tests/test_product_characteristic_register.py` — the new test file.

`models.py`, `forms.py`, `system_list`/`system_detail`, `characteristic_link_list`/`_create`/`_delete`, any `ClassificationScheme`/`ClassificationTerm` view, `app.js`, and `theme.css` were not touched.

## 6. Mirroring

Both repositories' pre-change files were confirmed at matching byte sizes and mtimes before writing (`views.py` 65982 bytes, `urls.py` 5339 bytes, `_sidebar.html` 5155 bytes identical on both). Written from identical source bytes (same `SendUserFile` `file_uuid`s committed to both device paths), each pre-existing file's write pinned with `expectedMtimeMs` read moments earlier. Both commits succeeded with zero rejections.

## 7. Recommendation

Slice P is complete and ready to stand as-is. Next in the approved, not-yet-built queue: **Slice Q** (Characteristics Flow Relationship List Enrichment), which depends on this slice's new page (it links out to `product_characteristic_list?selected=`).
