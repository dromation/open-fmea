# Single HTML runtime

```text
open_fmea/
├── open_fmea.html                 sole canonical HTML runtime
├── open_fmea.container            portable initial dataset
├── knowledge/
│   ├── open_fmea_ai_knowledge.jsonl
│   └── engineering_knowledge.md
├── database/
│   ├── open_fmea.sqlite
│   └── open_fmea.sql
├── architecture/
│   ├── open_fmea_dataflow_pipeline.json
│   ├── open_fmea_dataflow_pipeline.md
│   ├── open_fmea_validation_tests.jsonl
│   ├── open_fmea_release_history.json
│   └── mockups/                   unchanged controlled references
├── history/
│   └── html-releases-2026-09-13/chat_version/
└── development/tests/
    ├── smoke.cjs
    └── verification.cjs
```

Existing backend, domain and other application source directories were retained. They are not dependencies of this HTML runtime. Archived HTML files are historical engineering evidence and are not application entry points.

## Run and save

Open `open_fmea.html` directly with a current browser. It includes CSS, JavaScript, starting data, navigation, DFMEA views, analysis forms, calculations, migration, audit, learning and validation. It works offline without a companion file. Browser storage is local to the browser/file context. Save Container explicitly downloads changes; Open Container explicitly loads portable data. JSON/CSV are record interchange formats; JSONL imports learning cases as drafts.

All runtime components are inside the HTML IIFE, exposed through `window.OpenFMEA`: State, Repository, Commands, Queries, Calculators, Validators, Transactions, Learning, Knowledge, ImportExport, Diagnostics, DataFlow and UI. These are in-memory interfaces, not separate scripts or packages. Views use the same repository. The derived search index is rebuilt from source records at startup.

## Validation

Diagnostics / Validation executes data and UI checks inside the HTML, stores test runs, deduplicates findings, links change impacts and supports candidate review. It can import JSONL/JSON definitions, export results and compare an external container with active state. Rendering checks cover every navigation page and DFMEA subview, inspect the current viewport and check that rendering does not mutate engineering data. Exact mockup parity remains a human review step; broader manual requirements are not marked accepted by the automated checks.

Optional development checks use Node and Playwright with installed Chrome:

```text
node development/tests/smoke.cjs
node development/tests/verification.cjs
```

These tools are not required by users of the application. Tests use isolated browser contexts and file URLs. Verification additionally copies only the HTML to an empty temporary folder and runs offline. Reports and screenshots are written beside the tests. Install Playwright in the development environment or set `OPEN_FMEA_PLAYWRIGHT_PATH` to its package path.

## Companion snapshots

`database/open_fmea.sqlite` and `.sql` contain the same normalized baseline as the container. The snapshot schema preserves arbitrary source records as JSON: `snapshot_meta(key,value_json)` stores non-array values and collection lengths; `snapshot_records(collection,ordinal,object_id,payload_json)` stores ordered array elements. Empty collections and source ordering are preserved. These files support interchange/reporting and are not a live database behind the HTML. Original database files remain in history.

The current release checksum is recorded externally in `open_fmea_release_history.json` to avoid a self-referential embedded hash. Historical entries identify archived files and retain verified original checksums.
