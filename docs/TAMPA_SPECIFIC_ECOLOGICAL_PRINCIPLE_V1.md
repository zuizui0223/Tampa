# Tampa ecological mainline: buffered persistence under quantitative degradation

## Biological puzzle

Long-term Tampa Bay monitoring shows that *Thalassia testudinum* can remain recorded at a fixed transect while finer dimensions of meadow state deteriorate.

This is not just a monitoring-resolution problem.

It creates a biological question:

> **How can a sessile foundation species remain present while abundance, morphology or shoot density deteriorate?**

## Existing pattern

The retrospective record already establishes state decoupling:

- coarse presence is comparatively persistent;
- frequency, abundance, blade length and shoot density are more labile;
- different bay segments degrade along different quantitative dimensions;
- simple annual environmental summaries do not identify one common driver;
- simple neighbourhood propagation does not explain the annual pattern.

The paper should not keep mining the old annual table for another retrospective mechanism.

## Candidate mechanism: buffered persistence

A foundation species can remain present even while condition declines if stress is temporarily absorbed by hidden biological or ecosystem-level buffers.

### Buffer 1 — internal reserve state

Rhizome non-structural carbohydrate and meristem capacity may allow shoots to persist through temporary negative carbon balance or tissue loss.

Primary prospective prediction:

> higher baseline rhizome TNC predicts less negative future quantitative *Thalassia* change after current above-ground state is controlled.

### Buffer 2 — self-engineered physical state

Established canopy can alter near-bed flow and sediment/light conditions.

Required two-link prediction:

1. canopy causes excess physical attenuation relative to a matched bare-bed control;
2. stronger attenuation predicts more favourable future quantitative *Thalassia* change.

Only both links support self-facilitative buffering.

### Buffer 3 — community functional state

If focal *Thalassia* declines, pre-existing alternative seagrasses can preserve vegetation occupancy.

The open question is whether they also preserve function.

Prediction:

> alternative-canopy composition may retain occupancy while changing hydrodynamic attenuation or other foundation-species functions.

## Buffer role decomposition: resistance versus regenerative/functional continuity

The three organizational levels above do not all buffer persistence in the same way.

A useful second axis is **what the buffer does**.

### Resistance buffers

These reduce the amount of quantitative change experienced during a stress episode.

Candidate Tampa mechanisms:

- **rhizome energetic reserve (TNC):** stored carbon can sustain tissue and maintenance when current carbon balance is poor;
- **canopy physical engineering:** the standing meadow can reduce or transform local hydrodynamic exposure.

The common prediction is not reappearance. It is:

> stronger resistance-buffer state -> smaller subsequent quantitative loss while the focal meadow remains under observation.

### Regenerative / continuity buffers

These do not necessarily prevent focal-state decline. Instead, they preserve the capacity for subsequent growth or preserve habitat function when focal *Thalassia* weakens.

Candidate Tampa mechanisms:

- **rhizome meristem / apex bank:** regenerative capacity remaining below ground;
- **alternative seagrass canopy:** community-level continuity that can keep the habitat vegetated and potentially retain physical function even when *Thalassia* prominence declines.

These are deliberately not called observed "recovery" from binary re-recording. Regenerative capacity and functional continuity are new biological states that must be measured directly.

### Why this matters for the Tampa state-decoupling result

The same coarse outcome—continued recorded presence—can arise through biologically different routes:

1. the focal meadow resists change because internal or engineered buffers absorb forcing;
2. the focal quantitative state changes, but regenerative capacity remains;
3. focal dominance declines, but alternative foundation species preserve some habitat function.

Therefore:

> **coarse persistence does not identify whether the system resisted disturbance, retained regenerative capacity, or substituted function at the community level.**

This is a stronger ecological interpretation of state decoupling than simply saying that presence is a coarse monitoring variable.

### External forcing is not a buffer

High-frequency hot-fresh events, low light, hypoxia or disturbance are treated as inputs that may **consume or overwhelm** resistance/regenerative buffers.

The frozen event-stress study therefore asks whether local hot-fresh exposure depletes TNC; it does not add temperature/salinity as a fourth buffer.

## Stronger ecological hypothesis

The current data motivate:

> **coarse persistence can be maintained while hidden resilience capacity is being consumed or reorganised.**

But this is not yet a demonstrated resilience debt.

The current prospective programme can directly establish **hidden buffer depletion under persistent occurrence** if a measured buffer declines while coarse occurrence remains recorded, and can test whether the remaining buffer state predicts later quantitative deterioration.

A strict resilience-debt claim is held to the stronger Johnstone et al. (2016) meaning: diminished recovery capacity that becomes apparent after a subsequent independently characterized disturbance.

Therefore the present event -> TNC -> future-frequency chain, even if fully supported, is described first as **buffer depletion with delayed quantitative consequence**, not automatically as resilience debt.

See `docs/RESILIENCE_DEBT_BOUNDARY_V1.md`.

## State-versus-trajectory hypothesis

The reserve programme also makes a stronger dynamical prediction than a static "high TNC is good" association.

Consider two meadows with the same current post-exposure rhizome TNC:

- one recently **depleted** reserve to reach that current value;
- the other recently **maintained or rebuilt** reserve to reach the same current value.

If current reserve level were a sufficient ecological state descriptor, their subsequent quantitative trajectories should not systematically differ after current post-TNC and current above-ground state are represented.

The frozen temporal diagnostic therefore asks:

