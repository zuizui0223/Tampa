# Tampa ecology manuscript — Data and Code Availability v1

This file records public source provenance for the manuscript. The final submission should replace the repository commit placeholder with the frozen submission tag/commit and archival DOI, if created.

## Data Availability

All biological and environmental data analyzed in this study are publicly available.

### Tampa Bay fixed-transect seagrass monitoring

The primary Tampa Bay biological analyses use the public Darwin Core conversion maintained in the `tbep-tech/obis-example` repository:

- repository: https://github.com/tbep-tech/obis-example
- pinned commit: `6c567beff95ea04f0e397101befb49d5233ace8f`
- analyzed source tables: `dwc/event.csv`, `dwc/occurrence.csv`, and `dwc/emof.csv`

The Tampa analysis scripts verify the expected source byte sizes and Git blob identities before parsing. The manuscript does not depend on the current mutable repository head.

### Tampa Bay long-term water quality

Response-independent environmental screens use the public TBEP/EPCHC long-term water-quality source maintained in `tbep-tech/wq-static`:

- repository: https://github.com/tbep-tech/wq-static
- pinned commit: `00aa86030f9245fe0318c186e7137798684dce74`
- source file: `data-raw/Results_Updated.xls`
- expected source Git blob: `b681a270e5cddb585fe5f7e03a853aa313bf0831`

The source is reaggregated from station-month to bay-segment month/year within the manuscript repository.

### Published Tampa Bay hot–fresh reconstruction

The compound temperature–salinity analysis reuses the exact public analysis artifact from the published Tampa Bay hot/fresh study:

- repository: https://github.com/tbep-tech/temp-manu
- pinned commit: `e5aaec93c7501fc38c63b615a89e68636b36421f`
- source artifact: `data/thralltrndat.RData`
- Git blob: `f6518ea25685369057bfe92e71973ec04c57eac1`

The Tampa repository verifies the blob identity before extracting the published 30 °C / 25 ppt marginal and joint stress runs.

### National Park Service external Zostera panel

The post-hoc external ecological comparison uses the National Park Service Tier-3 seagrass dataset archived in the NPS Integrated Resource Management Applications DataStore:

- NPS reference ID: `2316692`
- frozen response download used by the analysis contract: https://irma.nps.gov/DataStore/DownloadFile/758144?Reference=2316692
- expected response size: `1,455,261` bytes

The exact parser, allowed species codes, missing-value semantics, permanent-quadrat eligibility rules, and frozen source header are recorded in `validation/nps_tier3_v2/final_outcome_contract.json`.

### Caribbean external-validation attempt

The terminal Caribbean SeagrassNet early-warning attempt used PANGAEA dataset:

- DOI: https://doi.org/10.1594/PANGAEA.994149

That one-shot endpoint stopped on its frozen numeric schema before any model was fit. It is reported only in the external-validation ledger and does not count as predictive evidence.

## Code Availability

All analysis, validation, figure-generation, manuscript-build, and submission-integrity code is maintained in:

- https://github.com/zuizui0223/Tampa

The repository contains:

- immutable source identities and parser contracts;
- canonical result ledgers;
- primary Tampa reproducibility workflows;
- post-hoc NPS external ecological workflows;
- mechanism stopping rules;
- main and supplementary figure-data builders;
- main and supplementary figure renderers;
- deterministic manuscript and Supplement builders;
- *Estuaries and Coasts* submission-integrity checks.

### Submission freeze

Before journal submission, replace the fields below with the frozen release:

- submission Git commit: `<SUBMISSION_COMMIT>`
- submission Git tag: `<SUBMISSION_TAG>`
- archival repository DOI: `<ARCHIVE_DOI_IF_CREATED>`

The frozen release should reproduce all headline results, Figure 1–4, Supplementary Figures S1–S7, and Supplementary Tables S1–S9 without relying on unpinned upstream data.

## Reuse boundary

The manuscript analysis repository does not claim ownership of upstream monitoring data. Users should consult the original Tampa Bay, NPS, and PANGAEA sources for their respective data licenses, attribution requirements, and authoritative metadata.
