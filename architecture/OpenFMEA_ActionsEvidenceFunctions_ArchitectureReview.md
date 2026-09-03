# Open-FMEA Architecture Review — Functions / Actions / Evidence / Effectiveness Verification GUI Gap

Status: architecture review — grounded entirely in code already implemented in Phase B, not a new capability. Written per house rule: every missing GUI section needs a review before it's built. User confirmed this as the next slice on 2026-09-03, ahead of FMEA-Projects-as-a-page and the User/Role/Team system.

Author: Claude, acting as Open-FMEA Technical Architect.

## 1. Why this is the cheapest remaining item on the nav-tree audit

Four entities from the newest navigation-tree audit already exist as complete, persisted Django models with matching domain entities and `to_domain()` mappings — I read the code directly before writing this, not inferred from names:

- `Function` (`fmea_app/models.py:192`) — has a `Requirement` child relationship, is already referenced from `FailureMode.function` (a real FK, `select_related("function", ...)` in `fmea_detail`), and already renders as a read-only worksheet column (`row.function`). It has **no create/edit form anywhere** — the only way a `Function` row gets created today is however the ingestion pipeline or seed data populates it.
- `RecommendedAction` (`fmea_app/models.py:484`) — FK to `FailureMode` *or* `FailureCause` (both nullable, exactly one expected in practice), `name`, `description`, `responsible_role` (FK to the existing `ResponsibleRole` catalog), `status` (`ActionStatus`: `open` / `in_progress` / `completed` / `verified` / `cancelled` — `fmea_domain/entities.py:24`), `due_date`. **Zero GUI surface** — no view, no URL, no template, no form.
- `Evidence` (`fmea_app/models.py:531`) — FK to `RecommendedAction`, `name`, `description`, `reference_uri` (a plain URL/text field, not a file upload — matches the existing model, no new capability implied). **Zero GUI surface.**
- `EffectivenessVerification` (`fmea_app/models.py:552`) — FK to `RecommendedAction`, `name`, `description`, `result` (free text), `verified_at`. **Zero GUI surface.**

No new entity, no new migration, no new domain rule is required to expose any of this. `fmea_domain/rules.py` has no `validate_action_transition`-style function (unlike `CauseInfluence`, which has real enforced transition rules) — confirming today's honest state is "free-choice status field," not a gap I'd be silently working around.

## 2. What the newest mockups actually asked for here, and a correction to my own earlier reading

The original plain-text nav tree listed "Functions / Failure Modes / Effects / Causes / Prevention Controls / Detection Controls / Actions" under a group labeled "FMEA ANALYSIS." Having now seen the *rendered* sidebar in Mockups 5–8, that label is reused differently in the visual design — the rendered "FMEA ANALYSIS" sidebar group is actually the four FMEA-type pages (DFMEA/PFMEA/System FMEA/Preventive FMEA). The text tree's actual Functions/Failure Modes/Effects/Causes/Controls/Actions list has no standalone sidebar entries in any mockup shown so far — which matches exactly how `fmea_detail.html` already works today: Failure Modes, Effects, Causes, Prevention Controls, and Detection Controls are all worksheet sub-sections of one FMEA's detail page, not top-level nav items.

This matters for scope: it means adding `Function` and `Action` follows the same pattern — sections inside `fmea_detail.html` — not new sidebar nav items, so this slice does **not** touch `test_gui_navigation_scope.py`'s allow-list at all.

`Evidence` and `EffectivenessVerification` map to the tree's "Evidence & Tests," which the rendered mockups group under a different sidebar section, "VALIDATION & CHANGE," alongside "Validation Trajectory" and "Change Impact" — neither of which exists or is being built. Giving `Evidence & Tests` its own sidebar entry while its sibling items don't exist would be the same mistake the "no nav item without backend" rule exists to prevent, just for a partially-backed section rather than a fully-fabricated one. Recommend instead: `Evidence` and `EffectivenessVerification` get a detail sub-page reachable *from* an `Action`'s own detail page (an `Action` needs a detail page regardless, to show its evidence/verification history) — no new sidebar entry.

