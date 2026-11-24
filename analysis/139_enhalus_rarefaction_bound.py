#!/usr/bin/env python3
"""Published-count arithmetic, not original genotype analysis.

Yu et al. 2019, doi:10.1002/ece3.5106.
Two 20 x 20 m plots, shoots sampled on a 1 m grid.
Conditional rarefaction bounds for observed finite ramet collection.
"""
from math import comb
import json

def bounds(N,G,n):
    if not 1 <= G <= N or not 1 <= n <= N:
        raise ValueError("invalid sample or group count")
    def p(k):
        return 1 - (comb(N-k,n)/comb(N,n) if N-k>=n else 0)
    # Inclusion probability is discretely concave in clone size.
    # Min: all but one clone singleton. Max: most balanced integer sizes.
    k,r=divmod(N,G)
    lo=(G-1)*p(1)+p(N-G+1)
    hi=(G-r)*p(k)+r*p(k+1)
    return lo,hi

def analyze():
    a={"ramets":271,"genets":214,"cover_pct":41.43,"alleles":44}
    b={"ramets":395,"genets":255,"cover_pct":85.21,"alleles":49}
    for d in (a,b): d["R"]=(d["genets"]-1)/(d["ramets"]-1)
    lo,hi=bounds(b["ramets"],b["genets"],a["ramets"])
    assert abs(hi-205.17850028914734)<1e-10
    assert abs(lo-175.2632911392405)<1e-10
    assert bounds(10,10,5)==(5,5)
    return {"status":"published_counts_arithmetic_not_raw_genotype_inference",
        "doi":"10.1002/ece3.5106","fragmented_plot":a,"continuous_plot":b,
        "fragmented_relative_ramet_count_change":271/395-1,
        "fragmented_relative_observed_genet_count_change":214/255-1,
        "fragmented_relative_R_change":a["R"]/b["R"]-1,
        "continuous_expected_rarefied_genet_count_bounds_at_n271":[lo,hi],
        "fragmented_observed_genets_minus_continuous_max_expected_rarefied":214-hi,
        "limitations":["Finite-collection individual-based random rarefaction, not a spatial rarefaction or estimate of true population size.",
           "An observed count exceeding an upper bound on expected richness does not imply statistical significance or impossible random draws.",
           "One fragmented and one continuous plot; disturbance, pollution, and habitat are confounded.",
           "Genotypic richness is not allele richness, heterozygosity, number of newly produced genets, or measured sexual recruitment.",
           "Raw workbook verification and clone identity checks are separate pending tasks."]}
if __name__=="__main__": print(json.dumps(analyze(),indent=2,sort_keys=True))
