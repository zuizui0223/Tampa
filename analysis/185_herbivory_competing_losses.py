#!/usr/bin/env python3
"""Published marginal arithmetic, not raw data or an identified causal mediation."""
import csv,json,hashlib,sys
from pathlib import Path
O=Path(__file__).resolve().parent
def bounds(d,m0,m1):
    assert 0<=d<=1 and 0<=m0<=1 and d+m0<=1 and m0<=m1<=1
    low=max(0,d+m1-1);high=min(d,m1);high_mono=min(d,m1-m0)
    assert low<=high_mono<=high
    return dict(damaged_exposed=d,mature_exposed=m0,mature_excluded=m1,
                maturation_RD=m1-m0,maturation_RR=m1/m0,
                hypothetical_mature_under_exclusion_among_damaged_bounds=[low/d,high/d],
                hypothetical_mature_under_exclusion_among_damaged_bounds_monotone=[low/d,high_mono/d],
                hypothetical_nonmature_under_exclusion_among_damaged_lower=1-high/d,
                hypothetical_nonmature_under_exclusion_among_damaged_lower_monotone=1-high_mono/d)
contrasts=[dict(reference='open',**bounds(.843,.101,.375)),dict(reference='partial_cage',**bounds(.795,.067,.375))]
male2=dict(initial_marked_including_3_carried_over=40,remained_closed=13,included=27,consumed_before_anthesis=5,consumed_after_anthesis=7,remained_postanthesis=15)
assert sum(male2[k] for k in ['consumed_before_anthesis','consumed_after_anthesis','remained_postanthesis'])==male2['included']
male2.update(total_loss_fraction=12/27,pre_anthesis_loss_fraction=5/27,post_anthesis_loss_fraction=7/27,pre_fraction_of_consumed=5/12,fraction_of_included_not_consumed_before_anthesis=22/27,pre_printed_percent=9)
r={'status':'published marginal arithmetic; source PDF verification for Thalassia; not raw data or population bounds with sampling uncertainty',
'piazzi2000':{'doi':'10.1515/BOT.2000.058','contrasts':contrasts},
'balestri2003':{'doi':'10.1016/S0304-3770(02)00151-1','mature_fruit_per_hermaphroditic_flower_exposed':.031,'mature_fruit_per_hermaphroditic_flower_excluded':.112,'RD':.112-.031,'RR':.112/.031,'relative_nonmaturation_reduction':(.112-.031)/(1-.031),'reported_abortion_loss_under_exclusion':.865,'potential_overlap_with_piazzi2000':True},
'planes2011':{'doi':'10.3354/meps09089','inflorescences_m2_cage':1.7,'inflorescences_m2_open':.4,'ratio':1.7/.4,'n_plots_per_arm':3,'shoot_density_test_reported':'F=0.105, p>0.5','protected_vs_unprotected_flowering_not_significant_at_conservative_alpha':True},
'verges2007':{'doi':'10.1007/s00442-006-0606-x','fresh_inflorescence_vs_leaf_consumption_ratio_reported_lower':2,'ground_leaf_vs_inflorescence_ratio_reported_approx':2,'leaf_extract_vs_inflorescence_ratio_reported':17,'leaf1_toughness_N':.74,'leaf2_toughness_N':.68,'bract_toughness_N':.37},
'thalassia2008':{'doi':'10.3354/meps07212','pdf_sha256':'f581737ea0b5691c5f78755c81c6a0e97483108cf7f910eba7d50a997f4f14bc','trial2':male2,'trial1_included':37,'trial1_consumed_total':7,'female_opened':34,'female_entirely_consumed':0,'female_bite_marks':1,'limits':'Different trials and dates, no experimental sex comparison, no pollen delivery or reproductive effect. 64 included male records are not all dehisced; text says 64 dehisced despite pre-anthesis consumption. No rate pooled.'},
'limits':['Published means rounded. Bounds use hypothetical common target marginal distributions, not confidence intervals or identified actual flower fates. Random assignment comparable only if design and cage effects support exchangeability; 2000/2003 may report same experiment.','M0 and D0 categories mutually exclusive for accounting under reported definition of mature undamaged inflorescences. Monotonicity is not proven. Cage effects can include other processes.','Flower-level fruit proportion differs from inflorescence-level maturity, cannot combine them.','No new data on actual Enhalus causes of loss or sea turtle effects. No formal meta-analysis.']}
if len(sys.argv)>1:
    p=Path(sys.argv[1]);assert hashlib.sha256(p.read_bytes()).hexdigest()==r['thalassia2008']['pdf_sha256']
(O/'results.json').write_text(json.dumps(r,indent=2,ensure_ascii=False)+'\n')
with (O/'competing_loss_bounds.csv').open('w') as f:
    w=csv.DictWriter(f,fieldnames=contrasts[0]);w.writeheader();w.writerows(contrasts)
print(json.dumps(r,indent=2,ensure_ascii=False))
