# Codex Implementation Instruction — Slice Q: Characteristics Flow Relationship List Enrichment

Status: **Instruction, 2026-09-10** — implements `OpenFMEA_CharacteristicsFlowRelationshipListEnrichment_ArchitectureDecision.md` exactly as decided there. Do not add, reinterpret, or "improve" anything beyond what is written below; if something here seems to conflict with the live code, stop and report back rather than guessing. **This is a list-page enrichment, not a diagram — do not attempt any graph/canvas rendering, and do not add an AI suggestion feature. Both are explicitly out of scope, per the decision doc.**

## 0. Decisions for this slice (restated from the architecture decision doc — do not re-derive)

1. Extend the existing `characteristic_link_list` route/view/template only. No new route, no charting/graph library, no AI.
2. Filter row gets three new GET-form fields: `category` (the four real `ClassificationTerm`s), `system` (via the same doubly-nullable chain Slice P used), `view` (`all`/`linked-only`/`unlinked-only`). Plain server-side reload.
3. Right-docked detail panel via `?selected=<stable_id>` on the same route: real Incoming (`to_characteristic=selected`) and Outgoing (`from_characteristic=selected`) lists, each showing the other characteristic, `relationship_type`, `strength`. No "Possible Links" section, no "Status" field on the characteristic.
4. Category/Special badge next to each characteristic's name (list rows and detail panel): real `primary_classification.name` (or "Unclassified") + a "Special" marker when `is_special=True`. Additive CSS only.
5. Coverage Summary panel (plain counts: total in view, linked, unlinked, total links) + Unlinked Characteristics panel (real `ProductCharacteristic` rows with zero `CharacteristicLink` rows either direction, linking out to `product_characteristic_list?selected=`).
6. Relationship Type legend: the six real `relationship_type` choices only. No symbol/category legend beyond category badge (Decision 4). No "confirmed vs. suggested" line anywhere.
7. **Explicitly forbidden in this diff**: any canvas/SVG/node-link graph rendering; any new charting/graph JS library or CDN reference; any `status`/"confirmed"/"suggested" field or column on `CharacteristicLink`; any AI/scoring/suggestion logic; any new `ClassificationScheme`/`ClassificationTerm` seed rows; any persistent Project/System "context" (session/cookie/user-state) mechanism.

## 1. Exact Scope

Modify only:
- `django_app/fmea_app/views.py` — extend the existing `characteristic_link_list` view function only. Do not touch `characteristic_link_create`, `characteristic_link_delete`, or `product_characteristic_list` (Slice P) beyond adding a link/href into it from the new Unlinked Characteristics panel.
- `django_app/fmea_app/templates/fmea_app/characteristic_link_list.html` — extend this one template only.
- `django_app/fmea_app/static/fmea_app/css/*.css` (locate the file already holding `.stat-tile`/`.panel`/`.grid`/`.table-shell` etc. — do not create a new stylesheet) — additive classes only (the category/special badge).

Do not touch: `urls.py` (no new route), `models.py` (no migration — every value used already exists on `CharacteristicLink`, `ProductCharacteristic`, `ClassificationTerm`, `System`), `forms.py`, `characteristic_link_form.html`, `product_characteristic_list.html` beyond being a link target, `_sidebar.html`, `app.js`.

## 2. Exact Allowed-New Files

None. Pure extension of the view, one template, and the existing stylesheet.

## 3. Required Validation and Explicit Exclusions

- The `system` filter must use a real queryset `Q` filter across the same FK chain Slice P used (`requirement__function__product__system` / `requirement__function__operation__process__system`) — not a per-row Python filter.
- "Linked"/"Unlinked" must be computed consistently everywhere it's used (the `view` filter, the Coverage Summary counts, and the Unlinked Characteristics panel) — one query shape reused, not three independently-written definitions that could disagree.
- Incoming and Outgoing lists in the detail panel must query `CharacteristicLink` directly by `to_characteristic`/`from_characteristic` — do not introduce any notion of implied/inferred direction beyond the model's real FKs.
- `?selected=` on a nonexistent id must not 500 (graceful response, consistent with Slices N/O/P's equivalent handling).
- Explicit exclusions to verify absent from the diff by name/grep before calling this done:
  - No new migration file.
  - No `<canvas>`, no SVG node-link rendering, no new JS graph/diagram library, no new CDN `<script src="https://...">` tag.
  - No `status` field or column added to `CharacteristicLink` (migrations and model diff both checked).
  - No "confirmed"/"suggested"/"possible link" text or logic anywhere in the new template or view code.
  - No AI/ML/scoring import or function.
  - No new `ClassificationScheme`/`ClassificationTerm` rows added via migration or seed command.
  - No session/cookie/request-scoped "current context" state — every filter is a GET param, nothing persisted server-side between requests.

## 4. Required Tests

Add to the existing test module covering `characteristic_link_list` (locate it — do not create a new test file):
1. Filters: seed characteristics with known categories/systems/link states; assert `category`, `system`, and `view` (`linked-only`/`unlinked-only`) each narrow the rendered rows correctly, and that `system` correctly matches via both the Product-side and Process-side chain (mirroring Slice P's equivalent test).
2. Detail panel: `?selected=<id>` with at least one incoming and one outgoing link renders both lists correctly and does not mix them up (an incoming link must not appear in the Outgoing list and vice versa); an invalid `selected` value does not 500.
3. Coverage Summary + Unlinked Characteristics: seed a known set of characteristics with and without links; assert the counts match exactly and the Unlinked Characteristics panel lists exactly the zero-link ones, each linking to the correct `product_characteristic_list?selected=` URL.
4. Category/Special badge: a characteristic with `primary_classification=None` renders "Unclassified"; one with `is_special=True` renders the Special marker.
5. Negative/regression: grep-based or explicit assertion that no `status` field exists on `CharacteristicLink` post-migration-check (`makemigrations --check --dry-run` reports no changes), and that the existing `characteristic_link_create`/`_delete` behavior is unchanged.
6. Full existing test suite for this app still passes (regression) — run it, do not just add these five.

## 5. Commands to Run

```
python manage.py test fmea_app
```
Run in both `open_fmea` and `open_fmea_training_set` per this project's established practice for prior slices; report the exact before/after test count in the completion report.

## 6. Acceptance Criteria

- All new tests from Section 4 pass; full existing suite still passes with no regressions; report the exact before/after test count.
- `git diff` touches only the view, the one template, the existing stylesheet, and the test file — no migration, no new route, no new model.
- Every item in Section 3's exclusion list is confirmed absent by direct grep in the completion report, not just asserted from memory.
- The completion report explicitly states that the node-link diagram and AI-suggestion capability remain not built, and names the two still-unmade decisions that block them (graph-rendering library choice; AI auto-link review-gate design) — so this is never mistaken for having closed out the full mockup.

## 7. Explicit Exclusions (restated)

No new migration. No graph/canvas/diagram rendering of any kind, no new charting/graph library or CDN reference. No `status`/confirmed/suggested concept on `CharacteristicLink`. No AI/scoring logic. No new `ClassificationScheme`/`ClassificationTerm` seed rows. No persistent Project/System context mechanism. No changes to `characteristic_link_create`, `characteristic_link_delete`, `product_characteristic_list`'s own view logic, `urls.py`, `_sidebar.html`, or `app.js`.
