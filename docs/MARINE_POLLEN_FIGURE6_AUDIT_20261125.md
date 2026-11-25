# Direct marine animal pollen transfer: ordinal Fig. 6 audit

2026-11-25 JST. Original published PDF acquired from the University of Edinburgh repository (https://www.pure.ed.ac.uk/ws/files/28992590/ncomms12980.pdf), DOI 10.1038/ncomms12980, archive 14985411249 / run 45531042729. Archive SHA256 fbc015db8390a554621eba991dace725083ddea5baab9c86be20c916e83f445f; PDF SHA256 009f7f76fa6ee20e2f6974446bdce06de38d656c2d26c4bfc1d651c5d35ae645; Europe PMC XML DOI and checksum verified. Supplement downloads timed out. PDF web screenshot cache miss, local pdftoppm render succeeded. Printed page 4, PDF page 5. Manual visual read of all 60 Fig. 6 cells (two treatments x 6 distances x 5 displayed trials), followed by automated modal pixel-color extraction from cell interiors; all 60 agree. This is published figure transcription, not acquired raw individual-flower records. Legend: -1 no record, 0 no tubes, 1 positive <10, 2 regular 10–99, 3 high >=100. Use figure legend for thresholds, no inferred continuous counts. Original data and figure unchanged.

| Distance cm | Recorded per arm | Control positive | Fauna positive |
|---:|---:|---:|---:|
|15|4|0|4|
|30|5|1|5|
|45|4|1|4|
|60|4|0|3|
|90|5|2|5|
|150|5|1|4|
|All|27|5|25|

Category counts control [22,5,0,0], fauna [2,3,14,8]; three no records in each arm. Positive fractions 18.52% vs 92.59%, RD +74.07 pp, ratio 5.0. At least ten tubes: 0/27 vs 22/27; among recorded positive cells 0/5 vs 22/25. At least 100 tubes: 0 vs 8. All distances have higher recorded positive fractions with fauna. Descriptive 90–150 cm subset 3/10 vs 9/10 positive, >=10 tubes 0/10 vs 9/10. Not a prespecified distance group, not evidence of distance-invariant effects or an estimate of transport range in nature. Hypothetical extreme binary completions of six missing cells yield RD [17/30,23/30] = [56.67,76.67] pp, only arithmetic sensitivity; no record may be unopened flower and is not a measured failure. No imputations in primary result.

Pearson descriptive cross-tab statistic from displayed four categories is 39.1667 (even if equal missing category included); original reports 38.75, df4. Displayed fauna categories by six distances give 14.5366, original reports 10.465, df15. The discrepancy is unresolved; cannot reproduce original inference or claim an error in raw data. No reconstructed individual-level p-values or confidence intervals. Four physical Y-maze mesocosms, randomized treatment rotation on nights, two female flowers per tank; published figure does not supply tank-night ID or complete assignment and exposure history. Even where flowers differ within tank, independent assignment does not follow. Do not count 27 cells as independent experimental replicates or pair row indices across treatments as known matched tanks.

Both treatments lacked water flow for the overnight tube assay; fauna 30–90/L. Small control signal may reflect residual pollen. Data establish transfer and tube growth in still water, not actual fertilization, seed set, recruitment, relative animal vs water contribution in nature, or downstream demographic rescue. Authors already proposed reproductive assurance and extension of water-mediated range, so ordinal effect accounting is the additional descriptive contribution, not discovery of animal pollination. Do not merge with separate daytime trap or pollen-addition experiments as a cohort.

Reproduce: python analysis/177_marine_pollen_figure6_audit.py github-actions-artifact-14985411249.zip --out output (Python/Pillow and Poppler pdftoppm). Executed locally with both archive and document checksum and 60-cell agreement. Committed core code matches executed calculation; not separately replayed in CI. Compact transcribed cells and summary stored here, not original PDF. Next decisive data: recover actual mesocosm/night assignment from authors, measure fauna x flow x distance interaction at tank level and follow fruit/seed outcomes. Keep Tampa epiphyte and otter pathways distinct. Main/manuscript unchanged.
