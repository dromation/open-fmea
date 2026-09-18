# Open-FMEA Architecture Review — FMEA Projects List Page + Team/Role Roster

Status: Architecture review, not yet approved for implementation. Written 2026-09-03, per the user's direction to prioritize Mockup 5 (FMEA Projects list) + Mockup 6 (FMEA Team) as the next slice after today's `v1.0.0` tag.

Scope note up front: **these two mockups are not the same size of problem**, and this review keeps them separate rather than silently treating "Projects page + Team" as one uniform slice. Mockup 5 is a Tier A/C gap-close (real data exists, page and a few fields don't). Mockup 6 is Tier D — a real user/role/permissions system that doesn't exist in any form today. Bundling them into one Codex instruction risks exactly the kind of scope mismatch this project's discipline exists to catch (see `Claude_Review_FunctionsActions_Implementation_ScopeCorrection.md` for the last time an instruction's literal text didn't match the real model). This review proposes treating them as two instructions, sequenced, not one.

## 1. What's real today (grounding, re-confirmed directly against `models.py`)

- `FMEAProject` exists (`models.py:61`): `name`, `description` only. No Project Code, Owner, Status, Progress %, or team.
- `FMEA` already has `project = models.ForeignKey(FMEAProject, null=True, blank=True, related_name="fmeas", ...)` — so `project.fmeas.all()` and `project.fmeas.count()` already work; a per-project FMEA count and FMEA-type breakdown need no new field, just a query.
- `Product`/`Process` are FK'd to `FMEA`, not to `FMEAProject` directly — so a project's "related products/processes" is an aggregation across `project.fmeas.all()`'s products/processes, not a new FK on `FMEAProject`.
- `FMEA.fmea_type` (design/process/product/software/system) and `FMEALifecycle` (draft/in_review/approved/superseded/obsolete, in `domain/fmea_domain/entities.py`) exist at the **FMEA** level. `FMEAProject` has no status field of its own today.
- Today's only "FMEA Projects" GUI is an anchor link into a Home dashboard section (`#fmea-projects`), not a standalone page. `/projects/create/` exists (used by `test_app_workflow.py`) but there is no list/detail view.
- `django.contrib.auth` is installed (`AUTH_USER_MODEL` is referenced once, as `CauseInfluence.reviewed_by`) but otherwise unused: no login flow, no per-user roles, no permission checks anywhere in `views.py`.
- `ResponsibleRole` (`models.py:467`) exists but is a plain name/description catalog (e.g. "Quality Engineer") used as a free-standing label on `RecommendedAction` — it is not a roster of people, has no link to a `User`, and isn't scoped to a project or FMEA.

This matches and slightly extends the Tier A/C/D breakdown already recorded in `OpenFMEA_DNA_CoreReference.md`'s Mockup 5/6 catalog entry (2026-09-03) — that entry is the authoritative source for the full mockup-vs-model audit; this review only adds the specific FK/query facts needed to scope real work.

## 2. Part 1 — FMEA Projects List Page (Mockup 5)

### 2.1 Proposed entity change

Extend `FMEAProject` with the fields the mockup actually shows as project-level data (not derivable from existing FKs):

```python
class FMEAProject(StableModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    project_code = models.CharField(max_length=64, blank=True)
    status = models.CharField(max_length=32, choices=PROJECT_STATUS_CHOICES, default="active")
    # Owner: see Section 3 — deliberately NOT added here if Part 2 is deferred (see Section 4)
```

`PROJECT_STATUS_CHOICES` — proposed minimal set matching what the mockup needs for a status pill/filter: `active`, `on_hold`, `completed`, `archived`. This is a project-management status, independent of any individual FMEA's `FMEALifecycle` — do not conflate the two.

"Progress %" from the mockup: recommend **not** a stored field — derive it from `FMEALifecycle` states across the project's FMEAs (e.g., `approved / total` as a percentage), computed at render time. A stored, separately-maintained progress percentage would drift from reality; a computed one can't.

### 2.2 Proposed GUI surface

- New page `fmea/projects/` (list): stat cards (Total Projects, Active, On Hold, Completed — trivial counts), a filterable/sortable table (Name, Project Code, Status, FMEA count, FMEA-type breakdown, last-updated), each row linking to a project detail page.
- New page `fmea/projects/<stable_id>/` (detail): project metadata, the list of FMEAs in the project (reusing existing FMEA list rendering where possible), and — only if Part 2 is approved — a Team tab (Section 3.2).
- `/projects/create/` already exists and needs no change beyond adding `project_code`/`status` to the form.

### 2.3 Explicit exclusions for this part

No PM-FMEA `fmea_type` value (still held off per the Mockup 3 decision — a project's stat-card breakdown by type just omits "preventive" until that's decided separately). No "Related Product/Process" as a stored field — computed via the FK chain in Section 1. No Import/Export/Reports/Templates/Filters toolbar actions from Mockup 5 beyond what's listed above — those are separate, uncataloged asks.

## 3. Part 2 — Team / Role Roster (Mockup 6)

This is the one that needs the most explicit user decision before any instruction is written — it is genuinely new infrastructure, not a gap-close.

### 3.1 What the mockup actually asks for vs. what a minimal real version could be

The mockup shows a member roster with named roles (Administrator, FMEA Leader, PM-FMEA Responsible, Contributor, Viewer) that read like **permission levels** (who can edit vs. view), not just descriptive labels. Building that literally — real login accounts, role-based permission enforcement on every view — is a substantial, cross-cutting change (every existing view would need an access-control decision) and is well beyond "expose an existing model in the GUI," the pattern every prior slice in this project has followed.

Recommend splitting this into two clearly separate pieces, and only approving the first for now:

- **Phase 2a (data + GUI only, no enforcement):** a `ProjectMembership` model — `project` (FK to `FMEAProject`), `user` (FK to `AUTH_USER_MODEL`), `role` (the five labels from the mockup, stored as a plain choice field, same pattern as `ResponsibleRole`) — plus a Team tab on the project detail page listing members and a simple add/remove form. This makes the roster *real and visible*, matching what most of Mockup 6's visual surface actually shows (a table of names + role badges), without touching authentication or permissions anywhere. `django.contrib.auth`'s `User` model is used only as a name-holder here (first/last name, email) — no login flow is added or required for this phase; a `User` row can be created without ever being used to log in.
- **Phase 2b (not proposed here, needs its own review if wanted later):** actual login, session-based access, and role-based permission enforcement (an "Administrator" can edit, a "Viewer" cannot). This is a materially different, larger project — real authentication UX, password/session handling, and a permission-check layer across every existing view — and should not be silently bundled into "add a Team tab."

### 3.2 Proposed GUI surface (Phase 2a only)

- Team tab on the project detail page (Section 2.2): table of members (name, role badge, added date), an "Add member" form (pick an existing `User` or create one inline with name/email — no password/login setup), remove-member action.
- No changes to any existing view's access control. No login page. No "who am I logged in as" concept beyond what already exists (the one `is_authenticated` check used for activity-log actor names).

### 3.3 Explicit exclusions for this part

No permission enforcement (Phase 2b, not this review). No password/login flow. No per-role capability differences in the GUI itself (a "Viewer" sees the exact same pages as an "Administrator" in Phase 2a — the role is a label, not a gate). No change to `ResponsibleRole` (stays as-is, a separate free-standing catalog for `RecommendedAction`, not merged with project membership roles — they're different concepts even though both use the word "role").

## 4. Open decisions — need explicit confirmation before a Codex instruction is written

1. **Split into two instructions (Projects list page; Team roster Phase 2a), or one combined?** This review recommends two, sequenced, given the size and risk mismatch (Section 3.1). If the user wants them combined anyway, say so explicitly — but the Team piece should still be scoped to Phase 2a only either way.
2. **`PROJECT_STATUS_CHOICES` — are `active`/`on_hold`/`completed`/`archived` the right four states?** The mockup's exact status vocabulary wasn't fully legible in prior audits; confirm or supply the exact set before an instruction locks in a migration.
3. **Team roster (Phase 2a) — confirm no login/permissions is acceptable for this pass.** If the user actually wants real per-role access control now (Phase 2b), that changes this into a much larger review, not a slice — flag that explicitly rather than assume.
4. **"PM-FMEA Responsible" role label** — Section 3 proposes keeping the five role labels as inert text (no behavior tied to "PM-FMEA" specifically), consistent with the still-held-off PM-FMEA/Asset/Maintenance track from Mockup 3. Confirm this is acceptable, i.e. the role label existing doesn't imply building anything PM-FMEA-specific.

Once these are answered, this review converts directly into one or two `Codex_Instruction_*.md` documents, following the same exact-scope/exact-files/acceptance-criteria pattern as every prior slice.
