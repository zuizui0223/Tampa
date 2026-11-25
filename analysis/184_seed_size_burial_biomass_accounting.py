#!/usr/bin/env python3
"""Observed seedling biomass accounting in sorted-seed burial experiment."""
import argparse, hashlib, io, json, zipfile, math
from pathlib import Path
import numpy as np
import pandas as pd
ARCHIVE='74f0c656295996b258907469cbbfd15a75df41744279d39a74947fbd74ad5374'
MEMBERS={'s001.xlsx':'6d4ac38364d5b523193c979196c49d31aa4a4c3965d7b70dbb7757ae8be391b8','s003.xlsx':'a5f47a9c0daf1106f071cb5f2e3a37abc8f873aa1ab403e91b0c13dc71170f83','s004.xlsx':'2e13b7a28ad1b242fc24a6cd158f8354a15974506f902fae4980f7bf0609bfaf'}
K=['Mesocosm ID','Pot ID','Seed size grouping','Seed burial depth (cm)','Time (weeks)']
SIZE=K[2];DEPTH=K[3]

def analyze(path):
    raw=path.read_bytes();assert hashlib.sha256(raw).hexdigest()==ARCHIVE
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        files={f:z.read(f) for f in MEMBERS}
    assert all(hashlib.sha256(v).hexdigest()==MEMBERS[k] for k,v in files.items())
    s=pd.read_excel(io.BytesIO(files['s001.xlsx']),sheet_name='Seed weight');assert s.Seed.value_counts().to_dict()=={'U':100,'L':29,'S':28}
    initial={k:dict(n=len(g),mean_mg=float(g.weight.mean()),sd_mg=float(g.weight.std())) for k,g in s.groupby('Seed')}
    size_ratio=initial['L']['mean_mg']/initial['S']['mean_mg']
    b=pd.read_excel(io.BytesIO(files['s003.xlsx']));c=pd.read_excel(io.BytesIO(files['s004.xlsx']));assert len(b)==100 and len(c)==486
    b=b[b[SIZE].isin(['large','small'])].copy();c=c[c[SIZE].isin(['large','small'])].copy();assert len(b)==30 and len(c)==168 and not b.duplicated(K).any() and not c.duplicated(K+['Plant ID']).any() and b['Time (weeks)'].eq(10).all()
    cols=['Aboveground_biomass (g DW)','Belowground_biomass (g DW)'];assert (c[cols].stack()>=0).all()
    c['mass']=c[cols].sum(axis=1,min_count=2)*1000
    c['available_mass']=c[cols].sum(axis=1,min_count=1)*1000
    g=c.groupby(K).agg(plant_rows=('Plant ID','size'),complete_mass_rows=('mass','count'),mass_mg=('mass','sum'),available_component_mass_mg=('available_mass','sum')).reset_index()
    j=b.merge(g,on=K,validate='one_to_one',how='outer',indicator=True);assert len(j)==30 and j._merge.eq('both').all()
    j['strict']=(j.plant_rows==j['Total seedling emergence'])&(j.plant_rows==j.complete_mass_rows)
    assert len(j[~j.strict])==5 and j.complete_mass_rows.sum()==166
    panels={}
    for depth,d in j.groupby(DEPTH):
        out={}
        for name,a in [('all_observed',d),('count_closed_complete_tank_pairs',d[d.groupby(K[0]).strict.transform('all')])]:
            t={}
            for group,u in a.groupby(SIZE):
                n=len(u);nplant=int(u.complete_mass_rows.sum());mass=float(u.mass_mg.sum());em=int(u['Total seedling emergence'].sum());assert n>0 and nplant>0
                t[group]=dict(pots=n,nominal_seeds=n*15,emerged=em,viable_unemerged=int(u['Viable seeds'].sum()),plant_rows=int(u.plant_rows.sum()),measured_plants=nplant,measured_mass_mg=mass,measured_mass_per_pot_mg=mass/n,measured_mass_per_nominal_seed_mg=mass/(n*15),mean_complete_plant_mass_mg=mass/nplant,available_component_mass_mg=float(u.available_component_mass_mg.sum()))
            L,S=t['large'],t['small'];assert L['pots']==S['pots'];count=L['measured_plants']/S['measured_plants'];individual=L['mean_complete_plant_mass_mg']/S['mean_complete_plant_mass_mg'];total=L['measured_mass_mg']/S['measured_mass_mg'];assert math.isclose(total,count*individual)
            w=a.pivot(index=K[0],columns=SIZE,values='mass_mg');diff=w.large-w.small
            out[name]=dict(groups=t,ratios=dict(emergence=L['emerged']/S['emerged'],complete_mass_count=count,complete_individual_mass=individual,measured_total_mass=total,hypothetical_equal_seed_dry_mass_budget=total/size_ratio,viable_unemerged=L['viable_unemerged']/S['viable_unemerged']),paired_tank_mass_differences_mg={str(int(i)):float(v) for i,v in diff.items()},positive_tank_pairs=int((diff>0).sum()),n_tank_pairs=len(w),leave_one_tank_out_mass_ratio=[float((w.large.sum()-w.large.iloc[i])/(w.small.sum()-w.small.iloc[i])) for i in range(len(w))])
        panels[str(depth)]=out
    return {'status':'original_data_observed_biomass_accounting_not_whole_seed_fate_or_reserve_measurement','paper_doi':'10.1371/journal.pone.0215157','archive_sha256':ARCHIVE,'members':MEMBERS,'initial_seed_size_sample':initial,'large_small_initial_mean_dry_mass_ratio':size_ratio,'sorted_pots':len(j),'nominal_seeds':450,'plant_records':len(c),'complete_mass_records':int(j.complete_mass_rows.sum()),'incomplete_pots':j.loc[~j.strict,K+['plant_rows','complete_mass_rows','Total seedling emergence']].to_dict('records'),'panels':panels,'limits':['Separate seed-size metric sample; not individual seed weight linked to seedling. Equal dry mass budget is a hypothetical scaling assuming proportional response and source sample means, not experimentally compared sowing densities, reserve use efficiency or maternal cost.','Measured sum includes only seedlings with both tissue masses recorded, not full biomass if missing. Keep missing components unfilled. Count-closed complete pairs selected on observed data; sensitivity, not independent confirmation.','Five tanks, one pot per size-depth combination per tank. No individual seedlings treated as independent experimental replicates, no hypothesis tests or generalized optimum.','Emergence count is cumulative, biomass at destructive harvest. Matching counts do not identify individual seed fate, and viable unemerged seeds are not established seedlings. No measured carbohydrate, maturation age or source-cohort link to 2025 data.']}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('archive',type=Path);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.write_text(json.dumps(analyze(a.archive),indent=2,sort_keys=True,allow_nan=False)+'\n')
