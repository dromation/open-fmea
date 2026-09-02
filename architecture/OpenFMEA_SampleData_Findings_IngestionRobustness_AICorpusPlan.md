# Findings — Real FMEA Sample Data: Ingestion Robustness Gap & AI Context-Corpus Plan

Status: Architecture findings and plan, grounded in direct execution of the actual Slice 1 ingestion code against real files — **not an implementation, not a Codex instruction. Do not implement until this is reviewed and a follow-up instruction is written**, per the standing convention for this project.

Reviewer/author: Claude, acting as Open-FMEA Technical Architect.

Scope: triggered by a request to look at `samples/open_fmea/` (a folder beside, not inside, the `open-fmea` git repository, at `D:\Dromation\org\apps\open_fmea\samples`). This folder contains real FMEA reference material that was never available during the Slice 1 XLSX ingestion review. This document reports what happens when that material is actually run through the just-reviewed ingestion pipeline, and lays out a plan — confirmed in scope with you — for turning real data into a prompting corpus for the existing AI boundary, without changing the "AI never authoritative, human review always required" principle.

## 1. What is in `samples/open_fmea/`

- `FMEA_templates.xlsx` — 7 sheets, one AIAG-style cover-sheet template per FMEA type: `PtFMEA`, `DFMEA`, `PFMEA`, `SFMEA`, `SWFMEA`, `OFMEA`, `Product FMEA`.
- `examples/FMEA_442710252570.00.xlsx` — a real, single-sheet PFMEA (casting/machining of a "Spigot D62" part), prepared by Janez Jurančič — genuine production data, not a synthetic sample.
- `examples/PPAP_Prirobnica.XX2.xlsx` — a real, 10-sheet PPAP package (`Articles`, `PFC`, `PFC_tabele`, `Prepare FMEA`, `FMEA_tabele`, `FMEA`, `Data-Drawings-Pictures`, `Histogram`, `QP`, `QP_tabele`), bilingual Slovenian/English, using AIAG-VDA-style rating labels (`Po`/`S`/`Pd`) and a `CTQ Y/N?` column instead of the classic RPN-only layout.
- `open_fmea` — a SQLite database, the legacy Tkinter prototype's schema (one near-duplicate flat table per FMEA type: `fmea_design`, `fmea_process`, `fmea_product`, etc., plus never-populated lookup tables `CAUSES`/`CONTROLS`/`EFFECTS`/`SFC`/`SOD`). Every table has **0 rows** — this is a schema artifact only, there is no historical data to migrate.
- `example_sets/`, `supervision_sets/`, `test_sets/`, `training_sets/` — empty directories.

Three files are usable as ingestion test material: the templates workbook and the two real examples.

## 2. Ground truth: running the actual Slice 1 parser against these files

Rather than reason about what the parser *should* do, I ran `fmea_ingestion.parsers.xlsx.parse_xlsx_workbook` — the exact function reviewed and accepted in the Slice 1 review — directly against all three files.

| File | Result |
|---|---|
| `FMEA_templates.xlsx` | 171 candidates produced, **171 unmapped (100%)** |
| `FMEA_442710252570.00.xlsx` (real) | 84 candidates produced, **84 unmapped (100%)** |
| `PPAP_Prirobnica.XX2.xlsx` (real) | **`AmbiguousWorkbookError` — the entire file fails to import, zero candidates** |

None of the three files available for testing produces a single usable candidate today. This is a materially stronger finding than "the header vocabulary needs broadening" — the header-detection step itself is misfiring on real files, before vocabulary ever comes into play.

### Finding A (severe) — header detection locks onto the cover-sheet metadata rows, not the real table header

`_find_header_row()` picks the first row with ≥2 non-empty cells within a 20-row scan. Every AIAG-style template places its cover-sheet metadata in label/value pairs above the real table — and those pairs already clear the ≥2 threshold several rows before the real header. Verified directly on `FMEA_templates.xlsx`'s `PtFMEA` sheet:

