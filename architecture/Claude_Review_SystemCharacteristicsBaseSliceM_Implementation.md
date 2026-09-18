# Claude Review — System Characteristics Base (Slice M) Implementation

**Author:** Claude (this session) · **Date:** 2026-09-05
**Instruction:** `Codex_Instruction_SystemCharacteristicsBase_SliceM.md` + `OpenFMEA_ClassificationScheme_ArchitectureDecision.md`

## 1. Critical grounding finding — Slice M duplicates Slice E's already-built `System` model and pages

Before writing anything, I read Slice M's instruction in full and found it was written as if `System` did not exist yet: it specifies the identical model shape (self-referential `parent`, `name`/`description`/`code`/`status`), the identical `Product.system`/`Process.system` FKs, and the identical `/systems/` list, `/systems/new/`, `/systems/<stable_id>/edit/` routes and sidebar link that **Slice E already built, tested (140/140), mirrored, and delivered earlier today** (see `Claude_Review_SystemProductProcessSliceE_Implementation.md`). Slice E's instruction is dated 2026-09-04 and Slice M's is also dated 2026-09-04 — both were evidently approved in the same batch without being cross-checked against each other.

I did not re-build `System`, `system_list`/`system_create`/`system_edit`, or the sidebar link a second time — that model and those routes already exist, are already tested, and re-running Slice M's own migration instructions against them would either collide with the already-applied migration or silently duplicate work. What I did:

- Left Slice E's `System` model, `/systems/` (flat list, sorted `parent__name, name`, with a Parent column), `/systems/new/`, `/systems/<stable_id>/edit/`, `/systems/<stable_id>/` (detail — Slice M doesn't even ask for a detail page, but doesn't prohibit one either), and the sidebar link exactly as they are.
- **Added the one genuinely new thing Slice M asks for on top of the existing `System` model that Slice E's own text explicitly pre-authorized:** full walk-up-the-parent-chain cycle detection in `System.clean()` (Slice E's Decision 9 said only a one-hop self-parent check was in scope, and explicitly said "If a future slice needs full cycle detection, it can add it then" — this is that addition, not scope creep). Verified it rejects both the one-hop case and a two-levels-deep grandchild cycle (`tests/test_system_model.py`).
- **Did not rebuild `system_list.html` to match Slice M's differently-described UI shape** (an indented parent/child tree) instead of Slice E's already-built, already-verified flat list with a Parent column. Both pages satisfy the same underlying requirement (children groupable near their parent), just via a different rendering choice. Picking a side and rewriting already-verified, delivered work on my own judgment felt like exactly the kind of unilateral scope decision the project's discipline says to avoid — flagging this explicitly for the concurrent architecture session to resolve (retire this part of Slice M's spec, or issue a follow-up instruction if the indented-tree rendering is actually wanted) rather than resolving it myself.

## 2. Second grounding finding — no `ProductCharacteristic` create/edit GUI exists (same category as Slice E's Finding 1)

Slice M's item 8 assumes an "existing `ProductCharacteristic` create/edit form" that only needs a `primary_classification` `<select>` added. Grepped the actual codebase before writing anything: zero matches for `ProductCharacteristicForm`, zero `ProductCharacteristic` create/edit routes in `urls.py`, zero corresponding view functions — `ProductCharacteristic` rows are populated only via ORM/ingestion/seed data today, exactly the same situation as `Product`/`Process` in Slice E. I did not build a new `ProductCharacteristic` CRUD GUI (not in this slice's allowed-file list, a real scope expansion). I built the parts of this requirement that are real: the `primary_classification` FK itself, and its read-only display wherever `ProductCharacteristic` already renders (see Section 3). The "settable via the existing create/edit form" half of acceptance criterion 4 does not apply for the same reason it didn't apply in Slice E.

## 3. What was built

**`ClassificationScheme`/`ClassificationTerm`** (`models.py`), following `OpenFMEA_ClassificationScheme_ArchitectureDecision.md` Decisions 1–2 exactly: `ClassificationScheme` (`name`, `description`); `ClassificationTerm` (`scheme` — a real FK, `related_name="terms"`, `on_delete=CASCADE`; `name`; `description`; `order`). Both `StableModel` subclasses. Note this uses a real Django FK rather than this codebase's other scheme-pattern precedent (`CauseCategory.scheme_id`, a plain stable-id-string `CharField`) — this is not an inconsistency I introduced; the decision document explicitly specifies a real FK here ("This replaces the dormant `primary_classification_id` field with a real FK of the same name/intent").

**`ProductCharacteristic.primary_classification`** replaces the dormant `primary_classification_id` `CharField` with a real nullable FK to `ClassificationTerm` (`on_delete=SET_NULL`). One migration (`0007_classificationscheme_and_more.py`) does this as a straightforward remove-old-field/add-new-field (Django's autodetector doesn't treat a name-and-type change as a rename without an interactive prompt; since the old field was confirmed unpopulated everywhere — "left unpopulated by design" per the decision doc, and confirmed by grep across the codebase — this loses no data). `to_domain()` updated so the domain layer's `primary_classification_id: str | None` contract still receives the related term's `stable_id` string (not the FK's raw integer PK, which Django's `<field>_id` shadow attribute would otherwise expose) — checked and tested directly (`test_product_characteristic_with_classification_round_trips_correctly`).

