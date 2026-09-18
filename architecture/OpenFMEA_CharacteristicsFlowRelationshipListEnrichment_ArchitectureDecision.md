# Open-FMEA Architecture Decision — Characteristics Flow / Diagram: Relationship List Enrichment (Mockup 9, third pass)

Status: **Decision, 2026-09-10** — proposing a firm, narrow default for the user to approve or correct. Written in direct response to the user-supplied wireframe spec for this mockup (2026-09-06/10), which is explicit that this page is a **relationship workspace for karakteristike**, not a generic flowchart editor. This document is a gap-analysis against `OpenFMEA_CharacteristicsFlow_ArchitectureDecision.md` (Slice L, built and independently verified 2026-09-05): it proposes the narrowest real slice of the new spec's content that does **not** require either of Slice L's two already-named, still-unmade decisions — a graph-rendering library choice, and an AI auto-link/confidence-scoring human-review-gate design. Most of the spec's numbered items depend on one of those two; this document is explicit, item by item, about which half is addable now and which is not.

## 1. What already exists (Slice L, built and independently verified 2026-09-05)

`CharacteristicLink`: `relationship_type` (6 choices), `strength` (5 choices), `created_by` (free text), `from_characteristic`/`to_characteristic` (both FK to `ProductCharacteristic`, `CASCADE`) — confirmed via direct migration read (`0013_characteristiclink.py`). **No `status` field exists on this model** — no confirmed/suggested/possible distinction of any kind. `characteristic_link_list` (`views.py:1472`) already filters by `relationship_type` and by a single `characteristic` id (matching either `from_characteristic` or `to_characteristic` via `Q`), rendering a plain table; `characteristic_link_create`/`characteristic_link_delete` are plain form/POST views. `ClassificationScheme`/`ClassificationTerm` (Slice M) exist but are seeded flat and narrow: one scheme, four terms — **Legal, Safety, Functional, Decorative** — no hierarchy, no Mechanical/Optical/Electrical/Software/Chemical subtypes, no "Special" or "Critical" term (though `ProductCharacteristic.is_special` is a real separate boolean, per Slice P's grounding). No visual diagram, no canvas, no node-link rendering, no AI suggestion engine exist anywhere in this app.

## 2. Item-by-item disposition against the new spec

Numbering matches the user's spec sections.

- **§1 Namen, §20 Base connection**: already true today — `characteristic_link_list` already reads from the real `ProductCharacteristic`/`CharacteristicLink` tables, not a separate store. No change needed.
- **§2 Page Header**: addable. Title/description already exist on the page; a Project/System context selector is **not** addable — no `CharacteristicLink`/`ProductCharacteristic` field carries a Project or System scope today (a characteristic's System, per Slice P, is reached only through a doubly-nullable `requirement→function→product|operation.process→system` chain, not a settable context). Propose a page-level System **filter** (Decision 2 below) instead of a persistent "context" concept — the mockup's "current context" implies a stateful selection this app has no session/user-state mechanism to hold (confirmed: no per-user session-state field anywhere in this codebase).
- **§3 View/Diagram Controls, §25 toolbar row**: addable as a GET-form filter row, extending the existing `relationship_type`/`characteristic` filters — see Decision 2.
- **§4 Main Diagram Canvas, §8-10 relationship lines/direction/fan-in-fan-out, §14 Selected Characteristic State (visual highlighting), §15 Relationship Focus (visual network isolation), §24 Zoom/pan**: **NOT addable.** All of this is the node-link graph rendering itself — exactly the capability Slice L's own decision document named as deferred, requiring its own graph-rendering-library decision. This document does not make that choice or approximate it with a different technology; a table-based "Incoming/Outgoing" list (Decision 3) conveys the same underlying facts without pretending to be a diagram.
- **§5-7 Characteristic Nodes, Symbols, Color State**: **partially addable, narrowed.** A small type/category badge next to each characteristic (reusing the real `primary_classification` term and the real `is_special` boolean, the same two facts Slice P already surfaces) is addable as additive CSS on the existing list rows and detail panel — see Decision 4. The mockup's fuller symbol taxonomy (Mechanical/Optical/Electrical/Software/Chemical as Functional subtypes, a distinct "Critical" term) does not exist in the real `ClassificationScheme` seed data (four flat terms only) — proposing new seeded terms is a separate, not-yet-asked-for change to `OpenFMEA_ClassificationScheme_ArchitectureDecision.md` and is out of scope here; this decision surfaces only the four real terms plus `is_special`.
- **§11 Manual Linking**: already built (Slice L's `characteristic_link_create`). No change.
- **§12 Automatic Link Suggestions, §13 Possible Links, §19's "confirmed vs. suggested" status, §23's "Suggested/Possible" legend line**: **NOT addable.** This is the AI auto-link/confidence-scoring capability Slice L's decision document explicitly named as not approved, requiring its own human-review-gate design decision. No `status` field exists on `CharacteristicLink` to even represent "suggested" today, and inventing one here — without the review-gate design that would govern how a suggestion becomes a confirmed link — would misrepresent a real design gap as solved. Not proposed.
- **§16 Right-Side Detail Panel, §17 Incoming, §18 Outgoing**: **addable, and the most directly useful real piece of this spec.** `CharacteristicLink.from_characteristic`/`to_characteristic` already gives a real, queryable direction — "Incoming" = links where the selected characteristic is `to_characteristic`; "Outgoing" = links where it is `from_characteristic`. This is a plain filter over already-built data, not a new capability. See Decision 3.
- **§19 Relationship Details (source/target/type/status)**: addable minus "status" (doesn't exist — see §12 above). Source, target, `relationship_type`, and `strength` are all real fields already on `CharacteristicLink`.
- **§21 Relationship/Coverage Summary**: addable as plain counts, same discipline as Slices N/O/P's equivalent panels — see Decision 5.
- **§22 Unlinked Characteristics**: addable — `ProductCharacteristic` rows with zero rows in `CharacteristicLink` on either FK, a straightforward `exclude`/annotate query. See Decision 5.
- **§23 Diagram Legend**: narrowed to a **Relationship Type legend** (the six real `relationship_type` choices) — the "Symbols" half depends on §5-7's narrowed real taxonomy (four terms + `is_special`, not the mockup's fuller list), and the "Suggested/Possible" line is dropped per §12's disposition.
- **§26 Interaction Flow**: the "Incoming/Outgoing → Possible Links → Manual/Suggested → Confirmed" flow in the spec is real up through "Incoming/Outgoing" and "Manual" (both addable/already built); "Possible Links" and "Suggested Relationship" are the same not-addable AI-suggestion piece as §12-13.

## 3. Decision 1 — this is a list-page enrichment, not a new diagram page

Extend the existing `characteristic_link_list` route/view/template exactly as Slices N and O extended their own list pages — no new route, no new charting/graph library, no AI. The page becomes a real "relationship workspace" in the sense the spec asks for (§1's stated goal), built entirely from list/table/panel UI this app already uses everywhere, not from a canvas.

## 4. Decision 2 — filter/toolbar row: extend the existing GET-form filters

Add to the existing `relationship_type`/`characteristic` GET-form: `category` (dropdown of the four real `ClassificationTerm`s), `system` (dropdown of `System.objects.all()`, filtered via the same doubly-nullable chain Slice P's decision already specified and accepted as honestly partial), and `view` (`all` vs. `linked-only` vs. `unlinked-only`, reusing Decision 5's linked/unlinked definition). Plain server-side reload, no AJAX, matching this app's universal convention.

## 5. Decision 3 — right-side detail panel with real Incoming/Outgoing lists

`?selected=<stable_id>` on the same route (no new route), showing: `stable_id`, `name`, the real category badge (Decision 6), then two real lists — **Incoming** (`CharacteristicLink.objects.filter(to_characteristic=selected)`, showing each link's `from_characteristic`, `relationship_type`, `strength`) and **Outgoing** (`CharacteristicLink.objects.filter(from_characteristic=selected)`, same fields). No "Possible Links" section (§12/13, not addable). No "Status" field on the characteristic itself — `ProductCharacteristic` has none (confirmed, same finding as Slice P) — the panel shows category/`is_special` instead, not a fabricated status.

## 6. Decision 4 — small category/special badge, additive CSS only

A compact badge next to each characteristic's name in the list and the detail panel, showing its real `primary_classification.name` (or "Unclassified") and, separately, a "Special" marker when `is_special=True` — the same two real facts Slice P's KPI/table already surface, reused here rather than recomputed differently. Additive CSS class only, no new field, no new taxonomy.

## 7. Decision 5 — Coverage Summary and Unlinked Characteristics panels

Plain counts over the currently-filtered characteristic set (same discipline as Slices N/O/P): total characteristics in view, linked count (`CharacteristicLink` involving them on either side, `>0`), unlinked count, total link count. A separate **Unlinked Characteristics** list — real `ProductCharacteristic` rows with zero `CharacteristicLink` rows either direction — rendered as a plain list with links into each characteristic's own detail (reusing Slice P's `product_characteristic_list?selected=` panel where useful, not duplicating it). No "possible/suggested" count anywhere (§12/13, not addable — there is nothing to count).

## 8. Decision 6 — Relationship Type legend, narrowed

A small legend listing the six real `relationship_type` choices (already defined on `CharacteristicLink.RELATIONSHIP_TYPE_CHOICES`) — no symbol/category legend beyond the four real `ClassificationTerm`s plus `is_special` (per Decision 4), no "confirmed vs. suggested" line.

## 9. Scope for this increment

1. Extend `characteristic_link_list` (view + template) with: the filter row (Decision 2), a right-docked `?selected=` detail panel with real Incoming/Outgoing lists (Decision 3), category/special badges (Decision 4), Coverage Summary + Unlinked Characteristics panels (Decision 5), the narrowed legend (Decision 6).
2. No new route — everything is a GET-param extension of the existing route, same convention as Slices N/O.
3. No new model, no migration — every value used already exists on `CharacteristicLink`, `ProductCharacteristic`, `ClassificationTerm`, `System`.
4. No changes to `characteristic_link_create`/`characteristic_link_delete` (Slice L's manual-linking forms stay exactly as built) or to `product_characteristic_list` (Slice P) beyond linking to it from the Unlinked Characteristics panel.

## 10. Explicitly out of scope — named here so it is never silently built around or silently dismissed

- **The node-link diagram itself** (canvas, nodes, lines, direction arrows, zoom/pan, visual selection-highlighting/focus) — blocked on a graph-rendering library choice that has never been made. This document does not choose one, and does not approximate a diagram with a different widget.
- **AI-suggested/possible links, and any "confirmed vs. suggested" status on `CharacteristicLink`** — blocked on an AI auto-link human-review-gate design that has never been made. No `status` field is added to the model in this decision.
- **A persistent Project/System "context" selector** — no session/user-state mechanism exists in this app for it; a per-request filter (Decision 2) is proposed instead.
- **Any expansion of `ClassificationScheme`/`ClassificationTerm`'s seeded terms** (Mechanical/Optical/Electrical/Software/Chemical/Critical) — a separate, not-yet-asked-for change to Slice M's decision, not folded in here.
- **Any per-characteristic "Status" field** — none exists on `ProductCharacteristic`; not invented here (same finding as Slice P).

## Recommendation

**Recommendation: READY FOR IMPLEMENTATION for the list-based half (Decisions 1-6, Sections 3-9); the diagram/AI half of the mockup remains explicitly blocked and is flagged to the user here rather than built around.** Two standing decisions still need to be made before the rest of Mockup 9 can be built: (a) which graph-rendering library/approach to adopt for the node-link diagram, and (b) how an AI-suggested link would be scored, presented, and gated through human review before becoming a real `CharacteristicLink` row. Neither is proposed or assumed by this document.
