# Physical structure and ecological functional legacy

2026-11-24. Response-open reanalysis of Meysick et al. 2019, 10.1371/journal.pone.0222020 S7. Local execution used the original-workbook ZIP (artifact 14911201555; SHA256 144aa9cbadf811e307f8c024180152e640f4a55c8f4fb19474382c69eef0ba6c) and checked workbook hash against manifest. All 16 configurations x 10 velocities, 30 seeds/cell. No independent field validation. Whole configuration holdout with training-only scaling; cell-weighted ridge-logistic models, fixed C=1 and sensitivity .1/.3/3/10. Baseline training-only mean at each flow. No observed sediment scouring mediator used. Four binary composition categories (short shoots, long shoots, oysters, mussels), not complete identity/traits. Geometry: log1p summed lateral object width and object count plus flow interactions. 

| Model | RMSE | 1-SSE/SSE_baseline |
|---|---:|---:|
| flow only | .23393 | .00873 |
| composition and flow | .22141 | .11201 |
| width and flow | .15947 | .53938 |
| geometry and flow | .11951 | .74129 |
| geometry and composition and flow | .12650 | .71013 |
| flow-specific training mean | .23496 | 0 |

Geometry alone has lower pooled MSE than geometry plus composition for all five C values, but the added composition improves 10–11 of 16 held-out configurations (11 at C=1); deterioration is concentrated, no general absence of identity effects. Geometry proxies taxa, identity categories omit abundances except in geometry models, and 16 configurations are not independent ecosystems. The original paper already documented structural control and flow-dependent complementarity. The new comparison addresses prediction for withheld configurations, not causal identity-versus-geometry separation. Source code reproduces the analysis logic; local Python execution performed before this commit, repository version has not separately run in CI.

## New empirical distinction: living engineers vs their structural legacy
Kvitek et al. 1992 (10.2307/1940749) showed otter foraging leaves shell debris and exposes old buried shells, providing attachment substrate for kelp and anemones. Leach et al. 2023 (10.1111/1365-2656.13929) explicitly discusses shell litter as a possible facilitator of kelp. The flume experiment measured live eelgrass, oysters and mussels; it did not test shells of otter prey. Li et al. 2017 (10.1007/s12601-017-0016-5) and Wei et al. 2023 (10.1016/j.rsma.2022.102799) experimentally show live Manila clam bioturbation enhances eelgrass seed burial. Distinguish physical trapping, live animal bioturbation, and filtering. Do not identify all prey clams with the studied oyster/mussel engineers. The physical legacy hypothesis for seed retention is untested.

A minimal bookkeeping model is dH/dt = alpha*consumption + other shell inputs - delta*H, H=effective exposed shell structure (not simply number of shells); T=T(flow,live structure,H), and q=q(predators,burial). Loss of live bivalves could reduce bioturbation while shell structure persists or grows. Test equal-geometry live/empty-shell/inert controls under matched flow, crossed with predator access and follow marked seeds through burial/retention and germination. Measure shell residence, reburial, breakage and removal; no claim of measured half-life or sea otter effect. Do not pool separate experiments into a causal cascade.

Glacier Bay acquisition workflow run 45383304380 was queued at last check; no raw diet or prey estimates yet. 2023 model concerns butter clams Saxidomus gigantea, not all bivalves; direct prey census needs taxon/life-stage function verification. Main branch and manuscripts unchanged.
