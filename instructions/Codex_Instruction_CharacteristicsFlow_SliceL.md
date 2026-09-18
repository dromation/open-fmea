# Codex Implementation Instruction — Characteristic Link (Manual Linking Only) (Slice L)

Status: Approved for implementation, 2026-09-04. Grounded in `OpenFMEA_CharacteristicsFlow_ArchitectureDecision.md`, which is this instruction's sole authority. That document approves exactly one thing: a new `CharacteristicLink` entity plus a manual create/list/delete GUI for it. It does **not** approve, and this instruction does not build, any part of Mockup 9's AI-assisted "Auto Link" capability or its force-directed "Link Network" graph visualization — both are named there as separate, dedicated future decisions, not as work postponed within this slice. Anything in Mockup 9 not explicitly listed in Section 1 below is out of scope.

## 0. Decisions for this slice

1. **`CharacteristicLink.from_characteristic` and `.to_characteristic` both FK to `ProductCharacteristic`, on `on_delete=models.CASCADE`.** No polymorphic/generic link, no System-level characteristic target — per the architecture decision Section 1, this is a deliberate narrowing, not an oversight.
2. **`relationship_type` is a Python-level `choices` enum** (`Drives`, `Influences`, `Affected By`, `Constrained By`, `Supports`, `Required By`) stored as a `CharField` with `choices=`, not a scheme/seeded-rows model. No `CharacteristicLinkScheme` or similar is created.
3. **`strength` is a Python-level `choices` enum** (`Critical`, `High`, `Medium`, `Low`, `None`) stored as a `CharField` with `choices=`. This field lives only on `CharacteristicLink` — no field is added to `ProductCharacteristic` in this slice, and no `Importance`/`ClassificationScheme` question is touched, decided, or referenced beyond this note.
4. **`created_by` is a plain `CharField`, free text** — matching `RiskEvaluation.actor` exactly (same max length, same "just a name string" precedent, not a FK to `settings.AUTH_USER_MODEL`).
5. **AI auto-link and force-directed graph rendering are explicitly OUT of scope and NOT approved by this slice** — not "not built yet," not "a later phase of this same instruction." They are a different, unscoped, unreviewed body of work that this instruction does not authorize in any form: no `AiProvider` task, no confidence field, no suggestion/review-queue model, no graph-rendering library import, no canvas element. If asked to add any of this "since the model already exists," stop and report rather than doing it.
6. **No "Link Matrix," "Link Rules," or "Impact Paths" tab.** This slice is a single list page and a single create form — no tab strip of any kind.
7. **`from_characteristic` and `to_characteristic` may reference the same `ProductCharacteristic`.** No self-link prevention is built in this slice (it is a plausible future validation rule, not decided here) — do not add it speculatively.
8. **No orphan-detection, warnings, or validation logic beyond standard Django form/model field validation** (e.g. required fields, valid choice values). No "characteristics with no links" query, no consistency checking.

## 1. Exact Scope

1. New model `CharacteristicLink` (`django_app/fmea_app/models.py`), extending `StableModel` like every other domain model in this app:
   - `from_characteristic = models.ForeignKey(ProductCharacteristic, related_name="outgoing_links", on_delete=models.CASCADE)`
   - `to_characteristic = models.ForeignKey(ProductCharacteristic, related_name="incoming_links", on_delete=models.CASCADE)`
   - `relationship_type = models.CharField(max_length=32, choices=RELATIONSHIP_TYPE_CHOICES)`
   - `strength = models.CharField(max_length=16, choices=STRENGTH_CHOICES)`
   - `created_at = models.DateTimeField(auto_now_add=True)`
   - `created_by = models.CharField(max_length=255, blank=True)`
