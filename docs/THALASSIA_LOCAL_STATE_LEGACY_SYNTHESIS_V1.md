# Thalassia local-state legacy synthesis — v1

## Biological pattern

The Tampa record contains two observations that should be interpreted together.

### 1. A one-year recorded absence does not erase local Thalassia history

Across 259 three-year exact-point sequences from 25 stable transects, longer uninterrupted pre-gap *Thalassia testudinum* occupancy predicted later exact-point re-recording after a one-year non-detection.

The strongest reference-saturated comparison used within-node variation.

- nodes with Thalassia run-length variation: **18**
- run-length range: **1–25 years**
- within-node centered Thalassia-run coefficient: **0.484**
- 95% bootstrap interval: **0.115–1.347**

A generic seagrass-habitat head-start did not show the same resolved increment:

- centered habitat-headstart coefficient: **0.160**
- 95% interval: **-0.219–0.362**

Thus the historical information is more focal-species-specific than a generic statement that the meter mark has long been vegetated.

### 2. Re-recording is not a return to the uninterrupted state

Across 701 quantitatively complete sequences from 22 nodes:

- re-recorded sequences: **109**
- uninterrupted sequences: **592**

At the target year, mean Braun-Blanquet state was:

- re-recorded: **1.95**
- uninterrupted: **2.93**

After source abundance, stable site identity and target year were represented, the re-recorded group retained a negative quantitative coefficient:

- **-0.204**
- 95% bootstrap interval **-0.302 to -0.103**

Therefore a 0 -> 1 observation-state return does not mean that the local quantitative state has reset to the uninterrupted reference.

## What this does and does not mean

Supported retrospective statement:

> **local Thalassia state has historical depth: prior focal occupancy predicts re-recording after a short observation gap, and re-recorded states remain quantitatively distinct from uninterrupted occupancy.**

Do not translate this directly into:

- demographic survival;
- rhizome survival;
- clonal recovery;
- ecological recovery;
- recolonization;
- hysteresis;
- a biological memory timescale.

A one-year non-detection can reflect true local shoot loss, patch displacement, sampling/detection variation, or a mixture of processes.

The result says that the observation process does not behave like a memoryless binary reset.

## Why the community result does not explain the legacy

Pre-existing mixed-species points were less likely to become seagrass-bare after focal Thalassia loss in the pooled exact-point analysis.

However, the stronger within-node richness audit did not pass its frozen support rule:

- informative nodes: **20**
- transitions: **357**
- centered richness coefficient: **0.273**
- 95% interval: **-0.062 to 0.613**

Likewise, the within-node habitat-continuity audit remained directionally positive but unresolved.

Therefore persistent site quality remains a plausible explanation for much of the apparent community-insurance signal.

The focal Thalassia-history result is more interesting because it survives stable-transect saturation and is not explained by generic seagrass-habitat headstart in the tested model.

## Relationship to existing seagrass recovery ecology

Seagrass disturbance/recovery literature already establishes that:

- recovery trajectories depend on disturbance scale and recovery timescale;
- clonal spread is a major recovery route;
- below-ground structure can remain altered after above-ground traits recover;
- *Thalassia* can require years to decades to return after strong disturbance.

Therefore the Tampa novelty is not that historical state can matter.

The specific unresolved mechanism is:

> **what measurable local state carries the focal-species history through periods when the above-ground observation becomes weak or absent?**

## Prospective state-augmentation test

The four-bay TNC programme is a direct response to that question.

The decisive primary is not another retrospective history coefficient. It asks, within the same stable meadow:

```
future_BB_anchor
  ~ baseline_BB_anchor
  + within_node_centered_anchor_TNC
  + node_fixed_effect
```

A supported TNC coefficient would show that a directly measured below-ground reserve state contains future information beyond current above-ground state and stable node identity.

It would not by itself prove that TNC caused historical re-recording, but it would convert a vague historical-legacy signal into a measured biological state variable.

## General ecological formulation

The useful principle is:

> **For a long-lived clonal foundation species, observed occupancy is not a memoryless state. A short recorded gap can occur within a location that still differs according to its prior focal-species history, and subsequent re-recording can remain quantitatively depleted.**

The next question is whether that historical depth is carried by regenerative reserve, fine-scale persistent habitat, or another unmeasured slow state.

## Conservation consequence

Monitoring should distinguish:

1. uninterrupted occupancy;
2. re-recording after a short gap;
3. the quantitative state at re-recording;
4. the local history preceding the gap.

Treating all present observations as equivalent can erase information about local state history.

This is a diagnostic implication, not proof that a re-recorded meadow is demographically recovering.
