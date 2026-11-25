#!/usr/bin/env python3
"""Published-table arithmetic only. No raw data, factorial estimate or pooled effect."""
import json, math
# van Tussenbroek et al. 2016, Ecology and Evolution, Table 2, DOI 10.1002/ece3.2309
TRAPS=[
    dict(site='Back-Reef',date='2006-04-26',traps=120,positive=16,grains=67,mean_distance_m=2.02,initial_distance_m=.4,pollen_neighborhood_m2=2.76),
    dict(site='Back-Reef',date='2006-05-10',traps=120,positive=17,grains=57,mean_distance_m=1.15,initial_distance_m=.4,pollen_neighborhood_m2=10.80),
    dict(site='Mid-Lagoon',date='2006-05-25',traps=100,positive=23,grains=71,mean_distance_m=.66,initial_distance_m=.2,pollen_neighborhood_m2=1.65),
]
# van Tussenbroek et al. 2016, Oecologia, Table 4, DOI 10.1007/s00442-016-3665-7
MEADOWS=[
    dict(site='Oostdijk',meadow='Channel',n=10,vegetative_biomass=106.7,leaf_biomass=43.2,reproductive_biomass=1.7,foliar_shoots=1194,reproductive_shoots=115,total_spathes=381,estimated_annual_seeds=167),
    dict(site='Oostdijk',meadow='Continuous',n=20,vegetative_biomass=103.9,leaf_biomass=32.6,reproductive_biomass=4.6,foliar_shoots=6958,reproductive_shoots=687,total_spathes=2934,estimated_annual_seeds=5571),
    dict(site='Oostdijk',meadow='Elevated',n=10,vegetative_biomass=47.1,leaf_biomass=12.9,reproductive_biomass=2.7,foliar_shoots=3973,reproductive_shoots=586,total_spathes=2215,estimated_annual_seeds=3529),
    dict(site='Goese Sas',meadow='Fragmented',n=20,vegetative_biomass=75.6,leaf_biomass=22.4,reproductive_biomass=4.8,foliar_shoots=4927,reproductive_shoots=662,total_spathes=2324,estimated_annual_seeds=3064),
]

def analyze():
    traps=[]
    for a in TRAPS:
        n,k,g=a['traps'],a['positive'],a['grains']
        assert 0<k<=n and g>=k
        traps.append(dict(**a,capture_incidence=k/n,positive_mean=g/k,all_trap_mean=g/n))
    a,b=traps[:2]
    assert a['site']==b['site'] and a['traps']==b['traps'] and a['initial_distance_m']==b['initial_distance_m']
    p,q=a['capture_incidence'],b['capture_incidence'];u,v=a['positive_mean'],b['positive_mean']
    inc=(q-p)*(u+v)/2;mag=(v-u)*(p+q)/2
    assert math.isclose(inc+mag,b['all_trap_mean']-a['all_trap_mean'])
    matched_design=dict(mean_distance_ratio=b['mean_distance_m']/a['mean_distance_m'],incidence_difference=q-p,positive_mean_ratio=v/u,mean_count_ratio=b['all_trap_mean']/a['all_trap_mean'],mean_count_difference=b['all_trap_mean']-a['all_trap_mean'],incidence_component=inc,magnitude_component=mag)
    # Sharp aggregate-data bounds: at most floor((G-K)/(t-1)) positives can reach t; if G>K*(t-1), at least one must.
    for r in traps:
        k,g=r['positive'],r['grains'];r['threshold_bounds']={}
        for t in (2,5,10):
            lo=int(g>k*(t-1));hi=min(k,(g-k)//(t-1));assert lo<=hi
            r['threshold_bounds'][str(t)]=[lo,hi]
    rows=[]
    for m in MEADOWS:
        r=m['reproductive_shoots'];s=m['total_spathes'];y=m['estimated_annual_seeds']
        z=dict(**m,spathes_per_reproductive_shoot=s/r,annual_seeds_per_total_spathe_index=y/s,annual_seeds_per_reproductive_shoot_index=y/r,annual_seeds_per_vegetative_biomass_index=y/m['vegetative_biomass'])
        assert math.isclose(r*z['spathes_per_reproductive_shoot']*z['annual_seeds_per_total_spathe_index'],y)
        rows.append(z)
    ref=next(x for x in rows if x['meadow']=='Continuous')
    contrasts={};fields=['reproductive_shoots','spathes_per_reproductive_shoot','annual_seeds_per_total_spathe_index']
    for r in rows:
        if r==ref:continue
        ratios={k:r[k]/ref[k] for k in fields};y=r['estimated_annual_seeds']/ref['estimated_annual_seeds']
        assert math.isclose(math.prod(ratios.values()),y)
        contrasts[r['meadow']]=dict(seed_ratio=y,foliar_shoot_ratio=r['foliar_shoots']/ref['foliar_shoots'],vegetative_biomass_ratio=r['vegetative_biomass']/ref['vegetative_biomass'],reproductive_biomass_ratio=r['reproductive_biomass']/ref['reproductive_biomass'],total_spathe_ratio=r['total_spathes']/ref['total_spathes'],component_ratios=ratios,log_ratio_shares={k:math.log(v)/math.log(y) for k,v in ratios.items()},estimated_seed_per_reproductive_shoot_ratio=r['annual_seeds_per_reproductive_shoot_index']/ref['annual_seeds_per_reproductive_shoot_index'])
    compensation=15/8.2
    return dict(status='published_table_recalculation_not_raw_data_or_causal_test',trap_doi='10.1002/ece3.2309',trap_table=2,trap_trials=traps,same_design_descriptive_contrast=matched_design,meadow_doi='10.1007/s00442-016-3665-7',meadow_table=4,meadow_rows=rows,versus_continuous=contrasts,illustrative_linear_supply_compensation=dict(source_doi='10.3354/meps08870',male_flower_density_ratio=8.2/15,required_per_donor_integrated_delivery_multiplier=compensation,illustrative_disk_radius_multiplier=math.sqrt(compensation),status='not_estimated_in_nature'),limits=['Table 2 gives aggregate counts, not trap-level distributions or independent experimental units. Two Back-Reef trials have same design but no paired trap IDs. Mid-Lagoon different spatial sampling. No exclusive water-vector attribution or female fertilization estimate.', 'Table 4 annual seed production is an author estimate with assumed seasonal constancy, not realized annual seed yield. Ratios of reported meadow means and exact arithmetic only, not per-spathe success probabilities or individual causal components. Fragmented and continuous sites differ geographically; no new significance test or meta-analysis.', '2016 animal experiment (10.1038/ncomms12980) measured pollen tubes in no-flow tanks; flow-on/off experiment measured visitation, not tube counts. No comparable 2x2 vector x flow reproductive outcome. No factorial interaction sign identifiable.'])
if __name__=='__main__':
    print(json.dumps(analyze(),indent=2,sort_keys=True,allow_nan=False))