2. One migration adding `CharacteristicLink` and its table only. No change to `ProductCharacteristic` or any other existing model.
3. List view — route `/characteristic-links/`, name `fmea:characteristic_link_list`. Renders every `CharacteristicLink`, columns exactly: From Characteristic (name), To Characteristic (name), Relationship Type, Strength, Created By, Created At. Server-side GET-form filters: `relationship_type` (`<select>` over the six values plus "All"), `characteristic` (`<select>` over all `ProductCharacteristic` names plus "All" — matches either `from_characteristic` or `to_characteristic`). No AJAX; filtering is a normal GET request re-rendering the page, matching every other list page in this app (e.g. Risk Matrix, Engineering Context).
4. Create form — route `/characteristic-links/create/`, name `fmea:characteristic_link_create`. Fields exactly: From Characteristic (`<select>` of `ProductCharacteristic`), To Characteristic (`<select>` of `ProductCharacteristic`), Relationship Type (`<select>`), Strength (`<select>`), Created By (text input). One link created per submit — no bulk/multi-row create UI. On success, redirect to the list view.
5. Delete action — route `/characteristic-links/<str:stable_id>/delete/`, name `fmea:characteristic_link_delete`. POST-only, deletes the one row, redirects to the list view. A "Delete" button/form per row on the list page, no confirmation modal required (matches this app's existing lack of client-side JS confirmation dialogs — a plain POST form is sufficient).
6. Sidebar: add a single `Characteristics Flow` (or equivalent short label — your call, keep it short) entry linking to `fmea:characteristic_link_list`, placed under the same nav grouping the mockup's `_sidebar.html` audit already reserved for this feature (see `Codex_Instruction_PlannedNavPlaceholders_Slice.md`, "CONTEXT (from Open-EQMS): ... Characteristics Flow / Diagram," currently a disabled placeholder). This slice converts that one placeholder to a real, working link — do not touch any other placeholder label in that file.

## 2. Exact Allowed / New Files

```text
django_app/fmea_app/models.py                                  # new CharacteristicLink model only; RELATIONSHIP_TYPE_CHOICES/STRENGTH_CHOICES constants
django_app/fmea_app/migrations/000X_characteristiclink.py      # new
django_app/fmea_app/views.py                                    # new characteristic_link_list/create/delete views only
django_app/fmea_app/urls.py                                     # new routes
django_app/fmea_app/forms.py                                    # new CharacteristicLinkForm
django_app/fmea_app/templates/fmea_app/characteristic_link_list.html    # new
django_app/fmea_app/templates/fmea_app/characteristic_link_form.html    # new
django_app/fmea_app/templates/fmea_app/_sidebar.html            # flip the one existing "Characteristics Flow / Diagram" placeholder to a real link; nothing else in this file changes

tests/test_characteristic_link.py                                # new
tests/test_gui_navigation_scope.py                                # one required update — see Section 4
```

Nothing else. No change to `ProductCharacteristic`, `CauseInfluence`, `admin.py`, OFEF export, or any AI/ingestion module.

## 3. Required Validation and Explicit Exclusions

- No AI/auto-link/confidence-scoring code anywhere in the diff — no `AiProvider` import, no confidence field, no suggestion model.
- No force-directed graph, no `<canvas>`, no graph-rendering library import (Chart.js or otherwise) anywhere in this slice's templates.
- No "Link Matrix," "Link Rules," or "Impact Paths" tab or route.
- No orphan-detection/warnings logic; no self-link prevention (Decision 7); no bulk-create path.
- `strength` choices are exactly `Critical`/`High`/`Medium`/`Low`/`None`; `relationship_type` choices are exactly `Drives`/`Influences`/`Affected By`/`Constrained By`/`Supports`/`Required By` — no additional values, no organization-configurable scheme.
- `_sidebar.html` diff is exactly one label's markup changing from disabled placeholder to a working link — every other entry in that file is unchanged.
- Filtering is a server-side GET-form reload only — no JS-driven client-side filtering, no fetch/AJAX call anywhere in the new templates.

## 4. Required Tests

`tests/test_characteristic_link.py`:
- Create two `ProductCharacteristic` fixtures and a `CharacteristicLink` between them with a specific `relationship_type`/`strength`; assert the list page renders both characteristic names, the relationship type, and the strength correctly.
- Assert the `relationship_type` GET filter narrows the list to only matching rows, and the `characteristic` GET filter returns rows where the given characteristic is either the from- or the to-characteristic.
- Submit the create form with a valid from/to/relationship_type/strength/created_by; assert a new `CharacteristicLink` row exists with exactly those values, and the response redirects to the list view.
- POST to the delete route for an existing link; assert the row no longer exists and the response redirects to the list view.
- Assert the list and create pages contain none of: `<canvas`, `"Link Matrix"`, `"Link Rules"`, `"Impact Paths"`, `"confidence"`, `"Auto Link"`.

`tests/test_gui_navigation_scope.py` — **one required, intentional change**: the existing assertion that `"Characteristics Flow / Diagram"` renders as a non-interactive, disabled placeholder no longer holds once this slice ships. Update that one assertion so the label is asserted as a real, working link to `fmea:characteristic_link_list`, matching how every other already-real nav item in that test is asserted. Every other assertion in that file — including every other still-disabled placeholder label — stays exactly as-is. Call this change out explicitly in your report as intentional, not a regression.

Full existing suite re-run with no other unrelated assertion changes.

## 5. Commands to Run

```powershell
python -B manage.py check
python -B manage.py makemigrations --check --dry-run
python -B -m pytest
```

## 6. Acceptance Criteria

1. `CharacteristicLink` exists with exactly the fields in Section 1.1, both FKs pointed at `ProductCharacteristic`, migrated cleanly.
2. `/characteristic-links/` lists all links with correct columns and working relationship-type/characteristic filters (server-side GET form, no AJAX).
3. `/characteristic-links/create/` creates exactly one link per submit with the five fields in Section 1.4, then redirects to the list.
4. The delete route removes exactly the targeted link and redirects to the list.
5. The sidebar's "Characteristics Flow / Diagram" entry is now a real, working link; every other placeholder in `_sidebar.html` is untouched.
6. No AI/auto-link code, no graph/canvas rendering, and no Link Matrix/Link Rules/Impact Paths surface appears anywhere in the diff.
7. Full test suite passes (including the one intentional, called-out flip in `test_gui_navigation_scope.py`), `manage.py check` clean, exactly one new migration.
8. Mirrored into `open_fmea_training_set` and the training EXE rebuilt, per the standing discipline.

## 7. Explicit Exclusions (restated for emphasis)

Any AI-assisted or "Auto Link" capability, any confidence-scoring field or logic, and any human-review-queue for AI-proposed links are **not** part of this slice in any form — they require their own dedicated future architecture review (prompt design, confidence-threshold policy, and an explicit human-review gate before any suggestion becomes a real `CharacteristicLink`) before any instruction for them is written, and nothing in this diff should anticipate or scaffold for that future work. Likewise, any force-directed graph rendering, graph-layout library, or "Link Network" visualization is **not** part of this slice — it requires its own separate graph-rendering-library decision (per `OpenFMEA_ChartingLibrary_ArchitectureDecision.md` Section 4, which explicitly declined to cover this case) before any instruction for it is written. The "Link Matrix," "Link Rules," and "Impact Paths" tabs are likewise out of scope and not silently expandable into this slice. If any of this seems to need changing to deliver a working slice, stop and report — do not silently expand scope.
