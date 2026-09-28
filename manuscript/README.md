# Tampa manuscript workspace

## Current manuscript

- **Single-file build:** `TAMPA_ECOLOGY_MANUSCRIPT_V1.md`
- **Builder:** `build_manuscript.py`
- **Abstract + Introduction source:** `TAMPA_ECOLOGY_ABSTRACT_INTRO_V1.md`
- **Methods source:** `TAMPA_ECOLOGY_METHODS_V1.md`
- **Results + Discussion source:** `TAMPA_ECOLOGY_RESULTS_DISCUSSION_V1.md`
- **Main figure captions:** `TAMPA_ECOLOGY_FIGURE_CAPTIONS_V1.md`
- **Scientific spine:** `TAMPA_ECOLOGY_MANUSCRIPT_SPINE_V2.md`
- **Claim–evidence map:** `CLAIM_EVIDENCE_MAP_V1.md`
- **Reference notes:** `TAMPA_ECOLOGY_REFERENCE_NOTES_V1.md`
- **Provisional bibliography:** `TAMPA_ECOLOGY_REFERENCES_V1.md`
- **Supplement plan:** `TAMPA_ECOLOGY_SUPPLEMENT_OUTLINE_V1.md`
- **Submission checklist:** `SUBMISSION_READINESS_V1.md`
- **Target journal contract:** `ESTUARIES_COASTS_TARGET_V1.md`
- **ESCO submission body:** `TAMPA_ECOLOGY_ESCO_SUBMISSION_V1.md`
- **ESCO figure captions:** `TAMPA_ECOLOGY_FIGURE_CAPTIONS_ESCO_V1.md`
- **ESCO back matter template:** `ESTUARIES_COASTS_BACK_MATTER_TEMPLATE_V1.md`
- **ESCO cover letter template:** `ESTUARIES_COASTS_COVER_LETTER_TEMPLATE_V1.md`
- **ESCO checklist:** `ESTUARIES_COASTS_SUBMISSION_CHECKLIST_V1.md`

## Authoritative scientific boundaries

- `../results/current_validation_v2.json`
- `../docs/ECOLOGICAL_MECHANISM_BOUNDARY_V1.md`

## Editing rule

Edit the section source files, then run:

```bash
python manuscript/build_manuscript.py
```

Commit both the edited source files and regenerated `TAMPA_ECOLOGY_MANUSCRIPT_V1.md`. The manuscript-integrity workflow fails if they drift.

## Current paper-level message

> **Persistent occurrence can conceal spatially heterogeneous quantitative degradation in a foundation species.**

Mechanism is deliberately secondary and unresolved.
