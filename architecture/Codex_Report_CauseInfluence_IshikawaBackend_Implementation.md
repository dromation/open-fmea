# Codex Report — CauseInfluence, CauseCategoryScheme, Ishikawa Backend Slice

Date: 2026-09-01
Repositories:

- `D:\Dromation\org\apps\open_fmea`
- `D:\Dromation\org\apps\open_fmea_training_set`

## Verdict

Implemented and verified in both the main repo and the training-set copy.

This slice adds the first real Ishikawa backend capability: configurable 5M+E categories, governed cause-influence edges, status-transition rules, OFEF round-trip support, and a list-form Ishikawa review GUI. The visual fishbone diagram, Product/ProcessCharacteristic linking, and AI category classification remain deliberately outside this slice.

## Implemented

- Domain entities: `CauseCategoryScheme`, `CauseCategory`, `CauseInfluence`, `CauseInfluenceStatus`.
- Framework-free rule: `validate_cause_influence_transition`.
- Django models/admin/migration for the three persisted entities.
- Idempotent seed command: `seed_cause_category_scheme`.
- Services:
  - `create_cause_influence`
  - `transition_cause_influence`
  - `legal_cause_influence_transition_statuses`
- GUI:
  - `/cause-influences/`
  - `/cause-influences/new/`
  - `/cause-influences/<stable_id>/`
  - `/failure-modes/<stable_id>/ishikawa-board/`
- OFEF import/export support for the new domain entities.
- Domain documentation: `docs/domain/cause-influence.md`.
- Demo seed rows so the training EXE opens with visible Ishikawa data:
  - `demo:cause-influence:seal-nicked-method`
  - `demo:cause-influence:sharp-edge-machine`

## Boundaries Preserved

- `source_type` is limited to `FailureCause` and `FailureMechanism`.
- `target_type` is limited to `FailureMode` and `FailureCause`.
- `CauseInfluence` category is edge-level, not source-object-level.
- `confirmed_root_cause` cannot target `FailureMode`.
- Confirming a `FailureMode`-targeted influence requires explicit retargeting to a real `FailureCause`.
- `rejected` and `confirmed_root_cause` are terminal states.
- AI classification is not wired; no AI output can create, transition, reject, or confirm a cause influence.

## Verification

Executed in `D:\Dromation\org\apps\open_fmea`:

```text
python -B -m pytest
69 passed

python manage.py check
System check identified no issues

python manage.py makemigrations --check --dry-run
No changes detected

python manage.py migrate --noinput
fmea_app.0002 and fmea_review.0002 applied

python manage.py seed_cause_category_scheme
Seeded cause-category scheme: cause-category-scheme:ishikawa-5me-default
```

Executed in `D:\Dromation\org\apps\open_fmea_training_set`:

```text
python -B -m pytest
69 passed

python manage.py check
System check identified no issues

python manage.py makemigrations --check --dry-run
No changes detected

source parity check
No source drift in checked paths

packaging/build_exe.ps1
69 passed
System check identified no issues
No changes detected
Built EXE:
D:\Dromation\org\apps\open_fmea_training_set\dist\OpenFMEA-Training\OpenFMEA-Training.exe
```

Training EXE smoke test:

```text
BaseUrl: http://127.0.0.1:8765
Ishikawa Review page: OK
New Cause Influence page: OK
Default 5M+E categories: OK
Ishikawa Board page: OK
Demo Method group: OK
Demo Machine group: OK
```

The training EXE server was also changed from single-threaded WSGI to threaded WSGI, because browser keep-alive connections could block later local requests during smoke testing.

## Still Deferred

- Visual Ishikawa fishbone diagram GUI.
- `ProductCharacteristic` rename.
- `ProcessCharacteristic`.
- Widening `CauseInfluence` to characteristic objects.
- `classify_ishikawa_category` AI wiring.
- RAG, embeddings, retrieval, and model training.
