# Open-FMEA Architecture Decision — Product Characteristic Register: New Standalone Read-Only Page (Mockup 8, "System Characteristics Base")

Status: **Decision, 2026-09-06** — proposing a firm, narrow default for the user to approve or correct. This is the corrected read of Mockup 8: the user's spec for "System Characteristics Base" describes a register of **Characteristics** (`ProductCharacteristic` rows), not a register of **Systems** — the already-built `/systems/` page (Slice E) is a different thing and is not touched by this decision. This document exists because Slice M (2026-09-05) built the real, adjacent pieces (`System`, `ClassificationScheme`/`ClassificationTerm`) but never built a standalone browse page for `ProductCharacteristic` itself — confirmed absent by direct route/view grep: `django_app/fmea_app/urls.py` has no `product-characteristics/` (or similar) path, and no `product_characteristic_list` view exists anywhere in `views.py`.

## 1. What already exists, verified live

`ProductCharacteristic` (`models.py:336`): `requirement` (nullable FK to `Requirement`), `name`, `description`, `is_special` (boolean, default False), `primary_classification` (nullable FK to `ClassificationTerm`). It is reached today only through `Requirement`'s FK chain — `ProductCharacteristic.requirement.function` → `Function.product` (nullable) **or** `Function.operation` (nullable) — so a characteristic's path to a `Product`/`System` is two nullable hops deep and can legitimately dead-end at any point (a characteristic with no `requirement`, a `Requirement` whose `Function` has neither `product` nor `operation` set, or a `Product`/`Process` with no `system`). `Product.system` and `Process.system` are the only paths from either side into `System`. `ClassificationScheme`/`ClassificationTerm` (Slice M) already exist and are already FK-reachable from `ProductCharacteristic.primary_classification`. `CharacteristicLink` (Slice L) already exists, FK'd both ways to `ProductCharacteristic`, and `characteristic_link_list` already computes a filtered link list keyed by characteristic id (`views.py:1472`) — this decision reuses that same relationship, not a new one. **No standalone list/detail page for `ProductCharacteristic` exists anywhere** — this is a wholly new page, not an extension of an existing one (unlike Slices N and O).

**Finding 1, restated and directly load-bearing here:** no `ProductCharacteristicForm` exists in `forms.py` (confirmed by grep this session and in the prior verification pass) and no create/edit view exists for this model. This decision is therefore **strictly read-only** — it must not add, and must not appear to add, any create/edit/delete capability for `ProductCharacteristic`. Any future decision to build real CRUD for `Product`/`Process`/`ProductCharacteristic` is a separate, not-yet-approved future slice (already logged as an open finding in `OpenFMEA_DNA_CoreReference.md` Section 0a and the readiness tracker) — this document does not fold that decision in by the back door.

## 2. Decision 1 — table columns: ID, Characteristic, Category, System/Product, Links, Status — each mapped to a real field or an honestly-partial derived chain

- **ID** / **Characteristic**: `stable_id` / `name` — real, direct.
- **Category**: `primary_classification.name` (via the real FK into `ClassificationTerm`), or a plain "Unclassified" label when null — real, direct, already-built relationship (Slice M).
- **System/Product**: derived by walking `requirement.function.product` and, if that's null, `requirement.function.operation.process` for a Process/System path — render whichever of Product/Process/System name resolves, or an explicit "—" (not blank, not an error) when the chain dead-ends anywhere along the way. This is the one place in this slice where "real data, honestly incomplete" must be visibly incomplete rather than silently blank, given how many optional hops sit between the two models.
- **Links**: count of `CharacteristicLink` rows where this characteristic is either `from_characteristic` or `to_characteristic` — the exact same query shape `characteristic_link_list` already uses for its own `characteristic` GET filter, reused, not reinvented.
- **Status**: **there is no real status field on `ProductCharacteristic`.** Do not invent one. Propose rendering "Special" / "Standard" from the real `is_special` boolean instead of a fabricated lifecycle status — this is the one column in the mockup's spec that does not map onto an existing field as literally named, and it is named here explicitly rather than silently substituted without comment.

