# Tampa clonal / below-ground measurement protocol v2

## Goal

Measure a genuinely new biological state that can test whether below-ground reserve contributes to future quantitative stability of *Thalassia testudinum* meadows.

The paired prospective contract is `results/clonal_state_prospective_v1_contract.json`.

The primary endpoint is **future quantitative change in meadow state**, not binary reappearance.

## Why rhizome reserve is biologically plausible

*T. testudinum* stores large carbohydrate pools in rhizomes. Seasonal studies report substantial variation in rhizome soluble carbohydrate, with high values in fall and low values in spring, and classic work interprets the robust rhizome system as a mechanism allowing slow response to environmental stress. Chronic light reduction can strongly deplete rhizome carbohydrate. Rhizome sugar, starch and total carbohydrate have also performed as responsive indicators in Florida turtle-grass monitoring.

This makes below-ground reserve a plausible buffering state, but it is not automatically a "health score". Florida studies also show negative relationships between plant nutrient content and rhizome carbohydrate, so carbohydrate can reflect both stored reserve and reduced carbon demand under nutrient-limited growth.

Key references:

- Dawes & Lawrence (1980), *Aquatic Botany* 8:371-380, DOI 10.1016/0304-3770(80)90066-2.
- Lee & Dunton (1997), chronic light reduction in *T. testudinum*, DOI 10.1016/S0022-0981(96)02720-7.
- Campbell, Yarbro & Fourqurean (2012), *Aquatic Botany* 99:56-60, DOI 10.1016/j.aquabot.2012.02.002.
- Sørensen et al. (2018), standardized seagrass NSC protocol, *Aquatic Botany* 151:71-79, DOI 10.1016/j.aquabot.2018.08.006.

## Sampling frame

Use Old, Middle and Lower Tampa Bay stable fixed-transect nodes.

The design is now **census-oriented**:

> attempt to sample every contemporaneously baseline-*Thalassia*-positive eligible node in the three core bays.

The recent 2023-2025 feasibility frame contained approximately:

- Old Tampa Bay: 8 *Thalassia*-positive nodes;
- Middle Tampa Bay: 11;
- Lower Tampa Bay: 14;
- total: 33.

These counts are planning context only. Re-evaluate eligibility at the contemporaneous baseline survey.

Do not select a balanced set of "stable", "degrading" and "unstable" nodes if the full eligible frame can be sampled. Such category sampling would throw away node replication and can make the study unnecessarily dependent on retrospective state labels.

### Precision gate

The primary future model has one focal TNC coefficient plus baseline frequency, baseline Braun-Blanquet state and two bay indicators.

A simple two-sided Gaussian planning benchmark (alpha 0.05, 80% power) gives approximate detectable partial correlations of:

- n = 24: |partial r| about 0.57;
- n = 30: about 0.51;
- n = 33: about 0.49.

Therefore:

- planning target: the full contemporaneous eligible frame, historically about 33 nodes;
- confirmatory minimum: 30 analyzable nodes;
- confirmatory bay minimum: 8 analyzable nodes in each of Old, Middle and Lower Tampa Bay.

Below that gate, report the prospective coefficient and uncertainty as a pilot. Do not use a null result to reject reserve buffering.

Extra cores within a node improve measurement precision, but they do not replace independent node replication.

## Seasonal and baseline alignment

Rhizome carbohydrate is seasonally variable. The field program therefore freezes temporal alignment before coring.

Primary requirements:

1. collect all confirmatory TNC samples within one predeclared **<=28-day seasonal campaign**;
2. preferably perform TNC coring and the paired fixed-transect baseline survey on the **same day** at each node;
3. hard rule: TNC collection must remain within **14 days before or after** the paired baseline fixed-transect survey;
4. record exact date and time for every core;
5. do not post-hoc select a narrower month, tide or time-of-day subset after the future response is known.

A historical feasibility audit shows why this is necessary: the 28 latest-positive 2025 nodes were surveyed across roughly **71 days**, and the densest historical 28-day window contained only **19 of 33** recent positive nodes. Routine monitoring dates therefore cannot simply be reused as though they were a synchronized physiological baseline.

If the routine monitoring calendar cannot meet the frozen timing window, conduct a **dedicated additional baseline fixed-transect survey** using the same meter-mark frequency and Braun-Blanquet protocol during the TNC campaign. Do not solve the scheduling problem by widening the seasonal window.

Samples outside the +/-14-day baseline-alignment rule are not primary-confirmatory samples.

## Core placement

At each eligible transect:

1. identify the permanent transect / meter-mark area;
2. place destructive cores adjacent to the monitored line or marks so the permanent observation unit is not damaged;
3. use one fixed offset rule chosen before the first outcome-bearing sample;
4. collect at least 3 independent below-ground cores per node;
5. record node ID, core ID, GPS, water depth, collection date/time and offset from the permanent transect.

If permitting requires a different placement rule, change and document the protocol **before** the first outcome-bearing core is collected.

## Rhizome tissue standardization

The primary predictor is:

> rhizome total non-structural carbohydrate (TNC) = soluble NSC + starch.

Use one fixed **horizontal-rhizome tissue class** across all nodes.

Before the field campaign, run a response-independent tissue-mass pilot on *Thalassia* material to freeze:

- the ontogenetic position of the rhizome segment relative to a living short shoot / meristem;
- segment length or dry-mass target;
- removal of root, sheath and short-shoot tissue;
- minimum analyzable dry mass.