Checked two other places that reference the old field name before touching anything: `domain/fmea_domain/entities.py`'s `DomainProductCharacteristic.primary_classification_id` field is untouched (it's an independent domain-layer field name/contract, unaffected by the Django model's internal field name or type, and the `to_domain()` fix above keeps satisfying it). `seed_demo.py`'s `defaults={"primary_classification_id": None, ...}` needed no change at all — Django's FK fields automatically expose a `<name>_id` attribute/kwarg, so passing `primary_classification_id=None` continues to work unchanged and sets the new FK to null exactly as before (confirmed by the full suite still passing, including `test_seed_demo_reproducibility.py`).

**`seed_classification_scheme`** management command, mirroring `seed_cause_category_scheme.py`'s exact idempotent `update_or_create` pattern: one scheme ("Product Characteristic Classification (default)"), four terms (Legal/Safety/Functional/Decorative, `order` 1–4).

**Admin registration** (`admin.py`): `System`, `ClassificationScheme`, `ClassificationTerm` each get a real `ModelAdmin`. Also corrected `ProductCharacteristicAdmin`'s `search_fields`, which referenced the now-removed `primary_classification_id` CharField — replaced with `primary_classification__name` (the same file Slice M's own allowed-file list already required touching for the three new registrations).

**Read-only "Classification" column** added to `fmea_detail.html`'s worksheet table, next to the existing "Product Characteristics" column, showing each characteristic's `primary_classification.name` or an em dash when unset. `_build_worksheet_rows`/`_worksheet_row` needed no change — `row.product_characteristics` already carries full `ProductCharacteristic` objects, so the template reads `primary_classification` directly. `engineering_context.html` was **not** touched, per Slice M's own conditional wording ("only if this template already renders `ProductCharacteristic` rows") — confirmed by re-reading that template that it only ever renders `Product`/`Process` rows, never `ProductCharacteristic`.

## 4. Test coverage

`tests/test_system_model.py` (4 tests): parent/children relationship, one-hop self-parent rejection, two-level grandchild-descendant cycle rejection, Product/Process-with-no-System regression check.

`tests/test_classification_scheme.py` (3 tests): seed idempotency (exact scheme name, four terms in the right order), classified `ProductCharacteristic` round-trip (model FK, `to_domain()`'s stable-id mapping), unclassified `ProductCharacteristic` displays as `None`/unclassified rather than erroring.

`tests/test_system_characteristics_base_views.py` (6 tests): `/systems/` 200 + lists every System with children grouped near their parent (per Section 1's flagged UI-shape note, not literal indentation); count correctness against real `children`/`products`/`processes` querysets; `/systems/new/` create round-trip; `/systems/<id>/edit/` cycle-forming POST rejected with the System left unmodified; `/systems/` narrowed-scope negative check (no "Organizations"/"Importance"/"Monitoring"/`<canvas`); the worksheet's Classification column shows the right term name and the right unclassified placeholder.

## 5. Verification

Fresh venv, live shell, both repos:

| Check | `open_fmea` | `open_fmea_training_set` |
|---|---|---|
| `manage.py check` | clean | clean |
| `makemigrations --check --dry-run` | "No changes detected" (after generating `0007`) | "No changes detected" |
| New test files (isolated) | 13/13 | — |
| Full suite | **153/153** | **153/153** |

153 = the prior 140 (Slices A–E) plus the 13 new tests here — arithmetic checked. Grepped every changed/new file for every excluded term the instruction names (`Importance`, `Monitoring`, `Nominal Value`, `secondary_classification`, `parent_term_id`, `Organizations`, `<canvas`, `Chart.js`) — zero matches.

Diff surface via `git status --short`: `models.py`, `admin.py`, `fmea_detail.html` (all modified/further modified), `seed_classification_scheme.py`, migration `0007` (new), `test_system_model.py`, `test_classification_scheme.py`, `test_system_characteristics_base_views.py` (new) — matches Slice M's allowed-file list exactly, minus the two files intentionally not touched (`system_list.html`/`system_form.html`, per Section 1; `engineering_context.html`, per Section 3) and the routes/model/sidebar-link items already satisfied by Slice E.

Mirrored to `open_fmea_training_set` and byte-diffed (`diff -q`): all 8 changed/new files identical. Full suite re-run there independently: 153/153.

## 6. Scope discipline

No `ProcessCharacteristic` change anywhere in the diff. No Importance/Monitoring-status/Nominal-Value/Target/Unit field on any model. No `ClassificationTerm` hierarchy, no `secondary_classification_ids`. No Organizations/tenancy concept, no chart/canvas/Chart.js usage, no Characteristics Flow diagram. No image/attachment/owner field on `System`.

## 7. Still open

- `.git/index.lock` still needs a manual delete in `open_fmea`. Nothing committed, per "build first, commit later."
- Sections 1 and 2's two findings need the concurrent architecture session's attention before any future slice assumes either the `/systems/` page's exact rendering shape or a `ProductCharacteristic` GUI that doesn't exist.
- Remaining slices from the 2026-09-05 batch: F (Evidence & Tests), G (FMEA Elements standalone pages), H (Process Control Characteristics), I (Change Impact), J (Risk Trajectory & Propagation), K (Consolidated Home), L (Characteristics Flow) — not yet read in full or implemented.