## 3. Decision 2 — KPI tiles: four tiles, all real; the mockup's "Monitoring Status" tile is explicitly declined

Total (`.count()`), Special Characteristics (`is_special=True` count — the one real flag this model has that resembles the mockup's emphasis on specially-controlled characteristics), Unclassified (`primary_classification` null count), Linked (per Decision 1's Links definition, `> 0`). **A "Monitoring Status" or similar operational-state tile is declined** — no field anywhere on this model or its chain represents a monitoring/control state (that concept, to the extent it's real anywhere in this app, lives on `ProcessCharacteristic.status`/`.effectiveness`, a different model covered by Slice N, not here). Naming this explicitly so it is not silently reintroduced as if it existed.

## 4. Decision 3 — filters: server-side GET form, same convention as every other list page

`classification` (dropdown of `ClassificationTerm.objects.all()`), `is_special` (yes/no), `system` (dropdown of `System.objects.all()`, filtering via the derived chain in Decision 1 — implemented as a queryset filter across the real FK path, e.g. `Q(requirement__function__product__system=...) | Q(requirement__function__operation__process__system=...)`, not a post-hoc Python filter over an unbounded queryset). Plain GET-form reload, no AJAX.

## 5. Decision 4 — right-docked detail panel: server-rendered, GET-param only, strictly read-only

`?selected=<stable_id>[&tab=general|classification|links]` on the new route. **General**: `name`, `description`, `is_special`, the derived System/Product chain from Decision 1 (rendered with the same honest "—" for a dead-end). **Classification**: the real `primary_classification` and its parent `ClassificationScheme`. **Links**: the real `CharacteristicLink` rows for this characteristic (both directions), each linking through to the existing `characteristic_link_list`/`characteristic_link_detail` machinery rather than re-rendering link edit controls here — this page never offers create/edit/delete for either `ProductCharacteristic` or `CharacteristicLink`, only links out to the pages that already do (for links) or explicitly nothing (for the characteristic itself, per Finding 1).

## 6. Decision 5 — bottom Coverage Summary panel: plain counts, same discipline as Slice O's Decision 5

How many characteristics in the filtered set are unclassified, unlinked, and have no resolved System/Product chain (a dead-end at every hop) — three plain counts, no composite score, no weighting, matching the same discipline already established for Slice O's Relationship/Coverage Summary panel.

## 7. Scope for this increment

1. New route (e.g. `product-characteristics/`) — this is a genuinely new page, unlike Slices N/O; there is nothing existing to extend.
2. New view function, new template, using the four table columns (Decision 1), four KPI tiles (Decision 2), three filters (Decision 3), read-only detail panel (Decision 4), Coverage Summary panel (Decision 5).
3. No new model, no migration — every value used already exists; the System/Product chain is a query-time join, not a new field.
4. No changes to `system_list`/`system_detail` (Slice E), `characteristic_link_list`/`_create`/`_delete` (Slice L), or any `ClassificationScheme`/`ClassificationTerm` view (Slice M) — this page only reads from and links to them.

## 8. Explicitly out of scope

- Any create/edit/delete capability for `ProductCharacteristic` — strictly read-only, per Finding 1. A future CRUD slice is a separate, not-yet-approved decision.
- Any fabricated "Monitoring Status"/lifecycle-state field (Decision 2) — `is_special` (Special/Standard) is the only real status-like value shown.
- Any multi-org/tenancy concept, any "Importance" field distinct from `is_special` — both already confirmed absent by the prior verification pass (Slice M's decision doc) and not reintroduced here.
- Any AJAX/client-side filtering or tab-swap.
- Any change to the existing `/systems/` page's flat-list rendering — that open question (flat list vs. indented tree) is a separate decision this document does not resolve.

## Recommendation

**Recommendation: READY FOR IMPLEMENTATION**, with the read-only boundary (Section 8's first bullet) called out as the one point most likely to be quietly overstepped during implementation — the completion report for this slice should explicitly confirm no `ProductCharacteristicForm`, no POST-handling view, and no create/edit/delete link or button was added anywhere on the new page.