## 3. Proposed design

**Functions:** add a `Function` create/edit form as a new worksheet section in `fmea_detail.html`, parented to the `FMEA` (mirrors `Process`/`Operation`, not `FailureMode` — `Function` is not FK'd to `FailureMode` in the model). Add a simple `<select>` to `FailureModeForm` so a new `FailureMode` can optionally be linked to an existing `Function` at creation time (the FK already exists on `FailureMode`, per `fmea_detail`'s `select_related("function", ...)` — I did not misread this, it's real).

**Actions:** add an "Actions" sub-section under each `FailureCause` row (mirrors the existing Prevention/Detection Controls pattern exactly — same template structure, same "table + compact add-form" idiom already used three times in `fmea_detail.html`). `failure_mode`-only actions (not tied to a specific cause) are a real possibility per the model (both FKs nullable) — recommend a second, smaller "Actions not tied to a specific cause" section directly under the `FailureMode` row for that case, rather than forcing every action onto a cause.

**Action detail page (new):** `/actions/<stable_id>/` — first detail-style page this slice adds. Shows the action's fields, its `Evidence` list + add-form, its `EffectivenessVerification` list + add-form. This is the one new URL/template pattern in this slice; everything else is an addition to the existing worksheet.

**Status field:** a plain `<select>` over all five `ActionStatus` values, no enforced ordering — matches the real absence of any domain transition rule (Section 1). Recommend **not** inventing an auto-transition (e.g., "recording an `EffectivenessVerification` automatically sets status to `verified`") — the project's own core rule against silent auto-assignment (DNA rule set, "never auto-assign risk/classification") generalizes cleanly here: a human sets status explicitly, always. If the user wants a suggested/pre-filled status when a verification is added (not auto-committed), that's a reasonable small addition — flagged as an open decision below rather than assumed.

**`ResponsibleRole` picker:** `RecommendedAction.responsible_role` is a real FK today with no create UI for `ResponsibleRole` itself anywhere in the app (grep confirmed zero hits in `views.py`/`urls.py`/`forms.py`). Recommend a plain `<select>` populated from existing `ResponsibleRole` rows (whatever's in the DB via seed/import) for this slice — **not** proposing a `ResponsibleRole` CRUD page, which is out of scope and not asked for by any mockup or nav-tree item.

## 4. Decisions Requiring Approval

1. **Action-not-tied-to-a-cause section** (Section 3) — build it, or restrict `Action` creation to always require a `FailureCause` for this first increment (simpler, but forecloses a real, already-modeled use case)?
2. **Status field behavior on recording a verification** — plain manual dropdown only (my recommendation, matches the "no silent auto-assignment" house rule), or a suggested/pre-filled (not auto-committed) status nudge when an `EffectivenessVerification` is added?
3. **`Function` linkage on `FailureMode` creation** — add the optional `<select>` now (Section 3), or leave `FailureMode.function` display-only this slice and defer editable linkage to later (it's currently populated only by ingestion/seed data, so this decides whether a user can *manually* attach a `Function` to a `FailureMode` yet)?

## 5. What this review does not propose

No new entity, no new migration, no new domain/transition rule, no `ResponsibleRole` CRUD, no sidebar/nav additions, no change to `test_gui_navigation_scope.py`. No file-upload capability for `Evidence` (stays a `reference_uri` text field, matching the existing model). No "Validation Trajectory" or "Change Impact" — those remain unbuilt and uncataloged-for-action, per the Mockup 3 hold-off decision, which this slice does not reopen.

## Recommendation

**READY WITH CONDITIONS** — same status language as every prior review in this project: the underlying data model is fully built and stable, but Section 4's three decisions are real judgment calls, not facts already settled by the codebase, and should be confirmed (or the recommended defaults accepted) before the Codex instruction is finalized for implementation.
