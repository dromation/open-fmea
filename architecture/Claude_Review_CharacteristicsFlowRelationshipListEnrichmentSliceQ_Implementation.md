# Claude Review — Slice Q: Characteristics Flow Relationship List Enrichment — Implementation

Status: **Implemented and independently verified, 2026-09-12.** Implements `Codex_Instruction_CharacteristicsFlowRelationshipListEnrichment_SliceQ.md` exactly as decided in `OpenFMEA_CharacteristicsFlowRelationshipListEnrichment_ArchitectureDecision.md`. Mirrored byte-identically into `open_fmea_training_set`. **This closes only the list-based half of Mockup 9 — see Section 6.**

## 1. What was built

Pure extension of the existing `characteristic_link_list` route/view/template — no new route, no new model, no new stylesheet.

1. **Three new GET-form filters**: `category` (the real `ClassificationTerm`s), `system` (via the same doubly-nullable `requirement→function→product|operation.process→system` chain Slice P used, real `Q` filter, not a Python loop), `view` (`all`/`linked-only`/`unlinked-only`).
2. **One shared definition of Linked/Unlinked**: a single annotated `ProductCharacteristic` queryset (`outgoing_link_count`/`incoming_link_count` via `Count(..., distinct=True)`) computes `links_count` once per characteristic; this same value drives the `view` filter, the Coverage Summary's Linked/Unlinked counts, and the Unlinked Characteristics panel — never redefined three ways.
3. **`category`/`system` scope the Links table** by restricting to links where either endpoint falls in the category/system-filtered characteristic set (`Q(from_characteristic__pk__in=...) | Q(to_characteristic__pk__in=...)`) — reusing the same Q-shape idiom `characteristic_link_list` already used for its own `characteristic` filter. `view` does not re-scope the Links table (a link inherently connects two "linked" characteristics, so "unlinked-only" has no meaningful Links-table row to show); it scopes the Coverage Summary and Unlinked Characteristics panel instead.
4. **Right-docked detail panel**: `?selected=<stable_id>` (no tabs — the decision doc's Decision 3 only calls for two plain lists). **Incoming** = `CharacteristicLink.objects.filter(to_characteristic=selected)`; **Outgoing** = `CharacteristicLink.objects.filter(from_characteristic=selected)` — each queried directly by the model's real FK, never inferred. `?selected=` on a nonexistent id 404s via `get_object_or_404` (not a 500), matching Slices N/O/P's convention.
5. **Category/Special badges** next to every characteristic name (Links table rows, Unlinked Characteristics panel, detail panel heading): `primary_classification.name` or "Unclassified", plus a "Special" marker when `is_special=True`. **No new CSS was needed** — the existing generic `.status` pill (neutral, already used for plain informational badges elsewhere) renders the category name, and `.status.status-active` (Slice O's "Yes"/active convention) renders the "Special" marker.
6. **Coverage Summary panel**: four plain counts (Total in View, Linked, Unlinked, Total Links) over the `category`+`system`+`view`-filtered characteristic set.
7. **Unlinked Characteristics panel**: the real zero-link `ProductCharacteristic` rows from that same filtered set, each linking to `product_characteristic_list?selected=<stable_id>` (Slice P's page) — not duplicating Slice P's own panel.
8. **Relationship Type legend**: the six real `RELATIONSHIP_TYPE_CHOICES` labels, reusing the `relationship_type_choices` context variable already passed to the template — no new context, no symbol/status legend.

## 2. Required tests (Section 4) — added to the existing test module

Located `tests/test_characteristic_link.py` (the module already covering `characteristic_link_list`) and added `CharacteristicLinkListEnrichmentTests` (11 new test methods) alongside the existing `CharacteristicLinkTests` class, unchanged:

1. `test_category_filter_narrows_links_and_unlinked_panel` — a fixture where `category=Safety` scopes to characteristics `p`/`q`/`u`/`w`; asserts the Links table (via `response.context["links"]`) includes the link touching `p`/`q` and the link touching `w`/`p`, excludes the Legal-only `r`/`s` link, and the Unlinked panel narrows to just `u`.
2. `test_system_filter_matches_via_product_chain`, `test_system_filter_matches_via_process_chain` — `system` filtered via the Product-side chain (`p`/`q` → System A) and the Process-side chain (`r`/`s` → System B) independently, each excluding the other pair's link.
3. `test_view_filter_unlinked_only_narrows_coverage_and_panel`, `test_view_filter_linked_only_narrows_coverage_and_panel` — both `view` values narrow Coverage Summary and the Unlinked panel to the exact expected characteristic sets.
4. `test_coverage_summary_and_unlinked_panel_match_known_fixture` — an 8-characteristic, 3-link fixture (`p,q,r,s,w` linked; `t,u,v` unlinked) asserts Total=8/Linked=5/Unlinked=3/Total Links=3 exactly, and that every Unlinked-panel row links to the correct `product_characteristic_list?selected=` URL.
5. `test_detail_panel_incoming_and_outgoing_do_not_mix` — characteristic `p` has one outgoing link (to `q`) and one incoming link (from `w`); asserts the Incoming list contains only `w` and the Outgoing list contains only `q`.
6. `test_detail_panel_invalid_selected_returns_404_not_500` — the required graceful-failure path.
7. `test_category_and_special_badges_render_real_facts` — "Unclassified" (characteristic `t`), "Special" (characteristic `w`), "Safety", "Legal" all render.
8. `test_no_status_field_on_characteristic_link` — `CharacteristicLink._meta.get_fields()` asserted not to contain `status`.
9. `test_no_ai_suggestion_or_diagram_content_added` — extends the existing exclusion-style test with `confirmed`/`suggested`/`Confirmed`/`Suggested`/`Possible Link`/`confidence` (in addition to the pre-existing `<canvas`/`Auto Link` checks already covered by `test_pages_have_no_ai_graph_or_extra_tab_content`, left unchanged).

The pre-existing `CharacteristicLinkTests` class (7 tests: list rendering, `relationship_type` filter, `characteristic` filter, create, delete, no-scope-creep, sidebar link) was **not modified** and still passes unchanged — confirming `characteristic_link_create`/`characteristic_link_delete` behavior is unaffected by this slice.

## 3. Test count

**242 → 253 (+11)**, run via `pytest`:

```
253 passed in 11.95s
```

`python manage.py makemigrations --check --dry-run` → **"No changes detected"** — `models.py` untouched.

## 4. Exclusions grep-verified (Section 3), not asserted from memory

| Exclusion | Verified |
|---|---|
| No new migration file | `migrations/` still ends at `0013_characteristiclink.py` |
| No `<canvas>`, no SVG node-link rendering, no new JS graph/diagram library, no new CDN `<script src="https://...">` | grep across the template — no matches |
| No `status` field/column on `CharacteristicLink` | grep of the model class body — no matches; also asserted by test |
| No "confirmed"/"suggested"/"possible link" text or logic in the new template/view code | grep of `views.py` + the template — the one incidental match (`record.suggested_domain_type` at `views.py:1415`) is a pre-existing, unrelated ingestion field, not part of this diff |
| No AI/ML/scoring import or function | grep — no matches |
| No new `ClassificationScheme`/`ClassificationTerm` rows via migration or seed command | grep of `views.py`/management commands for `.objects.create(` on these models — no matches outside the test fixture itself |
| No session/cookie/request-scoped "current context" state | grep for `request.session`/`set_cookie`/`request.COOKIES` in `views.py` — no matches near this view |

## 5. Diff footprint

Matches the acceptance criterion exactly:
- `django_app/fmea_app/views.py` — `characteristic_link_list` extended only; `characteristic_link_create`, `characteristic_link_delete`, and `product_characteristic_list` (Slice P) confirmed unchanged, same line numbers as before this slice.
- `django_app/fmea_app/templates/fmea_app/characteristic_link_list.html` — the one template extended.
- `tests/test_characteristic_link.py` — the existing test module extended (no new test file).
- No changes to `urls.py`, `models.py`, `forms.py`, `characteristic_link_form.html`, `product_characteristic_list.html` (beyond being a link target from the Unlinked panel), `_sidebar.html`, `app.js`, or any CSS file (no new visual pattern was needed beyond `.status`/`.split`/`.detail-panel`/`.related-list`, all already additive from Slices N/O/P).

## 6. Mirroring

Both repositories' `views.py` were confirmed at matching byte size (72523) and mtime before writing, `characteristic_link_list.html` and `test_characteristic_link.py` written fresh over their pre-change versions. Written from identical source bytes (same `SendUserFile` `file_uuid`s committed to both device paths), each pre-existing file's write pinned with `expectedMtimeMs` read moments earlier. Both commits succeeded with zero rejections.

## 7. What remains explicitly not built (per Section 6's requirement)

The node-link diagram and the AI-suggestion capability **remain not built** — this slice closes out only the list-based half of Mockup 9 (Decisions 1–6 of the architecture decision doc), not the whole mockup. Two standing decisions still block the rest, named explicitly so this is never mistaken for closing out Mockup 9 in full:

1. **Graph-rendering library/approach choice** — which technology would render the actual node-link diagram (canvas, nodes, direction arrows, zoom/pan, visual selection-highlighting). Not chosen or approximated here.
2. **AI auto-link human-review-gate design** — how a machine-suggested link would be scored, presented, and gated through human review before becoming a real `CharacteristicLink` row (including whether/how a `status` field would need to be added to the model). Not proposed or assumed here.

## 8. Recommendation

Slice Q is complete and ready to stand as-is. This concludes the currently-approved, not-yet-built queue (Slices N, O, P, Q) — all four are now implemented, tested, and mirrored. Mockup 3 (PM-FMEA) remains on its separate standing hold, untouched by this session. The two decisions in Section 7 above are the next open items if the user wants to pursue the diagram/AI half of Mockup 9.
