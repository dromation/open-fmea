# Open-FMEA Architecture Review — Evidence & Tests (Validation Test Plan)

Status: architecture review — new domain design, not grounded in an already-built entity (contrast with the Risk Matrix and Functions/Actions reviews, which reused existing Phase B models). Written per house rule, and specifically because building the small existing-model GUI first was found to conflict with this fuller vision — see `Codex_Instruction_FunctionsActionsEvidence_GUIGap_Slice.md`'s 2026-09-03 scope-pull notice.

Author: Claude, acting as Open-FMEA Technical Architect.

## 1. Why this needs a real review, not just a GUI-exposure slice

The existing `Evidence` and `EffectivenessVerification` models (`fmea_app/models.py` lines 531, 552) are minimal: `Evidence` is a name/description/URI attached to a `RecommendedAction`; `EffectivenessVerification` is a name/description/free-text result/timestamp, also attached to a `RecommendedAction`. Mockup 10 ("Evidence & Tests," 2026-09-03) shows something structurally different — a first-class **Validation Test** record with:

- a `Test Type` (Validation / Verification / Reliability / Acceptance)
- `Method` (e.g. "Photometric Test (Lab)") and `Objective` (free text)
- `Nominal / Target` and `Acceptance Criteria` (the pass/fail bar) as distinct fields from the measured `Result`
- a structured `Result` with a Pass/Fail badge — not free text
- `Planned Date` **and** `Executed Date` as two separate fields (today's `EffectivenessVerification` has only one `verified_at`)
- `Priority` (High/Medium/Low)
- a direct link to a DFMEA/`FailureMode` item ("Linked to DFMEA," "Open DFMEA Item") — the mockup's data model links a test to the FMEA line item under test, not necessarily through a `RecommendedAction` first
- multiple file attachments per record
- an `Owner` shown as a real person (avatar + name), not a free-text field
- its own 5-state status workflow: Planned / In Execution / Completed / On Hold / Cancelled — distinct from `ActionStatus`'s open/in_progress/completed/verified/cancelled

This is a new entity, not an extension of `Evidence`/`EffectivenessVerification` by a field or two. It needs its own review before any GUI or model work starts.

## 2. What already exists, and what doesn't

**Exists and reusable as-is:** the `RecommendedAction`→`FailureMode`/`FailureCause` link pattern (a `Test` could follow the same "link to a FailureMode/FailureCause, or to a RecommendedAction, whichever the workflow calls for" shape); `ResponsibleRole` as a possible `Owner` source *if* Owner stays a role-catalog reference rather than a real login account; the existing card/table/status-badge/theme.css visual components.

**Does not exist anywhere in this codebase, confirmed by direct check:**
- **File storage.** No `MEDIA_ROOT`, no `MEDIA_URL`, no `FileField`/`ImageField` anywhere in `fmea_app/models.py` or `open_fmea_project/settings.py`. This app also ships as a packaged Windows EXE (`packaging/`) — file storage location, size limits, and what happens to attachments when the EXE is rebuilt/redistributed are real questions with no existing answer, not just "add `FileField`."
- **A real per-person `Owner`.** Section 1's "Owner" in the mockup is a person with an avatar, not free text. `django.contrib.auth` is installed but essentially unused (Section 10's earlier finding, Mockup 6/7 audit) — no login flow, no user roster. Building a proper `Owner` field now either means a shallow "just a name string" placeholder (cheap, but not what the mockup shows and would need rework once the still-separately-flagged User/Role/Team system is built) or waiting on that system. This is the same dependency problem flagged for Mockup 9.
- **A DFMEA-item-first link.** Today's `Evidence`/`EffectivenessVerification` can only be reached via a `RecommendedAction`. The mockup's "DFMEA Link: F-01/FM-01" and "Open DFMEA Item" suggest a test can exist against a `FailureMode` (or a `Function`+`FailureMode` pair) directly, action-optional. That's a real modeling choice, not a detail.

