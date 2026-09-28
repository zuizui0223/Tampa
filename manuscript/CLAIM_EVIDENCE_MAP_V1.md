# Tampa ecology manuscript — claim–evidence map v1

This file is the manuscript audit map. It records the evidence class, canonical result, main figure and wording boundary for each paper-level claim.

| ID | Manuscript claim | Evidence class | Canonical source | Main display | Allowed wording / boundary |
|---|---|---|---|---|---|
| C1 | Persistent recorded *Thalassia* occurrence can coexist with quantitative degradation | Primary Tampa ecological result | `results/current_validation_v2.json → quantitative_state` | Figure 2 | “Persistent occurrence can conceal quantitative degradation.” Do not equate recorded presence with demographic persistence. |
| C2 | Degradation mode differs among Tampa Bay segments | Primary Tampa ecological result | `quantitative_state` + `community_reorganization` in `results/current_validation_v2.json` | Figures 2 and 3A | Old/Middle: plant-condition decline; Lower: frequency/abundance contraction + community reorganization. Do not force one bay-wide mechanism. |
| C3 | Lower Tampa Bay shows compositional reorganization | Primary descriptive community result | `community_reorganization` | Figure 3A | “Compositional reorganization” / “greater relative prominence of *Halodule*.” Do not claim competitive replacement. |
| C4 | Saturated presence can coexist with large quantitative trajectories in a second seagrass panel | Post-hoc external ecological replication | `results/nps_persistent_cover_v1.json` + sensitivity JSON | Figure 3B | Explicitly call post-hoc external ecological replication. Do not call untouched predictive validation or universal decline. |
| C5 | Low quantitative state contains information about next-year recorded-state instability | Exploratory strict walk-forward internal validation | `results/current_validation_v2.json → quantitative_early_warning` | Figure 4 | “Early-warning candidate” / “recorded-state instability.” Do not say extinction risk, collapse prediction or demographic survival. Retain adverse 2016. |
| C6 | Recent local state is strongly informative; apparent older-history value is reference-dependent | Secondary temporal-state diagnostic | `memory.site_identity_audit`, `matched_state_dimension_memory`, `eog_ecological_translation.stable_node_r2` | Figure 1B; Supplement S1 | Do not headline a 10-year biological-memory constant or causal state-dimension memory horizon. |
| C7 | Current retrospective data do not identify one common mechanism for post-2016 degradation | Claim-boundary synthesis | `docs/ECOLOGICAL_MECHANISM_BOUNDARY_V1.md` and mechanism entries in `results/current_validation_v2.json` | Supplement S2 / Discussion | Say “mechanism unresolved” or “tested summaries unsupported.” Do not infer absence of environmental causation. |
| C8 | The 2016/2017 pulse is protocol-sensitive | Protocol audit / negative boundary | `pulse_2016_2017` + source protocol audit | Supplement only | Do not call confirmed extinction/recolonization or discrete ecological collapse. |
| C9 | Existing Tampa Bay monitoring can use state decoupling as an earlier diagnostic layer | Conservation translation from primary results + official TBEP monitoring structure | `quantitative_state`, `community_reorganization`, `quantitative_early_warning` + TBEP Seagrass Assessment | Discussion / conservation translation | Recommend separate interpretation of extent, focal abundance, plant condition, and community context. Do not claim a validated intervention threshold or causal prescription. |
| C10 | Pre-existing mixed-species points are less likely to become seagrass-bare after exact-point Thalassia loss | Post-hoc exploratory exact-point community ecology | `results/community_insurance_v1.json` | Main text / future figure or Supplement | Use “community-insurance pattern” or “pre-existing mixture associated with occupancy retention.” Do not call facilitation, functional equivalence, or competitive replacement. |
| C11 | Greater pre-loss alternative-seagrass richness predicts greater retention of seagrass occupancy after exact-point *Thalassia* loss | Post-hoc exploratory exact-point community ecology | `results/community_diversity_insurance_v1.json` | Main text / Supplement | Use “biodiversity-insurance gradient” or “positive richness–retention association.” Do not call causal biodiversity insurance, facilitation, niche complementarity, or functional redundancy. |

## Figure provenance

- **Figure 1–2, Figure 3A, Figure 4:** built in primary Tampa CI by `analysis/30_main_figure_data.py`.
- **Figure 3B:** built separately by `analysis/31_nps_figure_data.py` to preserve its post-hoc external evidence status.
- **Rendering:** `figures/render_main_figures.py`; no model fitting or endpoint selection occurs during rendering.
- **Captions:** `manuscript/TAMPA_ECOLOGY_FIGURE_CAPTIONS_V1.md`.

## Hard wording stops

The initial manuscript should not use any of the following as its paper-level conclusion:

- “10-year ecological memory”;
- “state-dimension-dependent memory horizon” as an established mechanism;
- “EOG failure proves local control”;
- “climate change caused the Tampa decline”;
- “*Halodule* competitively replaced *Thalassia*”;
- “2016 was extinction and 2017 recolonization”;
- “quantitative state predicts extinction/collapse”.

## Manuscript novelty

The novelty is **not** the recommendation to monitor multiple state variables by itself. Current seagrass-monitoring synthesis already recommends integration across biological levels. The empirical contribution is that one 29-year repeated-site record demonstrates that those levels can diverge through time, that the degraded dimension differs spatially within one estuary, and that quantitative weakening can precede some changes in the coarse recorded state.