```
row1: 0 non-empty
row2: 1 non-empty -> ['Risk Failure Mode and Effect Analysis (RFMEA)']
row3: 1 non-empty -> ['POTENTIAL FAILURE MODE AND EFFECTS ANALYSIS (RISK FMEA)']
row4: 3 non-empty -> ['Item', 'Potential Risk Responsibility', 'PFMEA Number']   <- parser stops here
row5: 3 non-empty -> ['Product Name & Model', 'Key Date', 'Prepared by']
row6: 3 non-empty -> ['Core Team', 'Date (Original)', 'Date (Revised)']
row7: 13 non-empty -> ['Op Seq #', 'Process/ Product/ Function/ Requirment', 'Product Characteristics ID/Description', 'Potential Failure Mode', ...]   <- the real header
```

The parser locks onto row 4, treats "Item" / "Potential Risk Responsibility" / "PFMEA Number" as column headers, and ingests every row below — including the real header row 7 and every real data row — as ordinary cell values under those three wrong labels. That's why the output is 100% unmapped: the "column names" the mapper sees (`Item`, `PFMEA Number`, `442710252570`, `Leopold Volčič`, even a literal `1`) don't match anything in `DEFAULT_HEADER_MAPPINGS`, because they aren't real column names at all. This is not an edge case specific to one file — every one of the 7 template sheets and the real PFMEA example fails identically, because the AIAG cover-sheet layout is the standard shape.

### Finding B (severe) — one bad worksheet aborts the entire multi-sheet workbook

`parse_xlsx_bytes` iterates every worksheet and raises `AmbiguousWorkbookError` (via `_find_header_row`) on the first one it cannot find a header for, aborting the whole import — no per-sheet isolation. Running header detection sheet-by-sheet on `PPAP_Prirobnica.XX2.xlsx`:

```
'Articles'               -> FAILS (no discernible header)
'PFC'                    -> header at row 1
'PFC_tabele'             -> FAILS
'Prepare FMEA'           -> header at row 1
'FMEA_tabele'            -> header at row 3
'FMEA'                   -> header at row 2
'Data-Drawings-Pictures' -> FAILS (embedded images, no cell grid)
'Histogram'              -> header at row 1
'QP'                     -> header at row 3
'QP_tabele'              -> header at row 2
```

Seven of ten sheets do find *some* row (usually still the wrong one, per Finding A). But because `Articles`, `PFC_tabele`, and `Data-Drawings-Pictures` fail, the whole file is rejected — including the `FMEA` sheet, which is the one actually worth ingesting. A real multi-tab workbook — the normal shape for a PPAP package — is currently all-or-nothing against three sheets that were never meant to hold a tabular FMEA anyway.

### Finding C — real header vocabulary, once actually reached, is broader than `DEFAULT_HEADER_MAPPINGS`

This is the finding I described conversationally before running the parser; it's confirmed but subordinate to A and B — it only manifests once the real header row is correctly located. Headers observed in the real files that have no entry in `column_mapping.DEFAULT_HEADER_MAPPINGS`:

- `Op Seq #`, `Product Characteristics ID/Description`, `Classification`, `Responsibility Completion Date`, and the `Action Results` block (`Actions Taken & Completion date`, second `Severity`/`Occurrence`/`Detection`/`RPN`) — from the AIAG template/real PFMEA.
- `Po`, `S`, `Pd`, `CTQ Y/N?`, `Testing - Simulation`, `Recommended action`, `Planned action`, `Follow up date`, `Verifications-Sign` — from the bilingual PPAP `FMEA` sheet, which also uses a different rating-label convention (`Po`/`S`/`Pd`) than the classic RPN template.
- The real table headers also span **two physical rows** (a main label row plus a sub-label row for the merged Prevention/Occurrence/Detection and Action-Results blocks) — `_find_header_row` only ever considers a single row, so even a correctly-located header would still miss the second row's sub-labels today.

