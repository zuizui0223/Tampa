# Otter genetics source boundary and adult reference coverage

## Foster / sea otter
Foster et al. Science 2021 DOI 10.1126/science.abf2343 reported 30% higher allelic richness and 6% higher genotypic diversity in established (20–30 yr) otter areas. Foster's 2021 UVic dissertation chapter 3 is explicitly a pre-publication revision, not the final Science paper. It documents clone correction before allele-richness calculations, and no clear heterozygosity association (printed pp. 51, 53, 56). The 25% contrast reported in the thesis is a different analysis version; use the final abstract's 30% for the paper. The thesis PDF table's horizontal clone-group lines and site-category spans could not be visually verified via the available PDF screenshot route; do not use extracted table labels to infer site-level effects. No novel Foster effect estimate or causal conclusion.

Dryad 10.5061/dryad.ns1rn8pt4, version 128223, previous attempts: bulk version 404; dataset bulk 401. Public landing page reports no displayed files. Direct local network access failed DNS. New analysis/147 follows only official public file listing and advertised download links, with explicit STOP on denial. It also inventories Wasson et al. 2022, DOI 10.7291/D1FX0Z (Elkhorn Slough otter abundance and eelgrass mapped area); separate ecological extent endpoint, no genetics and not linked to Foster. Do not label inventory or CI success as successful source acquisition unless source manifest confirms it.

## Posidonia original-source new arithmetic
Original CSV SHA256 3081acdbd8b7bc330851ebf2057a4d4a7f279d8c3484e2c38f7c78494d6aca9d; source DOI 10.5061/dryad.dfn2z3577. Prior stage-marker CI run 45383439345 succeeded. New post-outcome finite-pool comparison after complete-case screening and within-group exact marker-profile deduplication: take r=6 adult profiles as reference, t=5 disjoint adult profiles as test, versus t=5 independent seedling profiles. Count distinct locus-specific marker alleles absent from the reference but present in test. For adult pool N with k carriers, A(n)=C(N-k,n)/C(N,n); for seedling pool M with l carriers, B(n)=C(M-l,n)/C(M,n). Expected new allele count in adult test = sum[A(r)-A(r+t)]; seedling test = sum[A(r)(1-B(t))]. Exact expected counts, not p-values or uncertainty intervals.

| site/cohort | withheld adults | seedlings | difference | seedling contribution absent from entire recorded adult pool |
|---|---:|---:|---:|---:|
| Parker 2013 | 2.1580 | 3.3835 | 1.2255 | 2.8893 |
| Parker 2014 | 2.1580 | 4.4038 | 2.2458 | 3.9263 |
| Stark 2013 | 3.5585 | 2.5106 | -1.0479 | .3704 |
| Stark 2014 | 3.5585 | 2.9871 | -.5714 | .1667 |
| Thompson 2013 | 4.4428 | 4.7658 | .3230 | 1.1586 |
| Thompson 2014 | 4.4428 | 6.4888 | 2.0460 | 3.0525 |

At r=2..6 with t=5, Parker 2013 can change direction (min -.0275), other contrasts retain signs. Repeated-profile-inclusive adult tests yield 4/6 positive too, with differences +2.7817,+3.8209,-.9656,-.4776,+1.6062,+3.3656. Two cohorts per site share adult reference. All comparisons conditional on sampled finite pools and very small reference samples, noncontemporaneous adults/seedlings, ambiguous ploidy and exact marker profiles rather than confirmed genets. More novel alleles in seedling samples than in withheld adult samples is not evidence of immigration, causal recruitment mechanism, or net genetic diversity increase. This diagnostic distinguishes complementarity to adult reference from previous absolute allele richness, and cannot infer allelic novelty in a full meadow.

Local calculation and synthetic test executed. analysis/148 reproduces from original pinned member via analysis/146. Dedicated CI added in .github/workflows/otter-source-posidonia-coverage.yml; independent CI result and new source acquisition pending at time of writing. No Tampa Paper A or prospective TNC changes. Draft/unmerged.
