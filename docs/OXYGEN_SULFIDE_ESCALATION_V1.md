# Tampa conditional oxygen–sulfide mechanism escalation v1

## Purpose

This document predeclares the **next physiological question** if the direct optical programme supports a within-canopy light -> reserve link.

It does not add another primary endpoint to the current integrated campaign.

The proposed mechanism is:

> **low light can weaken internal plant aeration, allowing sulfide intrusion into below-ground / meristematic tissues and thereby depleting reserve or regenerative capacity.**

This is more specific than saying that "low light is stressful".

## Biological basis

*T. testudinum* transports photosynthetically produced O2 through a lacunar system to below-ground tissues.

Several lines of prior evidence make oxygen–sulfide coupling a plausible downstream mechanism.

1. **Florida Bay field/laboratory work:** meristematic O2 falls strongly at night, and spontaneous sulfide intrusion into *T. testudinum* rhizomes was observed when internal O2 was low.  
   - Borum et al. 2005, Journal of Ecology, DOI 10.1111/j.1365-2745.2004.00943.x.

2. **Direct low-light experiment:** sequential low-irradiance days reduce internal O2 dynamics in *T. testudinum* and increase H2S intrusion into shoot meristems.  
   - Aquatic Botany 181 (2022) 103532, DOI 10.1016/j.aquabot.2022.103532.

3. **Sulfide physiology:** sulfide alters *T. testudinum* carbon/energy balance, and sulfide/hypoxia interact with other stressors.  
   - Aquatic Botany 67 (2000) 275-285, DOI 10.1016/S0304-3770(00)00099-1.  
   - Aquatic Botany 87 (2007) 104-110, DOI 10.1016/j.aquabot.2007.03.004.

4. **Tampa-specific historical motivation:** Lower Tampa Bay summer studies explicitly evaluated community oxygen metabolism under the hypothesis that shading, oxygen depletion or high sediment biological oxygen demand can overwhelm the plant's aeration capacity.

Therefore the oxygen–sulfide pathway is biologically plausible in the focal species and region, but it is **not yet a Tampa mechanism result**.

## Relationship to the current optical primary

Current frozen optical primary:

```text
tnc_post
  ~ tnc_pre
  + mean_daily_within_canopy_dli
  + water_body
```

If supported, it establishes that actual light exposure contains prospective information about reserve change.

It does **not** identify why low DLI affects reserve.

The oxygen–sulfide escalation asks whether the missing physiological step is failure of plant aeration.

## Mechanistic chain

Candidate chain:

```text
low within-canopy DLI
        |
        v
less photosynthetic O2 supply
        |
        +---- lower night/dawn internal meristem/rhizome pO2
        |                  |
        |                  v
        |          greater H2S intrusion
        |                  |
        +------------------+
                           v
               reserve / meristem impairment
                           |
                           v
               future quantitative decline
```

The key idea is **gating**:

> sediment sulfide alone need not predict decline if healthy plants can keep vulnerable tissues sufficiently oxygenated.

The biologically discriminating state is the failure of internal aeration and sulfide exclusion.

## Evidence ladder for a future study

### Level A — external context only

Measurements:

- high-frequency water-column dissolved O2;
- direct within-canopy DLI;
- porewater sulfide / sediment redox.

These establish environmental exposure.

They do **not** demonstrate sulfide intrusion into the plant.

Allowed wording:

> low-light / low-O2 / sulfidic environmental context.

Do not call this plant aeration failure.

### Level B — plant physiological process

Preferred nested measurements on a response-independent subset:

- meristem or rhizome internal pO2 across diel cycles;
- direct H2S detection in meristem/rhizome tissue if technically feasible;
- paired dawn/night versus daytime measurements;
- tissue sulfur diagnostics only if their physiological interpretation is frozen in advance.

Process prediction:

> lower recent DLI and/or lower nocturnal water-column O2 corresponds to lower internal pO2 and greater probability/magnitude of H2S intrusion.

Direct internal O2/H2S measurements are required for an **aeration-failure** claim.

### Level C — reserve / regenerative consequence

A later prospective design may ask whether the directly measured aeration/sulfide state predicts:

- TNC depletion;
- meristem/apex loss;
- future quantitative *Thalassia* change.

This requires a separately frozen design and adequate node replication.

Do not retrofit internal-O2 or sulfide variables into the current optical TNC model after viewing its result.

## Why dissolved oxygen alone is not enough

Water-column O2 is not equivalent to internal plant O2.

*T. testudinum* can maintain high internal tissue O2 while surrounding rhizosphere sediment remains anoxic, and the coupling changes with irradiance and plant state.

Therefore:

- a low water-column DO result is an external exposure state;
- an internal meristem/rhizome O2 result is a plant physiological state;
- H2S intrusion is a further process state.

Keep these levels separate.

## Relationship to hot–fresh events

The current 30 C / 25 ppt study tests a published Tampa compound-event index.

A hot–fresh event could covary with light, oxygen, runoff or stratification, but support for the hot–fresh index does not establish the oxygen–sulfide pathway.

Conversely, an oxygen–sulfide result must not be used to rescue a null/non-estimable hot–fresh primary.

These are distinct mechanism layers.

## Relationship to regenerative buffering

The oxygen–sulfide hypothesis may connect the existing **resistance** and **regenerative-capacity** ideas.

- TNC depletion represents loss of energetic reserve.
- H2S intrusion into meristematic tissue could impair the meristem/apex bank even if coarse presence initially remains recorded.

Thus one external physiological failure could erode both:

1. resistance capacity; and
2. regenerative capacity.

This is a future hypothesis, not an inference from binary reappearance.

## Conditional decision rule

The current campaign is not expanded to include this as another confirmatory primary.

Predeclared next step:

- **optical DLI -> TNC supported:** prioritize a dedicated internal-O2/H2S process study to identify the physiological link;
- **optical DLI -> TNC unsupported with adequate precision:** the specific low-light-initiated aeration-failure chain is weakened for the tested late-summer interval; do not rescue the optical null by adding O2/sulfide post hoc;
- **optical non-estimable:** no mechanistic conclusion; a future oxygen/sulfide study must be justified independently and frozen before new outcome access.

A direct oxygen/sulfide study may still be motivated by independent disturbance observations, but it becomes a new study rather than a reinterpretation of the current campaign.

## Claim boundary

Do not use:

- water-column hypoxia as a synonym for plant hypoxia;
- porewater sulfide as a synonym for tissue sulfide intrusion;
- low light as proof of sulfide toxicity;
- sulfide exposure as proof of future meadow collapse.

The strong mechanistic claim requires the appropriate process state to be measured directly.