`Product Characteristics ID/Description` and `Classification`/`CTQ` appearing in two independent real customer templates is a concrete, external confirmation that the not-yet-approved Characteristics/Ishikawa domain model review is asking for something real FMEA authors already track by hand — worth noting, but this document does not propose building that classification logic; it's still correctly gated behind that separate review's approval, exactly as the Slice 1 Codex instruction required.

## 3. Why Slice 1's own test suite didn't catch this

The 24 passing tests are all genuine and correct — they just never exercised a cover-sheet-shaped or multi-sheet-with-a-non-tabular-sheet file. `tests/fixtures/sample_fmea_minimal.xlsx` and `sample_fmea_prompt_injection.xlsx` are single-sheet, single-header-row fixtures built to exercise the mapping and review-workflow logic, not header-detection robustness against the shape real FMEA authors actually use. That gap is exactly what looking at `samples/` surfaced.

## 4. AI context-corpus plan (confirmed scope: prompting corpus, not model training)

You confirmed this should stay within the existing boundary: a data corpus to improve `extract_structured_data` prompting/context, not fine-tuning, not a change to the human-review-gate principle, and no new `AiProvider` methods.

**What already exists as "training conditions" for this, with nothing new built:**

1. **The `samples/` files themselves**, once Findings A/B are fixed, become header-vocabulary and phrasing ground truth — real column names, real bilingual phrasing, real cause/effect/control language — useful as static few-shot context for the `extract_structured_data` prompt. This is a small, single-company, single-domain (casting/machining) sample — good for grounding realistic *shape and phrasing*, not broad enough alone to generalize across arbitrary customer FMEAs.
2. **The review queue itself is already a growing labeled corpus, with zero new schema.** Every `ImportCandidateRecord` transition — `UNREVIEWED → ACCEPTED`, `→ MODIFIED` (with the corrected `extracted_value`/`suggested_domain_type`), `→ REJECTED` (with `review_note`) — is a real (raw cell text → human-confirmed correct interpretation) pair, produced as a side effect of normal use of the workflow just reviewed. Nothing needs to be built to start accumulating this signal; it only needs to be read back out later.

**Concrete, small next step (not authorized to build yet — needs its own short review, per house convention):**

A read-only export path — e.g. a management command — that serializes `ACCEPTED`/`MODIFIED` `ImportCandidateRecord`s into a versioned "context examples" file (raw cell text, source column header, corrected type/value). That file becomes optional few-shot context passed into `extract_structured_data`'s prompt in `ollama_provider.py`, sampled/selected however the next review specifies. This stays entirely inside the already-approved AI boundary: still one method (`extract_structured_data`), still schema-validated on the way back, still degrades to pure deterministic mapping when absent or when AI is disabled, still never bypasses Accept/Reject/Modify. No new `AiProvider` methods, no embeddings, no vector store, no fine-tuning — explicitly the same exclusions as the original AI/ingestion architecture review.

## 5. Recommendation — two independent follow-ups, both need their own review before a Codex instruction

1. **Ingestion robustness fix (should come first — this blocks any real file, not just an enhancement).** Fix `_find_header_row` to look past cover-sheet metadata rows to the actual table header (e.g., require a minimum column count, or score candidate rows against the *existing* `DEFAULT_HEADER_MAPPINGS` vocabulary rather than a bare non-empty-cell count), add per-sheet error isolation to `parse_xlsx_bytes` so one non-tabular sheet doesn't abort the whole workbook, add second-row sub-header merging, and broaden `DEFAULT_HEADER_MAPPINGS` with the vocabulary observed in section 2 (including the Slovenian/bilingual and `Po`/`S`/`Pd`/`CTQ` variants). Same package boundaries as Slice 1 (`fmea_ingestion`/`fmea_review` only) — this is a scoped enhancement to already-implemented code, not a new capability class.
2. **AI context-corpus export (independent, smaller, lower urgency).** The read-only export + prompt-context wiring described in section 4.

I have not written a Codex instruction for either — following the standing rule for this project, that comes after you've reviewed this document and told me which of the two (or both) to proceed with, and in what order.
