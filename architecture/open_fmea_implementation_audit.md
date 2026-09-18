# Open FMEA v1.8 stabilization audit — 2026-09-13

## Supplied baseline comparison

Before editing, the supplied v1.8 HTML embedded container and adjacent focus `.container` were semantically identical, schema `1.8.1-dfmea`, with eleven DFMEA records. The separate validation seed used schema `1.8.0` and six DFMEA records. It was not synchronized with the focus dataset. The original seed is retained in history as migration evidence; it was not silently merged into the authoritative dataset.

The supplied validation JSONL, AI knowledge JSONL, pipeline JSON/Markdown, release history, historical HTML/JSON/container/SQL/SQLite files and implementation prompts were inspected. Historical release checksums were checked against the files. Earlier fixes were treated as engineering evidence rather than assuming the latest version was correct. Original v1.8 files were copied to a dated backup before editing; that backup is now under history with the old versions.

## Implemented corrections

- Restored PFMEA rendering after a missing `kpis` helper regression, removed duplicate risk classification implementation and removed obsolete DFMEA filtering code.
- DFMEA tabs share project-scoped source records, reusable functions/elements/failure modes/effects/causes, control links, filters, selection and detail context.
- Replaced static DFMEA trend/action/date values with linked action counts, actual due dates and dated risk observations. Completed actions do not manufacture lower risk. Legacy RPN inconsistencies are visible and require explicit rating review.
- Added reviewed DFMEA CRUD, immutable audit snapshots, atomic JSON/CSV validation, portable import/export, recovery from malformed browser state, interface relationships and editable parameter diagrams.
- Retained one global navigation across 34 pages, including Ishikawa, WHY, 8D, Poka-Yoke and learning. DFMEA adapts to seven viewport widths; dense tables scroll locally. Mockup images remain unchanged.
- Analysis forms save source records; learning drafts preserve provenance. Approval requires evidence and completed validation. Imported approval claims do not silently authorize new cases.
- Added the in-browser Diagnostics / Validation engine, findings, linked change impacts, non-authoritative candidates and explicit human review before application Design FMEA creation.
- Established root `open_fmea.html` as the sole canonical runtime and synchronized its embedded baseline with root `open_fmea.container`, knowledge, definitions, pipeline and optional database snapshots. Archived historical HTML versions without removing unrelated application/backend work.

## Verification and limits

The optional development reports record page rendering, common navigation, DFMEA CRUD and rating history, import/export, analysis learning, candidate review and responsive tests. Standalone verification runs the HTML alone using a file URL with network disabled. The in-browser baseline check reports 23 passing checks and four failing legacy-data categories; these failures are expected findings, not a claim that the engineering dataset is valid.

The four categories are RPN mismatch (18 records), unresolved references, four orphan actions, and missing validation links for DF-005/DF-006. Diagnostics provides the exact current IDs. The supplied historical approval status of old learning cases is retained and labeled; it was not reapproved by this development run.

Exact pixel-level/controlled visual acceptance of all 23 mockups has not been established. Pages outside the DFMEA focus still contain legacy reference widgets and planned functionality. Rendering all pages successfully does not imply all page-specific CRUD/authority workflows are complete. Large-dataset performance, multi-user access control and backend integration are outside this single HTML stabilization verification. The new development learning case therefore remains a draft.
