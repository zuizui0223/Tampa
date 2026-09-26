# Tampa — ecological memory and state transitions in Tampa Bay seagrass

This repository develops an ecological analysis of long-term fixed-transect seagrass monitoring in Tampa Bay. It is intentionally separate from the EOG method-validation result that motivated the question.

## Scientific question

**How long does annual *Thalassia testudinum* state at a fixed transect retain ecological memory, and when does that memory break or reorganize?**

The first analysis treats one transect-year as an annual recorded-detection state and asks whether recent local history improves prospective prediction beyond static space-time information.

## Frozen public source

The analysis is pinned to:

- source repository: `tbep-tech/obis-example`
- source commit: `6c567beff95ea04f0e397101befb49d5233ace8f`
- focal taxon: *Thalassia testudinum*
- years: 1997–2025
- eligible parent-transect visits: 1,497
- stable transect nodes: 71

The parser verifies the exact byte sizes and Git blob identities of `dwc/event.csv` and `dwc/occurrence.csv` before analysis.

## Initial ecological validation

Exploratory result, frozen here before environmental-cause modelling:

1. Annualizing the 1,497 visits yields **1,480 transect-years** and **1,176 consecutive-year transitions**.
2. The data do **not** support a simple claim that memory weakened permanently after 2016. Persistence is high before and after the 2016–2017 pulse.
3. In 2016, **5 of 19 previously positive transects lost recorded *Thalassia***, compared with 15 losses among 492 comparable prior transitions (exploratory one-sided Fisher OR = **11.36**, p = **0.000445**).
4. In 2017, the **same five transects** regained recorded *Thalassia*. The gain pulse is also elevated relative to prior transitions (OR = **5.29**, p = **0.00837**).
5. Those five 2016 transects were surveyed and retained other seagrass records, especially *Halodule*, so the pulse is not explained by simple absence of sampling.
6. In prospective walk-forward prediction, a baseline using longitude, latitude, year and water body has mean log loss **0.3088**. Adding a decaying history of the focal transect sharply improves prediction; the best simple candidate is an exponential memory with a **3-year decay scale** (mean log loss **0.13275** across 22 target years).
7. Infinite/cumulative history is worse than the best finite-memory representation. The current hypothesis is therefore **finite ecological memory**, not permanent site identity.

## Current interpretation boundary

Supported as an exploratory pattern:

> Annual *Thalassia* recorded state has strong finite temporal memory, interrupted by a spatially clustered 2016 loss / 2017 return pulse.

Not yet supported:

- a climate-causal explanation;
- true demographic extinction/recolonization;
- a bay-wide 2016 collapse;
- detection-free occupancy;
- a unique mechanism for the 2016–2017 pulse.

The five affected transects are four in Middle Tampa Bay and one in Old Tampa Bay. Because Tampa Bay seagrass acreage peaked around 2016 before later bay-wide decline, the local binary turnover pulse must not be equated with the later regional acreage decline.

## Reproduce

```bash
python -m pip install -r requirements.txt
python analysis/01_transition_memory.py --out results/generated
```

The script downloads only the pinned public Darwin Core files and verifies their immutable identities before using them.

## Next test

The next analysis will distinguish three explanations for the 2016–2017 pulse:

1. **environmental pulse** — temperature, salinity, clarity/nutrients or disturbance altered *Thalassia* persistence;
2. **community replacement** — *Halodule* / *Syringodium* state changed when *Thalassia* disappeared and returned;
3. **observation/protocol effect** — the annual pulse reflects survey or data-generation changes rather than ecology.

Environmental attribution will be added only after the corresponding source, spatial join and temporal aggregation rules are frozen.
