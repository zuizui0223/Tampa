#!/usr/bin/env python3
"""Scenario accounting of observed emergence trajectories and terminal viable seeds.
No disturbance was imposed. No future germination rate or seed-bank longevity fitted.
"""
import argparse, hashlib, io, json, zipfile
from pathlib import Path
import numpy as np
import pandas as pd
ARCHIVE='74f0c656295996b258907469cbbfd15a75df41744279d39a74947fbd74ad5374'
K=['Mesocosm ID','Pot ID','Seed size grouping','Seed burial depth (cm)']
SIZE=K[2];DEPTH=K[3]; DAYS=[16,19,21,26,34,40,47,55,62,74]
E='Total seedling emergence'; V='Viable seeds'; F='Unsuccessfully emerged seeds'; D='Dead seeds'; N='Total number of seeds'
def sha(b):return hashlib.sha256(b).hexdigest()
def calc(a,b,day,h,mass_ratio=1.):
    # large minus small, optionally on hypothetical equal initial seed-mass input.
    immediate=(a[E]-h*a[day])/mass_ratio-(b[E]-h*b[day]); bank=a[V]/mass_ratio-b[V]
    assert bank>0
    return {'early_loss_fraction':h,'day':day,'large_small_difference_before_bank':float(immediate),'large_small_bank_difference':float(bank),'break_even_common_bank_conversion':float(-immediate/bank),'large_small_difference_at_q_0_25':float(immediate+.25*bank)}
def analyze(path):
    raw=path.read_bytes();assert sha(raw)==ARCHIVE
    with zipfile.ZipFile(io.BytesIO(raw)) as z:src={k:z.read(k) for k in ['s001.xlsx','s002.xlsx','s003.xlsx']}
    s=pd.read_excel(io.BytesIO(src['s002.xlsx']));f=pd.read_excel(io.BytesIO(src['s003.xlsx']));w=pd.read_excel(io.BytesIO(src['s001.xlsx']),sheet_name='Seed weight');ratio=float(w[w.Seed=='L'].weight.mean()/w[w.Seed=='S'].weight.mean())
    assert len(s)==1070 and len(f)==100 and not s.duplicated(K+['Time (days)']).any() and not f.duplicated(K).any()
    assert (f[[E,V,F,D]].sum(axis=1)==f[N]).all()
    p=s.pivot(index=K,columns='Time (days)',values='Seedling emergence').reset_index().merge(f,on=K,validate='one_to_one',how='outer',indicator=True);assert len(p)==100 and p._merge.eq('both').all()
    sort=p[p[SIZE].isin(['large','small'])].copy();assert len(sort)==30 and sort['Time (weeks)'].eq(10).all() and sort[DAYS].notna().all().all() and sort[DAYS].diff(axis=1).iloc[:,1:].ge(0).all().all() and (sort[74]==sort[E]).all()
    assert sort.groupby([K[0],DEPTH,SIZE]).size().eq(1).all()
    out={}
    for depth,g in sort.groupby(DEPTH):
        a,b=(g[g[SIZE]==i][DAYS+[E,V,N,F,D]].sum() for i in ['large','small']);assert len(g)==10
        rec={'observed':{'large':{str(k):int(v) for k,v in a.items()},'small':{str(k):int(v) for k,v in b.items()}},'equal_count':[],'equal_seed_mass_illustrative':[]}
        for day in DAYS:
            for h in [0.,.25,.5,.75,1.]:
                row=calc(a,b,day,h);rr=[];dd=[]
                for tank in sorted(g[K[0]].unique()):
                    sub=g[g[K[0]]!=tank];aa,bb=(sub[sub[SIZE]==i][DAYS+[E,V]].sum() for i in ['large','small']);bank=aa[V]-bb[V]
                    if bank>0:
                        r=calc(aa,bb,day,h);rr.append(r['break_even_common_bank_conversion']);dd.append(r['large_small_difference_at_q_0_25'])
                row['leave_one_tank_out_threshold_range']= [min(rr),max(rr)] if rr else None
                row['leave_one_tank_out_difference_q_0_25_range']= [min(dd),max(dd)] if dd else None
                rec['equal_count'].append(row)
                # Some depths have a nonpositive bank difference on equal-mass scale.
                delta=(a[E]-h*a[day])/ratio-(b[E]-h*b[day]);bank=a[V]/ratio-b[V]
                rec['equal_seed_mass_illustrative'].append({'day':day,'early_loss_fraction':h,'large_small_difference_before_bank':float(delta),'large_small_bank_difference':float(bank),'break_even_q':float(-delta/bank) if bank!=0 else None,'large_small_difference_at_q_0_25':float(delta+.25*bank)})
        out[str(depth)]=rec
    # Longer unsorted harvest is a different cohort, with two decreasing recorded count histories.
    long=p[p['Time (weeks)']==24];days=DAYS+[95,115,140];bad=long.loc[long[days].diff(axis=1).iloc[:,1:].lt(0).any(axis=1),'Pot ID'].tolist()
    assert len(long)==35 and sorted(bad)==[11,12]
    longsum={str(depth):{str(k):int(v) for k,v in g[days+[E,V,N]].sum().items()} for depth,g in long.groupby(DEPTH)}
    return {'status':'source_based_counterfactual_accounting_not_observed_disturbance_or_seasonal_seed_bank_transition','paper_doi':'10.1371/journal.pone.0215157','source_archive_sha256':ARCHIVE,'member_sha256':{k:sha(v) for k,v in src.items()},'source_pots':100,'sorted_pots':30,'nominal_sorted_seeds':450,'seed_mass_ratio_separate_sample':ratio,'sorted':out,'unsorted_24wk_descriptive_only':longsum,'unsorted_nonmonotone_pots':bad,'limits':['For sorted cohorts E_final is observed terminal emergence count, E_day the earlier recorded cumulative-looking count. Scenario R=E_final-h*E_day+q*V, h imposed fractional loss of early emerged seedlings, q hypothetical future conversion of terminal viable seeds to recruited seedlings, assumes later emergence and bank unchanged by disturbance. This is a potential count accounting, not observed survival, actual establishment or fitted forecast. q common across size classes and assumes all surviving early and later emergents contribute equally, no density feedback or mortality after final observation.','No measured disturbance or future q, no seasonal transfer or repeated disturbance dynamics. A threshold outside [0,1] means no feasible interior crossover under these assumptions. Same initial seed-mass budget additionally assumes linear scaling and separate mean mass sample.','Nominal 15 seeds per pot, some fate sums differ from 15; no repair or denominator substitution. Four-cm sorted cell totals both exactly 75. Paired tank leave-one-out is sensitivity, not confidence interval.','Unsorted long cohort is distinct from sorted cohorts and 8-week harvest. Two nonmonotone histories; descriptive recorded counts only, not individual survival or cumulative incidence reconstruction. No linking separate harvests into trajectories.']}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('archive',type=Path);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.write_text(json.dumps(analyze(a.archive),indent=2,sort_keys=True,allow_nan=False)+'\n')
