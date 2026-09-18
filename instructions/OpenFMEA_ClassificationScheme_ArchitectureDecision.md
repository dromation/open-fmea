# Open-FMEA Architecture Decision — Classification Scheme (`ProductCharacteristic` Type/Category)

Status: **Proposed for approval, 2026-09-05.** Written to unblock a decision that has been sitting open since Phase B: `ProductCharacteristic.primary_classification_id` exists on the model today (added by `Codex_Instruction_ProductProcessCharacteristic_Linking_Slice.md` as a deliberately dormant field) but references nothing, because `ClassificationScheme`/`ClassificationTerm` was explicitly deferred everywhere it came up (`OpenFMEA_CharacteristicIshikawaCauseModel_ArchitectureReview.md` Section 2, the Ishikawa-backend slice's exclusion list, the Characteristic-linking slice's exclusion list, and `OpenFMEA_MockupSpecifications_GUIWireframeArchitecture.md`'s audit of Mockup 8). It is the last open item blocking the classification piece of Mockup 8 (System Characteristics Base). This document proposes a firm, narrow default so the field stops sitting empty — not the general hierarchical/multi-classification design `OpenFMEA_CharacteristicIshikawaCauseModel_ArchitectureReview.md` Section 2 originally sketched. Per DNA rule 8, the approved scope from any review is always the narrowest one stated, not the full ambition — this decision narrows that earlier sketch the same way the Ishikawa-backend slice narrowed its own review down to `CauseCategoryScheme` alone.

## What already exists (confirmed from source)

- `ProductCharacteristic.primary_classification_id` — a `CharField`/nullable reference field, added and left unpopulated by design. No model it points to exists.
- `CauseCategoryScheme` / `CauseCategory` — the real, already-built precedent for exactly this shape: a named scheme entity plus ordered rows FK'd to it, seeded via an idempotent management command (`seed_cause_category_scheme`), exposed nowhere as a hardcoded Python enum.
- `OpenFMEA_CharacteristicIshikawaCauseModel_ArchitectureReview.md` Section 2 previously sketched a fuller version of this concept: `ClassificationTerm` rows with an optional `parent_term_id` for hierarchy, and `ProductCharacteristic` carrying both a required `primary_classification_id` and an optional tuple of `secondary_classification_ids`. That sketch is **not** what this document proposes building — see Decisions 1–3 below for the narrower version, and "Explicitly out of scope."

## Decisions

**Decision 1 — Python enum or scheme+seeded-rows?**
Per `OpenFMEA_DNA_CoreReference.md` rule 6: "A Python enum is appropriate for a closed, structural vocabulary that isn't organization-configurable... a scheme+seeded-rows pattern is required for anything an organization might legitimately redefine." Classification taxonomy is squarely the latter — one organization's Legal/Safety/Functional/Decorative is another's 5M+E-flavored or ISO-flavored scheme, exactly the same reasoning that put `CauseCategoryScheme` ahead of a hardcoded 5M+E enum.

**Proposed: scheme+seeded-rows, following the `CauseCategoryScheme`/`CauseCategory` pattern exactly.**

- `ClassificationScheme` (`StableModel` subclass): `name`, `description`.
- `ClassificationTerm` (`StableModel` subclass): `scheme` (FK to `ClassificationScheme`, `related_name="terms"`, `on_delete=CASCADE`), `name`, `description`, `order` (int, for display ordering — mirrors `CauseCategory.sort_order`).

No `parent_term_id`, no hierarchy. `OpenFMEA_CharacteristicIshikawaCauseModel_ArchitectureReview.md`'s hierarchical sketch (Mechanical/Optical/Electrical/Software nested under Functional) is real future territory, not this increment — a flat list of four terms is all the mockups actually show being used, and hierarchy is exactly the kind of "since we're building it anyway" scope creep this project's discipline exists to prevent.

**Decision 2 — What does a `ClassificationTerm` attach to?**

**Proposed: a single nullable FK, `ProductCharacteristic.primary_classification` → `ClassificationTerm`, `on_delete=SET_NULL`, `related_name="classified_characteristics"`.** This replaces the dormant `primary_classification_id` field with a real FK of the same name/intent (rename during the same migration, no separate placeholder field left behind).

No generic/polymorphic "classifiable" relationship. No `secondary_classification_ids`. Both were part of the earlier, broader sketch and both are unnecessary for what the mockups show: a single Type/Category value per characteristic. `ProcessCharacteristic` and any future `System`-level characteristic do **not** get this FK in this increment — they can get their own FK to `ClassificationTerm` later, once there is a concrete slice that needs it, following this same additive pattern. Building it speculatively now for entities nothing yet reads is exactly the "smallest workable version" rule this project applies everywhere else.

**Decision 3 — Seed data.**

**Proposed: one default `ClassificationScheme` named `"Product Characteristic Classification (default)"`, seeded via a management command `seed_classification_scheme` (mirroring `seed_cause_category_scheme`'s idempotent pattern exactly — running it twice creates no duplicates), with exactly four `ClassificationTerm` rows: Legal, Safety, Functional, Decorative, `order` 1–4.** These are the four categories actually seen across the mockups (Mockup 8's "Type" column and the Product/Process Characteristics panels) — no Mechanical/Optical/Electrical/Software subdivision, no speculative fifth category.

No UI to create additional schemes or terms in this increment. Managing taxonomies (adding a scheme, editing terms, reordering) is a future "admin configures taxonomies" slice, gated on someone actually needing a second scheme — not assumed necessary now just because the model supports it.

**Decision 4 — Scope of this first increment.**

**Proposed, in full:**
1. `ClassificationScheme` / `ClassificationTerm` models + migration.
2. `seed_classification_scheme` management command (idempotent, one scheme + four terms).
3. `ProductCharacteristic.primary_classification` FK wired to `ClassificationTerm` (migration renames/repurposes the existing dormant field rather than adding a second one).
4. A read-only "Classification" column wherever `ProductCharacteristic` is already rendered today (the worksheet table in `fmea_detail.html`, and the Engineering Context page's Product panel, if and only if that page already renders `ProductCharacteristic` rows — no new page is created to show this).
5. A simple `<select>` dropdown on the existing `ProductCharacteristic` create/edit form, populated from the seeded scheme's terms, to set `primary_classification`. No client-side scheme picker — this increment has exactly one scheme, so the form simply lists that scheme's terms.

**Not in scope, explicitly:**
- Any change to `ProcessCharacteristic` (no classification FK added to it in this increment).
- Importance (Critical/High/Medium/Low) or Monitoring-status (Monitored/Calculated/Not Monitored) fields — both seen in the same mockup rows as Type/Category, both separate, still-uncommitted-to concepts. Do not fold them into this slice because they sit in the same table column group visually.
- Any multi-organization/tenancy handling (no organization scoping on `ClassificationScheme` — there is exactly one scheme, usable by the single tenant this codebase supports today).
- Any UI to manage schemes/terms themselves (create/edit/delete a scheme or term).
- Hierarchy (`parent_term_id`) and multi-classification (`secondary_classification_ids`) from the earlier, broader sketch.

## What this unblocks

The `ClassificationScheme` piece of Mockup 8 (System Characteristics Base)'s blocker list specifically: the "Type"/"Category" columns become real, seeded, human-set data instead of a fabricated or hardcoded value. This does **not** unblock Mockup 8 as a whole — the mockup also requires the `System` hierarchy (self-referential parent/child, reviewed separately in `OpenFMEA_SystemHierarchy_ArchitectureReview.md`, not yet built), and explicitly does not unblock Importance, Monitoring status, the "Organizations" stat card, or any chart/diagram on that mockup. See `Codex_Instruction_SystemCharacteristicsBase_SliceM.md` for the first slice that combines this decision with the `System` model into one browsable page.

## Explicitly out of scope (restated)

Multi-org/tenancy, Importance scale, Monitoring status, any change to `ProcessCharacteristic`, classification hierarchy (`parent_term_id`), multi-classification (`secondary_classification_ids`), and any scheme/term management UI.

**Recommendation: READY FOR IMPLEMENTATION** — this is a narrow, additive, low-risk model addition matching an established codebase pattern exactly.
