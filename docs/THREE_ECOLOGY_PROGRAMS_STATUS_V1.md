# Three independent ecology programmes — executable status

## Azores — state-dependent mobility gating

**Completed**
- EOG clue separated from ecological claim;
- Europe-wide eel panel audited;
- exact Durif cohort identified;
- project-fixed stage analyses and body/timing robustness implemented;
- behavioural migration initiation reconstructed from six compatible public project tables;
- Dutch consecutive-barrier confirmation protocol and schema gate implemented.

**Positive-control result**
- 575 FIII/FIV/FV eels reconstructed in six compatible migration tables;
- raw initiation: FIII 61.7%, FIV 79.4%, FV 87.8%;
- adjusted initiation OR per stage = **1.99**, 95% CI **1.49–2.66**, p ≈ **3.2e-6**;
- leave-one-project-out OR range **1.67–2.26**, all 95% intervals >1;
- among 427 initiators, onset latency multiplier per stage = **0.75**, 95% CI **0.60–0.93**, p = **0.0088**;
- final successful-migrant endpoint also shows a robust stage signal after project/year/body-length/release-timing adjustment.

**Interpretation**
Durif readiness behaves biologically as expected. This is a construct/positive control, not the novelty claim.

**Unresolved novelty target**
> Does hydrological opportunity / barrier permeability control how internal readiness is translated into realised movement?

**Next decisive input**
- Dutch DANS consecutive-barrier dataset DOI 10.17026/LS/WTSUNG;
- run `analysis/08_dutch_barrier_confirmation_gate.py`.

---

## Louisiana — within-home-range environmental-state fidelity

**Completed**
- EOG propagation anomaly separated from ecological claim;
- Lake Erie Zenodo archive resolved directly;
- point IDs decoded into bird + matched homing/random event without outcome-driven repair;
- individual bird fixed as the biological replication unit;
- direct standardizer and corrected deterministic Monte Carlo analysis implemented;
- South Carolina King Rail broad-relocation boundary added;
- Godwit external-generality analysis implemented.

**Independent Lake Erie result**
Source QC:
- 607 rows;
- 17 source-defined missing rows excluded;
- 2 malformed IDs excluded without repair;
- **190 matched events from 10 birds**;
- strict two-random subset: **173 events**.

State Retention Index:
- **10/10 birds positive**;
- median SRI **0.886**;
- sign test **p = 0.00098**;
- strict subset: **10/10 positive**, median **0.882**.

Time-ordered state-trajectory test:
- **10/10 birds** show smaller successive used-water-depth changes than matched local-availability pseudo-trajectories;
- median temporal retention **0.658**;
- strict subset median **0.667**;
- sign test **p = 0.00098**;
- all 10 birds individually pass the temporal randomization test in both primary and strict analyses.

**Supported statement**
> King Rails repeatedly occupied a temporally smoother water-depth trajectory than was locally available at the same observation times.

**Boundary**
Separate UTM coordinate files lack explicit event IDs. Do not silently join by row order. The stronger claim that geographic displacement itself produces the state retention remains unresolved.

**Next decisive test**
- independently verify coordinate-to-event linkage, or obtain event-linked coordinates;
- meanwhile run Godwit external-generality test and use South Carolina as same-species broad-relocation boundary.

---

## Tampa — buffered persistence under quantitative degradation

**Completed**
- retrospective binary–quantitative state decoupling established and externally reproduced;
- Tampa positioned as third independent ecological programme;
- rhizome TNC selected as first decisive prospective mechanism test;
- Boca Ciega added prospectively before outcome-bearing sampling;
- four-bay `clonal_state_prospective_v2` contract frozen;
- fail-closed precollection freeze, field manifest and baseline validator implemented.

**Four-bay planning frame**
- Old Tampa Bay: 8 nodes;
- Middle Tampa Bay: 11;
- Lower Tampa Bay: 14;
- Boca Ciega Bay: 8;
- total planning frame: **41 nodes**.

**Confirmatory gate**
- >=36 analyzable nodes;
- **>=8 per bay**;
- <=28-day synchronized campaign;
- baseline within +/-14 days;
- >=3 valid cores per node;
- one frozen HPLC TNC method.

**Current hard stop**
The validator intentionally returns STOP until a response-independent pilot freezes:
- rhizome tissue class;
- minimum transect offset;
- core diameter and depth;
- preservation time and method;
- assay-batch randomization;
- campaign dates.

**Next decisive input**
- Thalassia tissue/HPLC pilot + field/logistics freeze;
- then execute the four-bay prospective TNC campaign.

---

# Current order of work

1. **Louisiana:** coordinate-event linkage or external generality after the positive Lake Erie state-fidelity result.
2. **Azores:** Dutch within-landscape barrier/opportunity confirmation.
3. **Tampa:** response-independent pilot/freeze, then four-bay TNC sampling.

These remain three separate ecological papers. Any synthesis is secondary.