The pilot may establish laboratory feasibility only. It cannot inspect a future biological response.

Do not mix apical, old distal and vertical short-shoot tissues opportunistically across nodes.

Node-level primary predictor:

> median TNC across valid independent cores.

## Analytical method

Seagrass NSC values are strongly method-dependent. The primary study therefore uses one laboratory workflow throughout.

Preferred analytical standard:

- HPLC-based seagrass NSC workflow following the logic of Sørensen et al. (2018);
- quantify soluble NSC and starch separately;
- define TNC as their prespecified sum;
- report concentrations on one dry-mass basis;
- use the same extraction solvent, extraction schedule, starch treatment/hydrolysis and calibration throughout.

Sørensen et al. found HPLC substantially more precise than the common phenol-sulfuric colorimetric assay and showed that extraction and starch-solubilization choices materially change estimated NSC. The method must therefore be frozen before future outcome access.

### Species-matrix pilot

Because the standardized analytical paper was developed on another seagrass species, run a small *Thalassia* matrix pilot before the outcome-bearing campaign.

The pilot can determine:

- adequate tissue mass;
- extraction recovery;
- dilution range;
- chromatographic resolution;
- technical replicate precision.

It cannot choose a method by whichever one later correlates best with meadow outcome.

## Sample preservation and laboratory blinding

Before the first field sample, freeze:

- metabolic-arrest / preservation procedure;
- maximum allowed collection-to-preservation interval;
- transport temperature;
- long-term storage condition;
- drying / grinding procedure;
- assay batch structure.

For every core record collection time and preservation start time.

Randomize samples across assay batches with respect to bay and baseline state. Include technical standards and controls.

The laboratory cannot be blinded to collection metadata that are needed for sample handling, but future meadow outcome does not yet exist and therefore cannot affect assay order.

## Nutrient-state diagnostic

Collect a contemporaneous leaf sample for:

- %N;
- %P;
- N:P.

Reason: high rhizome carbohydrate can mean large reserve, but it can also arise when nutrient limitation suppresses growth demand and carbohydrates accumulate.

This is a **secondary mechanism diagnostic**.

Primary inference remains the prospective TNC coefficient. Do not replace a null TNC result with a nutrient-adjusted or residualized carbohydrate metric.

If coverage is adequate, freeze one sensitivity model adding leaf nutrient status before the future outcome is opened.

## Other secondary clonal measurements

Collect when feasible:

- below-ground dry biomass per area;
- rhizome branching density;
- meristem density;
- rhizome diameter;
- internode length;
- below-ground : above-ground biomass ratio;
- local shoot density at the sampled patch;
- optional validated genet/clonal-continuity marker.

These cannot replace a null primary TNC result.

## Existing baseline state

At the paired fixed-transect baseline retain:

- focal frequency;
- Braun-Blanquet all-point state;
- blade length where collected;
- shoot density where collected;
- water body;
- survey timing.

These are baseline controls / context, not new reserve measurements.

## Future endpoint

Primary:

> next fixed-transect survey focal frequency - baseline focal frequency.

Secondary:

- next Braun-Blanquet minus baseline;
- next blade length minus baseline;
- next shoot density minus baseline.

Binary re-recording / reappearance is not the primary mechanism endpoint and must not be described as recovery.

## Primary prospective model

The focal test is the standardized TNC coefficient in the predeclared model:

```text
future_delta_frequency
  ~ baseline_frequency
  + baseline_Braun_Blanquet
  + rhizome_TNC
  + water_body
```

Directional hypothesis:

> higher baseline rhizome TNC predicts more positive / less negative future change in focal frequency.

Freeze the node-level bootstrap or permutation rule before future response access.

## Interpretation

### Supported

A supported positive TNC coefficient is consistent with below-ground reserve state contributing information about future meadow persistence/resistance beyond current above-ground state.

It does **not** by itself prove causal clonal buffering.

### Unsupported with adequate precision

If the primary TNC interval is unsupported while the >=30-node / >=8-per-bay precision gate is met, the study weakens rhizome TNC as the primary measured reserve explanation under this design.

Do not rescue it by selecting starch, soluble sugar, below-ground biomass or a clonal trait after outcome access.

### Unsupported below the precision gate

If the sample falls below 30 nodes or any bay falls below 8 nodes, retain the estimate and uncertainty as a pilot. Do not use the null to reject the reserve-buffering hypothesis.

## Relationship to other Tampa mechanism tests

Keep the TNC primary test analytically separate from:

- direct hydrodynamic attenuation;
- high-frequency temperature/salinity/PAR;
- canopy/epiphyte optical measurements.

Do not add a TNC x attenuation or TNC x stress interaction after viewing the future outcome. Any integrated multiple-buffer model must be frozen in advance and will require more replication than the current Tampa network probably supplies.

## Field decision rule

Do not begin the outcome-bearing prospective study until all are frozen:

- contemporaneous eligible node list and alternates;
- core offset geometry;
- number and diameter/depth of cores;
- one <=28-day campaign window;
- +/-14-day baseline-survey alignment;
- horizontal-rhizome tissue class;
- preservation / metabolic-arrest procedure;
- *Thalassia* matrix pilot;
- HPLC extraction and quantification workflow;
- soluble NSC and starch definitions;
- dry-mass basis;
- leaf N/P diagnostic protocol;
- future survey window;
- primary model code;
- bootstrap/permutation rule;
- exclusion and missing-data rules.

The scientific value comes from measuring the hidden biological state **before** the future quantitative response is known.
