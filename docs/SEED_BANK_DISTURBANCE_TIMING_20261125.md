# Seed-bank value depends on timing of hypothetical disturbance (2026-11-25)

## Scope and source
Follow-up to analysis/184 using Jørgensen, Labouriau & Olesen (2019), DOI 10.1371/journal.pone.0215157. Same verified original source archive 14918042341, SHA256 74f0c656295996b258907469cbbfd15a75df41744279d39a74947fbd74ad5374. New source linkage of s002.xlsx time series (SHA256 f357afbefd89a554e38952829d17cb94f05a7b55276fed06dd3b315784a4b57f) to s003.xlsx endpoint fates by exact mesocosm, pot, size and depth. 1070 time rows, 100 pot records, unique keys, 100/100 linked. Endpoint component counts sum to source totals, which do not always equal nominal 15 planted seeds; retain discrepancies. Primary sorted cohort 30 pots, 5 tanks, 2 size classes x 3 depths, nominal 450 seeds, all ten observation days 16–74 present, nondecreasing counts and final day 74 agrees with recorded terminal emergence in every pot. Source labels sorted harvest 10 weeks but last recorded day 74; keep both labels, no assumed correction. Different 8/24-week unsorted harvests not longitudinal cohorts. Two 24-week pot histories (11,12) decrease from day 115 to day 140; no conversion to individual cumulative emergence events. No actual disturbance experiment or follow-up germination of terminal viable seeds.

## Observed sorted seed contrasts
|depth cm|size|day 16|day 26|day 74 emergence|viable unemerged|source total|
|---:|---|---:|---:|---:|---:|---:|
|2|small|25|28|31|18|73|
|2|large|35|37|40|22|75|
|4|small|22|34|37|15|75|
|4|large|13|22|26|33|75|
|6|small|2|13|15|18|74|
|6|large|6|20|22|29|74|

## Counterfactual calculation
For an imposed single pulse at observed day d, remove fraction h of the seedlings already recorded as emerged by d. Assume all subsequent observed emergence and final viable seed counts unchanged, all retained emergents contribute equally, and common fraction q of final viable unemerged seeds eventually yields recruited seedlings. Then potential count score R=E_final-h*E_d+q*V. Neither h nor q estimated; no mortality after terminal observation, altered germination, density dependence, or feedback included. Not a fitted recovery forecast, realized recruitment or proof of a seed-bank insurance effect. For equal seed counts at 4 cm, large-minus-small score = -11+h*(E_small,d-E_large,d)+18*q. Break-even q at day 16 = (11-9h)/18; day 26 = (11-12h)/18. Vary all ten recorded days and h=0,.25,.5,.75,1. Thresholds outside [0,1] mean no interior crossing; negative threshold with positive bank difference implies large is higher throughout feasible q.

| day | loss fraction h | q threshold at 4 cm | leave-one-tank-out threshold range | difference at q=.25 |
|---:|---:|---:|---|---:|
|26|0|.611111|.416667–.857143|-6.5|
|26|.5|.277778|.166667–.392857|-.5|
|26|1|-.055556|-.083333–0|+5.5|
|16|1|.111111|-.055556–.363636|+2.5|
|74|1|0|0–0|+4.5|

At q=.25 and day 26 h=1, paired leave-one-tank-out difference remains positive +2.75 to +5.5 (four tanks). With h=.5 range -2 to +1. These are scenario sensitivities, not confidence intervals. With no pulse at 2 and 6 cm, large has more terminal emergents and viable seeds; cannot generalize the 4 cm crossover to every depth. No estimate of seasonal timing or actual disturbance frequency. Same mass budget divides large-seed count score by 1.670435358, the separate sampled mean mass ratio (not actual individual costs or experimentally compared density). At 4 cm and h=0 break-even q=4.507616, unattainable; at day26 h=1, q=.127313 (illustrative only). At 2 and 6 cm large has lower terminal viable seed count per hypothetical equal initial seed-mass budget; no assumption that large is universally superior.

## Next empirical gate
Need longitudinal seed-bank fate under actual disturbance schedules, with seed size classes, non-destructive emergence/survival, post-harvest viable-to-emergence transition, and repeat disturbance or field seasonal cohorts. The original experiment and previous analysis 184 identify stage differences, but not actual seasonal conversion probability or selection for bet-hedging. Prior studies of seed bank longevity and disturbance should be credited, not claimed novel. No change to main, Paper A or TNC. Local exact-source run completed. Git blob 6fd40c7bea7e35cb68162e5bd250c1fa30a4c2ae equals local code. Result SHA256 cef6933a1f15f7eabbfee6dae770e3e6a502fa9f81b793bf7e8099a3e5f733a6. Independent CI not run. Reproduce: python analysis/185_seed_bank_disturbance_timing.py <verified archive> --out results.json.
