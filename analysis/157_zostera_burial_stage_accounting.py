#!/usr/bin/env python3
"""Post-hoc pot-level fate accounting, Jorgensen et al. 2019.
DOI 10.1371/journal.pone.0215157; separate destructive harvest cohorts.
Not individual seed trajectories, future recruitment, or a new causal fit.
"""
import argparse, hashlib, io, json, statistics as st, zipfile
from collections import defaultdict
from pathlib import Path
import openpyxl
HASHES={'s002.xlsx':'f357afbefd89a554e38952829d17cb94f05a7b55276fed06dd3b315784a4b57f','s003.xlsx':'a5f47a9c0daf1106f071cb5f2e3a37abc8f873aa1ab403e91b0c13dc71170f83','s004.xlsx':'2e13b7a28ad1b242fc24a6cd158f8354a15974506f902fae4980f7bf0609bfaf'}
FATES=('failed','dead','viable','emerged')
DEPTHS=(.1,1,2,3,4,6,8)
def read(root,file):
    raw=(root/file).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=HASHES[file]:raise ValueError('source drift '+file)
    w=openpyxl.load_workbook(io.BytesIO(raw),data_only=True,read_only=True)
    rows=list(w.active.values);w.close();return rows

def sums(rows):
    n=len(rows);total=sum(r['total'] for r in rows);d={k:sum(r[k] for r in rows) for k in FATES}
    d['emerged_plus_viable']=d['emerged']+d['viable']
    return {'pots':n,'planned_seeds':15*n,'reported_total':total,'counts':d,
      'counts_per_planted':{k:v/(15*n) for k,v in d.items()},
      'pooled_counts_per_reported_total':{k:v/total for k,v in d.items()}}

def contrast(a,b):
    # a and b each one pot per tank, b minus a. Same tank is block, not same pot.
    assert set(a)==set(b)==set(range(1,6))
    d={str(t):{k:b[t][k]-a[t][k] for k in (*FATES,'total','emerged_plus_viable')} for t in sorted(a)}
    return {'tank_differences':d,'summed_differences':{k:sum(x[k] for x in d.values()) for k in next(iter(d.values()))},
            'positive_tanks':{k:sum(x[k]>0 for x in d.values()) for k in next(iter(d.values()))}}

