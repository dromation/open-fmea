# Codex Implementation Instruction — FMEA Projects List Page + Team Roster (Phase 2a)

Status: Approved for implementation. Merges `OpenFMEA_ProjectsTeamRoster_ArchitectureReview.md` (this session's architecture review) with the compatible parts of `Codex_Instruction_GUI_Mockup_Implementation_Preparation.md`'s Slice B (the implementing session's own page-inventory/route proposal) — the user asked for the two to be combined 2026-09-03. Corresponds to mockups 5 (FMEA Projects List) and 6 (FMEA Team).

Authority, in order: same chain as prior slices. Two assumptions below (Section 0.3, 0.4) are stated as decisions rather than left open, per the user's direction to move forward — flag clearly in your report if either seems wrong once you're looking at the real data, rather than silently building around a bad assumption.

## 0. Decisions for this slice

1. **Two logical pieces, one instruction.** Projects list page (Tier A/C — data exists, page doesn't) and Team roster (Tier D — new model) ship together since the user asked to merge the two plans, but they remain scoped separately below (Section 1 Part 1 / Part 2) — don't let Team's larger footprint bleed into Part 1's scope.
2. **Team roster is Phase 2a only: roster + role labels, no login/permissions.** `django.contrib.auth`'s `User` model is used only as a name/email holder for membership rows — no login flow, no password setup, no per-role access control anywhere. A "Viewer" and an "Administrator" see identical pages in this phase. This matches both this session's architecture review and the implementing session's own independent conclusion in `Codex_Instruction_GUI_Mockup_Implementation_Preparation.md` Slice B ("do not build login/permissions") — two independent sources converged on the same scope, which is a good sign, not a coincidence to second-guess.
3. **`PROJECT_STATUS_CHOICES`: `active`, `on_hold`, `completed`, `archived`.** Stated as the working assumption (the mockup's exact status vocabulary wasn't fully legible in prior audits). If you can read the actual status labels more precisely from the mockup image itself (`architecture/mockups/mockup-05-fmea-projects-list.png`) once building this, use those instead and note the correction in your report — don't block on it.
4. **The five role labels (Administrator / FMEA Leader / PM-FMEA Responsible / Contributor / Viewer) are inert text, no behavior.** In particular, "PM-FMEA Responsible" existing as a role label does not imply building anything PM-FMEA/Asset/Maintenance-specific — that track stays held off per the standing Mockup 3 decision. The role is just a string stored on `ProjectMembership.role`.

## 1. Exact Scope

### Part 1 — FMEA Projects List Page

1. Extend `FMEAProject` (`models.py`):
   ```python
   PROJECT_STATUS_CHOICES = [
       ("active", "Active"),
       ("on_hold", "On Hold"),
       ("completed", "Completed"),
       ("archived", "Archived"),
   ]
   project_code = models.CharField(max_length=64, blank=True)
   status = models.CharField(max_length=32, choices=PROJECT_STATUS_CHOICES, default="active")
   ```
2. New view + template, route `fmea/projects/` (`fmea:project_list`): stat cards (Total, Active, On Hold, Completed — trivial `.count()` queries), a table (Name, Project Code, Status, FMEA count via `project.fmeas.count()`, FMEA-type breakdown via `project.fmeas.values('fmea_type').annotate(...)`, last-updated), each row linking to detail.
3. New view + template, route `fmea/projects/<str:stable_id>/` (`fmea:project_detail`): project metadata, list of the project's FMEAs (reuse existing FMEA rendering patterns where practical), and the Team tab from Part 2.
4. Extend the existing `/projects/create/` form (`create_project` view, whatever form it uses today) to include `project_code` and `status`.
5. "Related Product/Process" from the mockup: compute via `project.fmeas.all()`'s `products`/`processes` at render time — do not add a stored field for this.

### Part 2 — Team Roster (Phase 2a)

1. New model `ProjectMembership` (`models.py`, same `StableModel` base pattern as other entities):
   ```python
   class ProjectMembership(StableModel):
       ROLE_CHOICES = [
           ("administrator", "Administrator"),
           ("fmea_leader", "FMEA Leader"),
           ("pm_fmea_responsible", "PM-FMEA Responsible"),
           ("contributor", "Contributor"),
           ("viewer", "Viewer"),
       ]
       project = models.ForeignKey(FMEAProject, related_name="memberships", on_delete=models.CASCADE)
       user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="project_memberships", on_delete=models.CASCADE)
       role = models.CharField(max_length=32, choices=ROLE_CHOICES)
   ```
   Adjust field names/base class to match this codebase's actual conventions if `StableModel`'s exact shape requires it (check an existing simple model like `ResponsibleRole` for the pattern) — the point is the three fields (project, user, role), not the exact base-class mechanics.
2. New view + template, route `fmea/projects/<str:stable_id>/team/` (`fmea:project_team`, matches `Codex_Instruction_GUI_Mockup_Implementation_Preparation.md`'s proposed route): table of members (name, email, role badge), an "Add member" form (pick an existing `User` by email, or create one inline with first/last name + email — no password field anywhere on this form), a remove-member action.
3. No changes to any existing view's access control. No login page, no session/permission checks added anywhere.

## 2. Exact Allowed / New Files

```text
django_app/fmea_app/models.py          # FMEAProject fields (Part 1), new ProjectMembership model (Part 2)
django_app/fmea_app/migrations/000X_....py   # one new migration, both model changes together is fine
django_app/fmea_app/forms.py           # extend project-create form; new ProjectMembership form
django_app/fmea_app/views.py           # project_list, project_detail, project_team, add/remove membership
django_app/fmea_app/urls.py            # the three new routes
django_app/fmea_app/templates/fmea_app/project_list.html      # new
django_app/fmea_app/templates/fmea_app/project_detail.html    # new
django_app/fmea_app/templates/fmea_app/_project_team_tab.html # new (included from project_detail.html)
django_app/fmea_app/templates/fmea_app/_sidebar.html          # add "FMEA Projects" as a real nav link (it's Tier A per the mockup audit — currently only an anchor link)

tests/test_projects_list_and_team_roster.py   # new
```

## 3. Required Validation and Explicit Exclusions

- No login flow, no password field, no permission/access-control change anywhere — Phase 2a only (Section 0.2).
- No PM-FMEA/Asset/Maintenance behavior of any kind tied to the "PM-FMEA Responsible" role label (Section 0.4).
- No new field on `FMEAProject` beyond `project_code`/`status` — "Related Product/Process" and any FMEA-count/type-breakdown are computed, not stored (Section 1 Part 1.5).
- `ResponsibleRole` (the existing free-standing role catalog used by `RecommendedAction`) is untouched and unrelated to `ProjectMembership.role` — don't merge or cross-reference the two, they're different concepts that happen to share the word "role."
- One migration is acceptable for both model changes; run `manage.py makemigrations --check --dry-run` before committing to confirm nothing else drifted.

## 4. Required Tests

- `test_projects_list_and_team_roster.py`: render the projects list page and assert stat cards + at least one project row; create a project via the extended form and assert `project_code`/`status` persist; render a project detail page and assert its FMEAs are listed; add a team member via the team page and assert the `ProjectMembership` row exists and renders with its role badge; remove a member and assert the row is gone. Use `self.client.get`/`self.client.post` throughout (real HTTP requests), consistent with every other GUI test file in this project.
- Full existing suite re-run with no unrelated assertion changes.

## 5. Commands to Run

```powershell
python -B manage.py check
python -B manage.py makemigrations --check --dry-run
python -B -m pytest
```

## 6. Acceptance Criteria

1. `fmea/projects/` lists real `FMEAProject` rows with working stat cards and per-project FMEA counts/type breakdowns.
2. `fmea/projects/<stable_id>/` shows project metadata and its FMEAs.
3. `fmea/projects/<stable_id>/team/` shows real `ProjectMembership` rows; add/remove works through real forms.
4. No login, password, or permission-check code appears anywhere in the diff.
5. No PM-FMEA-specific logic appears anywhere in the diff.
6. `_sidebar.html` gains a real "FMEA Projects" link (replacing the anchor-only entry, if one exists) — no other nav change.
7. Full test suite passes, `manage.py check` clean, exactly one new migration.
8. Mirrored into `open_fmea_training_set` per the standing discipline.

## 7. Explicit Exclusions (restated for emphasis)

No authentication/login system. No permission enforcement. No PM-FMEA/Asset/Maintenance track. No merging `ProjectMembership.role` with `ResponsibleRole`. No stored "Related Product/Process" field. No other mockup (beyond 5 and 6) implemented as part of this slice — the rest of `Codex_Instruction_GUI_Mockup_Implementation_Preparation.md`'s page inventory stays reference material only; each further slice still needs its own go-ahead the same way this one just got it, not a blanket green light from that document alone.

If you believe any of this needs to change to deliver a working slice, stop and report — do not silently expand scope.