```text
paired_anchor_delta_tnc_42d = median_j(tnc_post_anchor_j - tnc_pre_anchor_j)

future_delta_frequency
  ~ baseline_frequency_post
  + tnc_post
  + paired_anchor_delta_tnc_42d
  + water_body
```

The trajectory is deliberately computed from matched q25/q50/q75 anchor changes before node summarization, rather than subtracting independently summarized node medians. This reduces the chance that spatial below-ground heterogeneity is relabelled as temporal change.

The focal prediction is:

> at the same current post-exposure reserve level, a meadow with a more positive recent reserve trajectory has a more favourable subsequent quantitative trajectory.

This is a concrete form of **trajectory dependence**.

If supported, the ecological implication is not merely that "history matters." It is that the instantaneous measured state is incomplete: the direction from which the system arrived at that state contains additional prospective information.

That would make the Tampa problem more general than monitoring resolution:

> **two foundation-species meadows can occupy the same measured state yet carry different near-future risks because their hidden buffer trajectories differ.**

### Predeclared state-versus-trajectory interpretation

| Static four-bay TNC primary | Reserve-trajectory diagnostic | Interpretation |
|---|---|---|
| supported | supported | Current reserve level and recent reserve trajectory both carry prospective information; consistent with a genuinely dynamic internal buffer state. |
| supported | unsupported | Current reserve stock predicts the future, but the 42-day trajectory adds no supported information beyond current stock under this design. |
| unsupported | supported | The authoritative static reserve primary remains unsupported. Report trajectory dependence only as a secondary finding suggesting that recent change may be more informative than level; it does **not** rescue the primary TNC mechanism claim. |
| unsupported | unsupported | No supported reserve-level or reserve-trajectory signal under the frozen tests; move to other measured buffers rather than retuning TNC analyses. |

If the trajectory coefficient is measurement-sensitive under the frozen pre/post-core diagnostics, use that label instead of the supported/unsupported synthesis above.

### What this is not

This diagnostic does **not** by itself establish:

- hysteresis;
- an alternative stable state;
- a critical threshold;
- rate-induced tipping;
- formal ecological memory as a causal mechanism.

Those ideas require stronger dynamical evidence. In particular, rate-induced tipping concerns the rate of change of an external forcing relative to a system's ability to track a moving state. The Tampa diagnostic instead measures recent change in an internal reserve state.

The narrower wording is deliberate:

> **recent reserve trajectory contains information beyond current reserve level.**

This secondary diagnostic cannot rescue a null authoritative four-bay static TNC primary.

### Measurement-validity boundary for trajectory dependence

A 42-day TNC change is called a reserve trajectory only when the measurement design itself can distinguish time from space and assay drift.

Therefore the temporal diagnostic is eligible only if:

- exactly the same frozen **q25/q50/q75 anchor IDs** are represented in both rounds, and each anchor-specific post-minus-pre change is calculated before the node median trajectory;
- pre and post use distinct non-overlapping core offsets, so the second sample is not simply re-coring disturbed sediment;
- every included TNC sample passes the authoritative TNC-v2 sample/assay QC;
- the response-independent HPLC method pilot passes its frozen recovery and precision limits;
- pre/post sampling round is **not perfectly confounded with HPLC assay batch**.

If all pre material is effectively one assay batch and all post material another, the temporal diagnostic is non-estimable rather than being interpreted as reserve change.

This matters because the ecological claim is stronger than a repeated-measures correlation:

> **the same meadow can arrive at the same current reserve level by different matched-location reserve trajectories, and those trajectories may carry different near-future risks.**

That claim requires the observed trajectory to be biological rather than a core-location or assay-round artifact.

## Persistent site-template alternative

Stable transect identity explains a large fraction of the retrospective level differences in coarse state.

Therefore a future cross-node association such as "high TNC -> better future state" or "high attenuation -> better future state" can still reflect persistent site quality that influences both the measured buffer and the future trajectory.

The mechanism programme handles this by requiring **mechanism-specific process gates**, not by pretending the site-template alternative has disappeared:

- event exposure -> within-node TNC depletion for the reserve pathway;
- vegetated -> bare-bed excess attenuation for the engineering pathway;
- directly measured composition -> physical function for community functional continuity.

See `docs/SITE_TEMPLATE_ALTERNATIVE_AND_EVIDENCE_LADDER_V1.md`.

A supported prospective association without its process gate is described as a **buffer-state predictor**, not a fully identified buffering mechanism.

## Novelty boundary

Seagrass carbohydrate reserves, self-facilitation, ecosystem engineering, community insurance and resilience debt are all established ideas.

The Tampa contribution is not the existence of those mechanisms.

It would be:

> **prospectively comparing multiple candidate buffers against the same future quantitative endpoint in one long-monitored foundation-species system.**

The novelty is the decomposition.

## Falsification

The buffered-persistence programme weakens if:

- TNC has no prospective relationship with future state under adequate precision;
- canopy attenuation is physically real but unrelated to future persistence;
- community replacement retains occupancy but not measurable ecosystem function;
- no measured buffer predicts future state beyond current condition;
- apparent state decoupling is adequately explained by current above-ground state alone.

## Main ecological endpoint

A strong supported result would be:

> **foundation-species persistence is not a single state: coarse presence can outlast deterioration because resilience is stored in biological reserves, self-engineered physical conditions, or community-level functional insurance.**

Which mechanism is supported must come from the prospective measurements, not from retrospective relabelling.
