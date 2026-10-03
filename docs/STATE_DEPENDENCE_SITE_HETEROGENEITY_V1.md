# Tampa state dependence versus persistent site heterogeneity

## Why this matters

The Tampa record initially appeared to contain a long ecological-memory signal: earlier recorded state improved prediction beyond the immediately preceding year under a geography / bay reference.

That result was real as a predictive comparison, but its biological interpretation changed when stable transect identity was represented directly.

At the transferred 10-year history scale:

- binary recorded state without node identity:
  - lag-1 log loss = 0.1701;
  - long-history log loss = 0.1395;
  - history won 14/22 target years;
  - paired sign-flip p = 0.01485;
  - 6 history scales passed the frozen support rule.
- binary recorded state with stable node identity:
  - lag-1 log loss = 0.1571;
  - long-history log loss = 0.1417;
  - history won 13/22 target years;
  - paired sign-flip p = 0.0880;
  - **0 history scales** passed.
- focal frequency showed the same qualitative change:
  - 12 supported history scales without node identity;
  - **0** with node identity.
- Braun-Blanquet / cover index retained **0** supported scales with node identity.

Across all 16 tested history scales, no state dimension retained formal older-history support after stable node identity entered the reference.

Source: `results/site_identity_memory_audit_v1.json`.

## Ecological interpretation

This does not show that ecological history is biologically irrelevant.

It shows that a long record of past state can carry two different kinds of information:

1. **true temporal dependence** — past state or trajectory changes what happens next;
2. **persistent unit heterogeneity** — some monitored units are chronically different, so their past state predicts their future because both reflect an enduring site template.

If the second component is not represented, persistent site quality can look like a long memory process.

For Tampa, the robust conclusion is therefore:

> recent local state is strongly informative, but the apparent long-history increment is reference-dependent and is largely compatible with persistent among-transect heterogeneity.

Do not translate the pre-audit history coefficient into a biological memory horizon.

## Connection to statistical ecology

This identification problem is not unique to Tampa.

Hamel, Yoccoz & Gaillard (2012) evaluated repeated ecological data and emphasized that temporal autocorrelation and individual heterogeneity need to be represented together to obtain reliable estimates; models omitting either process performed poorly.

Reference:

Hamel, S., Yoccoz, N.G. & Gaillard, J.-M. (2012). Statistical evaluation of parameters estimating autocorrelation and individual heterogeneity in longitudinal studies. *Methods in Ecology and Evolution* 3:731-742. DOI: 10.1111/j.2041-210X.2012.00195.x.

Authier, Aubry & Cam (2017) showed in a life-history setting that ignoring persistent heterogeneity can bias estimated state dependence upward and argued that state dependence and heterogeneity can easily be mistaken for one another.

Reference:

Authier, M., Aubry, L.M. & Cam, E. (2017). Wolf in sheep's clothing: Model misspecification undermines tests of the neutral theory for life histories. *Ecology and Evolution* 7:3348-3361. DOI: 10.1002/ece3.2874.

These papers concern repeated individuals / life histories rather than fixed seagrass transects, so Tampa should not claim that it is reproducing the same biological process. The transferable point is the **identification problem in longitudinal data**.

## Relationship to ecological memory

Mechanistic ecological-memory theory treats history as informative when future state depends on more than the instantaneous current state—for example through accumulated biotic/abiotic material, trajectory or altered system state.

That is a stronger claim than:

> old observations predict new observations.

For Tampa, a defensible memory-like mechanism therefore requires a newly measured state or trajectory that survives the persistent-site alternative.

Examples already frozen prospectively:

- matched-anchor reserve change over 39-45 days;
- baseline rhizome TNC beyond current above-ground state;
- event exposure -> within-node reserve depletion;
- direct physical canopy engineering -> future quantitative state.

## General methodological proposition

The Tampa audit motivates a broader caution for long-term ecological monitoring:

> **Predictive value of long history is not by itself evidence of ecological memory when monitoring units differ persistently in latent quality.**

A useful minimum workflow is:

1. quantify immediate state dependence;
2. test older-history increment;
3. repeat the comparison with stable unit identity / heterogeneity represented;
4. treat history that disappears under unit saturation as site-template information, not a memory timescale;
5. require process-level or within-unit dynamic measurements for a stronger memory mechanism claim.

## What would be novel in Tampa

The novelty is not the statistical distinction itself.

The contribution is that the distinction changes the ecological interpretation of a decades-long foundation-species record:

- an apparently long-memory occupancy signal collapses under stable-site saturation;
- the remaining ecological puzzle shifts from "how long is memory?" to "what persistent or hidden state makes some meadows resistant?";
- that revised question generates direct prospective measurements of reserve state, local forcing and engineered microenvironment.

In other words, **prediction failure redirects mechanism discovery**.

## Claim boundary

- The site-identity audit is post hoc.
- Node identity is a saturated reference, not an identified habitat mechanism.
- Absence of supported older-history increment after node saturation does not prove zero biological memory.
- Do not call the stable node effect habitat quality without direct measurement.
- The prospective site-template-resistant diagnostics are secondary and cannot rescue a null authoritative four-bay TNC primary.