## 3. Proposed design (for discussion, not yet decided)

A new entity — recommend `ValidationTest` (avoids colliding with either existing `Evidence` or `EffectivenessVerification` name) — with fields matching Section 1's list, minus file attachments and a real `Owner` account, both flagged as separate decisions below rather than assumed into scope. Existing `Evidence`/`EffectivenessVerification` are left as-is (not migrated, not deleted, per the DNA rule "nothing deleted from architecture, only superseded") — they continue to serve `RecommendedAction`'s own light evidence trail; `ValidationTest` becomes the answer to "Evidence & Tests" as its own nav page instead of trying to force the existing two small models to carry a UI they weren't shaped for.

`ValidationTest` link shape: FK to `FailureMode` (required) — matches "DFMEA Link: F-01/FM-01" in the mockup (Function + FailureMode, both already real fields) — and an optional FK to `RecommendedAction`, for when a test exists specifically to verify one action's effectiveness (this optional link is where `ValidationTest` and `EffectivenessVerification` overlap conceptually; Decision 3 below asks whether `EffectivenessVerification` should be retired in favor of `ValidationTest` for that specific case, or left alone).

Status workflow: `Planned` / `In Execution` / `Completed` / `On Hold` / `Cancelled` as its own enum, matching the mockup exactly — free-choice dropdown, no enforced transitions, consistent with `ActionStatus`'s existing precedent of not enforcing transitions absent a specific reason to.

## 4. Decisions Requiring Approval

1. **File attachments — build now, or defer?** Building them means designing storage (local filesystem under a new `media/` directory is the simplest fit for a single-machine/EXE-packaged app; no cloud storage exists or is implied anywhere else in this project) and packaging implications (what ships in the EXE, what's user data vs. app code). Recommend deferring attachments to a second increment — `ValidationTest` is fully useful without them, and this avoids deciding packaging/storage policy under time pressure.
2. **Owner — placeholder text field now, or wait for the User/Role/Team system?** Recommend a placeholder: reuse the existing `ResponsibleRole` catalog (already used by `RecommendedAction`) rather than inventing a second, redundant "just a name" field — keeps one owner/role concept in the app instead of two, and upgrades cleanly to a real per-person account later without a rename.
3. **Relationship to `EffectivenessVerification`.** Leave `EffectivenessVerification` alone (simplest, no migration risk, accepted duplication for one narrow case) — or treat `ValidationTest` (with its optional `RecommendedAction` link) as the superset and stop using `EffectivenessVerification` for new records going forward, without deleting/migrating existing rows (per the "nothing deleted, only superseded" rule)? Recommend the latter — avoids two parallel, overlapping "did this action work" mechanisms.
4. **Nav/page scope for this first increment.** A full standalone "Evidence & Tests" page (stat cards, filters, detail panel) matching the mockup, or a lighter first cut (a table + create form only, no donut charts/stat aggregation) with the fuller dashboard as a later refinement — same "full 10×10 grid vs. collapsed summary" style choice as the Risk Matrix review had.

## 5. What this review does not propose

No `System`/`System Characteristics Base`/`ClassificationScheme` dependency (unlike Mockup 8/9's items, `ValidationTest` stands on its own — it links to the already-real `FailureMode`, not to a not-yet-approved characteristics graph). No Validation Trajectory or Change Impact (the two other items in the mockups' "VALIDATION & CHANGE" nav group) — those remain separately deferred and this review does not fold them in. No AI involvement of any kind. No change to `Evidence`, `RecommendedAction`, or `ActionStatus`.

## Recommendation

**NOT YET READY** — unlike the Risk Matrix and Functions/Actions reviews, this one has a real new entity and at least one hard infrastructure decision (file storage) behind it, not just default-able UI judgment calls. Recommend deciding Section 4 first; a Codex instruction should not be written until at least Decisions 1–3 are settled (Decision 4 can reasonably default to "lighter first cut" without blocking).
