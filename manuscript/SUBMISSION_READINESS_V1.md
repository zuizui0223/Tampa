# Tampa ecology manuscript — submission readiness v1

## Current state

- [x] Primary ecological source pinned and reproducible.
- [x] Canonical result ledger exists.
- [x] Ecological mechanism stopping rule exists.
- [x] Main paper hierarchy frozen around state decoupling.
- [x] Abstract drafted.
- [x] Introduction drafted.
- [x] Methods drafted.
- [x] Results drafted.
- [x] Discussion drafted.
- [x] Figure 1–4 data contracts frozen.
- [x] Figure 1–4 PNG/SVG renderer passes CI.
- [x] Figure captions drafted with evidence-status boundaries.
- [x] External NPS Figure 3 sidecar separated from Tampa primary evidence.
- [x] Single-file manuscript assembled deterministically.
- [x] Claim–evidence map exists.
- [x] Manuscript-integrity CI passes.
- [x] Core literature context added.
- [x] Unresolved manuscript placeholders: **0**.
- [x] Approximate assembled manuscript length: **~6,056 words** before formatted References / back matter.

## Required before initial journal submission

- [x] Select target journal: **Estuaries and Coasts — Original Article**.
- [x] Apply journal Abstract/keyword/citation/caption constraints in the ESCO submission build.
- [x] Complete provisional bibliography for all current in-text citations.
- [x] Check every current in-text author–year citation against the bibliography.
- [x] Apply Estuaries and Coasts / APA-style reference ordering and author–year punctuation.
- [ ] Final Word export: verify journal-specific typography and line numbering.
- [x] Write Supplementary Methods S1–S14 and assemble deterministic SI source.
- [x] Render Supplementary Figures S1–S7 and generate Supplementary Tables S1–S9 with dedicated CI.
- [x] Add Data Availability statement with exact public source locations and pinned commits.
- [x] Add Code Availability statement pointing to the public Tampa repository; final submission tag/commit/DOI remains to be frozen.
- [ ] Add author list, affiliations and corresponding-author information.
- [ ] Add author-contribution statement.
- [ ] Add competing-interests statement.
- [ ] Add acknowledgements / funding.
- [ ] Decide whether the journal requires permits/ethics text for public monitoring data; document not applicable if appropriate.
- [ ] Freeze a submission commit/tag and archive release.
- [ ] Run final manuscript–figure numeric consistency audit against that tag.
- [x] Add Estuaries and Coasts figure renderer at 174 mm width with EPS + 600 dpi TIFF outputs.
- [x] Final visual QA of the Estuaries and Coasts EPS/TIFF package.
- [ ] Check species names, units, minus signs, superscripts and Braun–Blanquet wording after typesetting/export.
- [x] Confirm adverse target year 2016 remains visible in Figure 4 and text.
- [x] Confirm NPS external comparison is still labelled post-hoc in manuscript/captions/claim map.
- [x] Manuscript/Supplement integrity checks enforce the boundary against demographic extinction/recolonization claims.
- [x] Manuscript/captions retain explicit boundaries against climate causation and competitive replacement.

## Nice to have, not required to submit

- [ ] Graphical abstract / conceptual state-hierarchy diagram.
- [ ] Public repository landing page that links manuscript, figures, canonical JSON and reproducibility workflows.
- [ ] Machine-readable figure-data release.
- [ ] Short plain-language monitoring implications box.
- [ ] Future-study protocol for new meadow-scale PAR / temperature / salinity / below-ground reserve measurements.

## Analyses that should **not** be added before initial submission

Per the frozen mechanism boundary, do not add another retrospective:

- temperature threshold;
- salinity threshold;
- lag window;
- spatial radius;
- generic connectivity index;
- hidden-state simulation family;
- depth/sediment transformation;
- bulk-light formula.

Likewise, do not repair already-consumed external early-warning endpoints and relabel them as untouched validation.

## Decision rule for “ready to submit”

The initial paper is scientifically ready once:

1. references and journal formatting are complete;
2. Supplementary Methods/Figures/Tables document the existing analyses;
3. the submission commit reproduces all main figures and canonical headline results;
4. no new retrospective mechanism claim has been introduced.

A newly identified causal mechanism is **not** a prerequisite for submission.