def analyze(root):
    er,fr,br=[read(root,k) for k in HASHES]
    assert er[0][:6]==('Seed size grouping','Seed burial depth (cm)','Mesocosm ID','Pot ID','Time (days)','Seedling emergence')
    assert fr[0]==('Mesocosm ID','Pot ID','Seed size grouping','Seed burial depth (cm)','Time (weeks)','Unsuccessfully emerged seeds','Dead seeds','Viable seeds','Total seedling emergence','Total number of seeds')
    assert br[0]==('Mesocosm ID','Pot ID','Plant ID','Seed size grouping','Seed burial depth (cm)','Time (weeks)','Aboveground_biomass (g DW)','Belowground_biomass (g DW)','Cotyledon length (cm)')
    fate={};groups=defaultdict(dict)
    for tank,pot,size,depth,week,f,d,v,e,total in fr[1:]:
        key=(tank,pot);assert key not in fate and all(isinstance(x,int) and x>=0 for x in (f,d,v,e,total)) and f+d+v+e==total and total>0
        r=dict(tank=tank,pot=pot,size=size,depth=depth,week=week,failed=f,dead=d,viable=v,emerged=e,total=total,emerged_plus_viable=e+v)
        fate[key]=r;assert tank not in groups[size,week,depth];groups[size,week,depth][tank]=r
    expected={(s,10,d) for s in ('small','large') for d in (2,4,6)}|{('unsorted',w,d) for w in (8,24) for d in DEPTHS}
    assert len(fate)==100 and set(groups)==expected and all(set(g)==set(range(1,6)) for g in groups.values())
    ts=defaultdict(dict);blank=0
    for row in er[1:]:
        if all(x is None for x in row[:6]):blank+=1;continue
        size,depth,tank,pot,day,e=row[:6];key=(tank,pot);r=fate[key]
        assert (size,depth)==(r['size'],r['depth']) and day not in ts[key] and 0<=e<=15
        ts[key][day]=e
    assert set(ts)==set(fate) and sum(map(len,ts.values()))==1070
    declining=[]
    for key,t in ts.items():
        seq=[t[d] for d in sorted(t)];assert seq[-1]==fate[key]['emerged']
        if any(a>b for a,b in zip(seq,seq[1:])):declining.append(key)
    biomass=defaultdict(list);ids=set();metadata_conflicts=[]
    for tank,pot,plant,size,depth,week,ag,bg,cot in br[1:]:
        key=(tank,pot);r=fate[key];assert (*key,plant) not in ids;ids.add((*key,plant))
        if (size,depth,week)!=(r['size'],r['depth'],r['week']):metadata_conflicts.append([tank,pot,plant]);continue
        assert all(v is None or v>=0 for v in (ag,bg))
        biomass[key].append(None if ag is None or bg is None else ag+bg)
    assert len(ids)==486 and metadata_conflicts==[[4,48,2]]
    # Only complete paired pot comparisons whose number of biomass rows equals the recorded emerged count.
    # This is a post-outcome diagnostic, not an intention-to-treat biomass estimate.
    def adequate(r):
        vals=biomass[r['tank'],r['pot']];return len(vals)==r['emerged'] and all(v is not None for v in vals)
    mass={};size={}
    for d in (2,4,6):
        a,b=groups['small',10,d],groups['large',10,d];size[str(d)]=contrast(a,b)
        valid=[t for t in range(1,6) if adequate(a[t]) and adequate(b[t])]
        x=[sum(biomass[t,b[t]['pot']])-sum(biomass[t,a[t]['pot']]) for t in valid]
        mass[str(d)]={'included_tanks':valid,'large_minus_small_recovered_complete_biomass_g':x,'mean_difference_g_per_planted_seed':st.mean(x)/15}
    pooled={s:{t:{k:sum(groups[s,10,d][t][k] for d in (2,4,6)) for k in (*FATES,'total','emerged_plus_viable')} for t in range(1,6)} for s in ('small','large')}
    return {'status':'posthoc_original_pot_level_fate_accounting','source_hashes':HASHES,
      'audit':{'pots':100,'planted':1500,'reported_total':sum(r['total'] for r in fate.values()),'pots_below_15':sum(r['total']<15 for r in fate.values()),'pots_above_15':sum(r['total']>15 for r in fate.values()),'final_emergence_matches':100,'nonmonotone_time_series_pots':sorted(declining),'blank_emergence_rows':blank,'biomass_rows':len(ids),'biomass_metadata_conflicts':metadata_conflicts,'biomass_row_count_mismatch_pots_after_metadata_gate':sum(len(biomass[k])!=r['emerged'] for k,r in fate.items())},
      'groups':{f'{s}|{w}|{d:g}':sums(list(g.values())) for (s,w,d),g in groups.items()},
      'large_minus_small_by_depth':size,'large_minus_small_pooled_within_tank':contrast(pooled['small'],pooled['large']),
      'unsorted_8cm_minus_1cm_by_harvest':{str(w):contrast(groups['unsorted',w,1],groups['unsorted',w,8]) for w in (8,24)},'biomass_complete_pair_sensitivity':mass,
      'limits':['Reported fate counts sum to reported total, but reported total is not necessarily the 15 planted; never assign missing/excess records to a fate. Counts per planted are descriptive not a closed probability vector.', 'Emerged is cumulative recorded emergence, not survival at harvest; two time series decrease. Emerged plus viable is an arithmetic union of reported categories, not total living individuals or expected future recruits.', '8 and 24 week pots are separate destructive cohorts; differences are not individual transitions. Compare 1 vs 8 cm post hoc, since 0.1cm 24wk has unusually low recorded totals. Five tank blocks only; no new significance tests.', 'Biomass complete-pair sensitivity excludes missing/mismatched rows and pots; not an unbiased treatment estimate, no imputation or individual seed weight matching.', 'No genetic or animal disturbance measurements; 2019 effect already published.']}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path('seed_burial_source'));a=p.parse_args();print(json.dumps(analyze(a.root),indent=2,sort_keys=True,allow_nan=False))
