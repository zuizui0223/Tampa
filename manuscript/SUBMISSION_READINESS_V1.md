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

- [ ] Select target journal and apply journal-specific structure/word limits.
- [x] Complete provisional bibliography for all current in-text citations.
- [x] Check every current in-text author–year citation against the bibliography.
- [ ] Apply the selected target journal's reference style and punctuation rules.
- [ ] Write Supplementary Methods from `TAMPA_ECOLOGY_SUPPLEMENT_OUTLINE_V1.md`.
- [ ] Render Supplementary Figures/Tables S1–S9.
- [ ] Add Data Availability statement with exact public source locations and pinned commits.
- [ ] Add Code Availability statement pointing to the Tampa repository release/commit used for submission.
- [ ] Add author list, affiliations and corresponding-author information.
- [ ] Add author-contribution statement.
- [ ] Add competing-interests statement.
- [ ] Add acknowledgements / funding.
- [ ] Decide whether the journal requires permits/ethics text for public monitoring data; document not applicable if appropriate.
- [ ] Freeze a submission commit/tag and archive release.
- [ ] Run final manuscript–figure numeric consistency audit against that tag.
- [ ] Export publication-quality vector figures at the target journal dimensions.
- [ ] Check species names, units, minus signs, superscripts and Braun–Blanquet wording after typesetting/export.
- [ ] Confirm that adverse target year 2016 remains visible in Figure 4 and text.
- [ ] Confirm NPS external comparison is still labelled post-hoc everywhere.
- [ ] Confirm no sentence implies demographic extinction/recolonization from recorded state.
- [ ] Confirm no sentence implies climate causation or competitive replacement.

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
