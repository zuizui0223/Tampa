#!/usr/bin/env python3
"""Marine pollination supply / failure accounting from published summaries only.

No digitized heatmap cells, raw individual flowers, new fitted models or pooled
treatment effects. Source units and rounded values deliberately retained.
"""
import json, math
from itertools import combinations

# Van Tussenbroek et al. 2010, DOI 10.3354/meps08870, abstract, Methods, Results.
# 10 haphazard 4-m2 quadrats per year for flowers/buds at pre-anthesis.
# Shoot density is a separately reported site summary. Fruit set is control arm.
YEARS = [
    dict(year=2008, shoots_m2=700, male_flower_or_bud_per_4m2=15.0,
         female_flower_or_bud_per_4m2=10.2, pollen_ovule_ratio=67000, fruit_set=.86),
    dict(year=2009, shoots_m2=689, male_flower_or_bud_per_4m2=8.2,
         female_flower_or_bud_per_4m2=11.7, pollen_ovule_ratio=37000, fruit_set=.65),
]
CONTRASTS = [
    dict(year=2008, low=.60, high=.86, design="male-flower removal versus unmanipulated control"),
    dict(year=2009, low=.65, high=.91, design="natural control versus artificial pollen supplementation"),
]

# Shelton 2008, DOI 10.1890/07-1835.1, Table 1, May-June 2006.
# [site, lower flowering-area male proportion, upper proportion, male spadices/m2].
# Bounds reflect authors' assumptions about unflowered area; NOT confidence intervals.
SHELTON = {
    "P. serrulatus": [
        ["KD", .032, .059, .63], ["CR", .006, .010, .35], ["SD", 0., 0., 0.],
        ["MB", .018, .032, .32], ["SS", .002, .004, .11], ["OZ", .006, .012, .06],
        ["TH", .008, .010, .43]],
    "P. scouleri": [
        ["KD", .022, .039, .65], ["SD", .014, .025, .65],
        ["MB", .017, .031, .48], ["SS", .001, .001, .72]],
}

def robust_rank_pairs(rows):
    counts = dict(same=0, opposite=0, area_uncertain=0, density_tie=0)
    opposites = []
    for a,b in combinations(rows, 2):
        area = 1 if a[1] > b[2] else -1 if b[1] > a[2] else 0
        density = (a[3]>b[3])-(a[3]<b[3])
        key = ("area_uncertain" if area==0 else "density_tie" if density==0
               else "same" if area==density else "opposite")
        counts[key] += 1
        if key=="opposite":
            opposites.append([a[0],b[0]])
    assert sum(counts.values())==len(rows)*(len(rows)-1)//2
    return dict(counts=counts, opposite_site_pairs=opposites)

def analyze():
    a,b=YEARS
    change={k:100*(b[k]/a[k]-1) for k in
            ("shoots_m2","male_flower_or_bud_per_4m2",
             "female_flower_or_bud_per_4m2","pollen_ovule_ratio")}
    contrasts=[]
    for x in CONTRASTS:
        low,high=x["low"],x["high"]
        contrasts.append(dict(**x,fruit_difference_pp=100*(high-low),
                              fruit_rr=high/low,nonfruit_rr=(1-high)/(1-low),
                              relative_nonfruit_reduction=1-(1-high)/(1-low)))
    # Van Tussenbroek et al. 2016 DOI 10.1038/ncomms12980, Results.
    # Same 6 trials, published means +/- SEM: added 9 +/- 3.9, removed 3 +/- 0.8.
    # SEM of net difference unidentified; use algebraic Cauchy-Schwarz bounds.
    # Not a newly conducted significance test or exact confidence interval.
    gain,loss,s_gain,s_loss=9.,3.,3.9,.8
    min_se,max_se=abs(s_gain-s_loss),s_gain+s_loss
    tcrit=2.570581835636314
    interval=lambda se:[gain-loss-tcrit*se,gain-loss+tcrit*se]
    return {
        "status":"published_summary_arithmetic_and_source_boundary_not_raw_reanalysis",
        "thalassia_field_2010":{
            "source_doi":"10.3354/meps08870","source_years":YEARS,"percent_changes":change,
            "male_flower_or_bud_density_m2":[x["male_flower_or_bud_per_4m2"]/4 for x in YEARS],
            "female_flower_or_bud_density_m2":[x["female_flower_or_bud_per_4m2"]/4 for x in YEARS],
            "male_flower_or_bud_per_1000_shoots_ratio_of_site_means":[1000*x["male_flower_or_bud_per_4m2"]/4/x["shoots_m2"] for x in YEARS],
            "natural_control_fruit_set_difference_pp":100*(b["fruit_set"]-a["fruit_set"]),
            "within_year_contrasts":contrasts,
            "limits":"Two years, same site, different experiments; no common randomization, joint seed data, or site-paired individual records. Fruit set scored before ripe-fruit harvest; mature seeds conditional on retained fruits. Do not multiply early fruit set by selective later seed set to infer per-flower seed output."},
        "thalassia_animal_2016":{
            "source_doi":"10.1038/ncomms12980","n_fauna_trials":6,"n_control_trials":4,
            "minutes":15,"mean_gained":gain,"mean_lost":loss,
            "published_sem_gain":s_gain,"published_sem_loss":s_loss,
            "net_mean_gained":gain-loss,"sem_bound_unknown_paired_covariance":[min_se,max_se],
            "illustrative_t_interval_df5_min_sem":interval(min_se),
            "illustrative_t_interval_df5_max_sem":interval(max_se),
            "figure6_status":"NO_CELL_LEVEL_DATA_ACQUIRED",
            "limits":"Rounded means/SEM as published. Paired covariance unknown; t intervals are algebraic sensitivity under conventional t assumptions, not valid recovered CI. Control no grains gained/lost. Different mesocosm experiment shows tubes after animal presence; exact counts not measured for abundant tubes. No natural-flow factorial seed or fruit endpoint. No claim that animal pollen removal offsets male herbivory or that seed success is established."},
        "phyllospadix_2008":{
            "source_doi":"10.1890/07-1835.1","table_1_source_rows":SHELTON,
            "rank_audit_by_species":{k:robust_rank_pairs(v) for k,v in SHELTON.items()},
            "limits":"Published table, no raw ovule or individual data. Pairs share sites and are descriptive only. Robust strict nonoverlap criterion for male area; overlapping/touching bounds not ranked. Area proportion and spadix density are distinct quantities and neither directly measures delivered pollen. This is not animal-mediated pollination evidence."},
    }

if __name__=="__main__":
    x=analyze()
    assert all(math.isclose(c["fruit_difference_pp"],26.) for c in x["thalassia_field_2010"]["within_year_contrasts"])
    assert x["phyllospadix_2008"]["rank_audit_by_species"]["P. serrulatus"]["counts"]=={"same":14,"opposite":3,"area_uncertain":4,"density_tie":0}
    assert x["phyllospadix_2008"]["rank_audit_by_species"]["P. scouleri"]["counts"]=={"same":0,"opposite":3,"area_uncertain":3,"density_tie":0}
    print(json.dumps(x,indent=2,sort_keys=True,allow_nan=False))
