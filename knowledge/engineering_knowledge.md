# Open FMEA engineering knowledge

The canonical application is `../open_fmea.html`. Open it directly in a browser. Its embedded container provides a complete starting dataset. No knowledge file, database, server or development tool is needed to run the application.

The active repository is in browser memory, with local browser persistence. Use Save Container to download a portable snapshot; use Open Container to load one. The application cannot silently update the adjacent file on disk. The supplied `../open_fmea.container` is synchronized with the embedded starting dataset, not with subsequent edits in an individual browser.

## Analysis and learning

Ishikawa 5M/6M, 3WHY/5WHY, 8D D0–D8 and Poka-Yoke retain their analysis records. A learning draft includes its source ID, a source snapshot, cause, corrective action, observed result and method. Approval requires explicit user confirmation, an evidence record and a completed validation. Imported cases become drafts even when an external file says they are approved.

Retrieval ranks approved cases using deterministic text relevance and feedback quality. Accept/modify/reject feedback is recorded. This is case memory; the application does not train model weights or allow model output to overwrite FMEA records. Supplied historical approvals retain their original status and are labeled as inherited approvals, not newly verified engineering evidence. The new development lesson remains a draft.

Shared function, element, failure mode, cause and effect IDs connect the DFMEA views. Changing tabs does not create copies. Exact legacy text was normalized to shared objects while legacy values and unresolved references remain available for review. Closing an action does not reduce risk automatically; reviewed S/O/D changes create new risk history.

## Known baseline findings

- Eighteen DFMEA/PFMEA current RPN values disagree with their stored S/O/D. They are marked `Needs rating review`; no replacement ratings were invented.
- Legacy controls, actions and evidence contain unresolved source references. Diagnostics lists each occurrence.
- Four historical actions have no resolvable failure link.
- DF-005 and DF-006 have no validation traceability.

Use Diagnostics / Validation → Run Checks to record findings and linked change impacts. Create Candidate produces a separate draft. Human review with explicit S/O/D is required before a candidate can create an official record in the Open FMEA application Design FMEA project. This is separate from a later System FMEA.

The controlled sidebar reference is `architecture/mockups/mockup-04-consolidated-home.png`, extended by the analyses already present in the supplied HTML versions. The DFMEA content reference is mockup 11. Mockup images were not edited.

The JSONL corpus preserves historical lessons and validation definitions. New lessons require source evidence and review. Automated UI checks do not establish exact visual parity or constitute engineering approval.
