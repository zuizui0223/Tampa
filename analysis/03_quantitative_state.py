#!/usr/bin/env python3
"""Quantitative-state audit for Tampa Bay Thalassia testudinum.

Pinned Darwin Core Event/Occurrence/eMoF are joined at point -> transect-visit ->
transect-year scales. Primary ecological state variables are:
  1) point frequency of Thalassia within each transect visit;
  2) mean Braun-Blanquet cover class across all sampled points (0 at points without
     a focal occurrence; nonnumeric 'Reported' cover remains missing at present points).
Blade length and shoot density are secondary because their measurement availability varies.
"""
from __future__ import annotations
import argparse, csv, hashlib, io, json, math
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from urllib.request import Request, urlopen
import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu

COMMIT='6c567beff95ea04f0e397101befb49d5233ace8f'
BASE=f'https://raw.githubusercontent.com/tbep-tech/obis-example/{COMMIT}/dwc'
FILES={
 'event': {'url':f'{BASE}/event.csv','size':24654717,'blob':'583b4d4e328290ab065346579eb4f29f03ea0f99'},
 'occurrence': {'url':f'{BASE}/occurrence.csv','size':12508487,'blob':'d34aeb5aedb72459d1e04059629cb09450df929e'},
 'emof': {'url':f'{BASE}/emof.csv','size':16449353,'blob':'e463046726080334637824555309fd89c7c447da'},
}
FOCAL='Thalassia testudinum'
EVENT_HEADER=['eventID','parentEventID','eventType','eventDate','year','month','day','decimalLatitude','decimalLongitude','geodeticDatum','minimumDepthInMeters','maximumDepthInMeters','country','countryCode','stateProvince','waterBody','locality','locationID','samplingProtocol','institutionCode','datasetName','datasetID','license','locationRemarks']
OCC_HEADER=['occurrenceID','eventID','basisOfRecord','occurrenceStatus','scientificName','scientificNameID','taxonRank','kingdom','phylum','class','order','family','genus','collectionCode','recordedBy','identificationRemarks']
EMOF_HEADER=['eventID','occurrenceID','measurementType','measurementTypeID','measurementValue','measurementUnit','measurementUnitID','measurementRemarks']
MEASURE={
 'cover':'seagrass percent cover (Braun-Blanquet scale)',
 'blade_length':'seagrass blade length arithmetic mean',
 'shoot_density':'seagrass shoot density arithmetic mean',
 'epiphyte':'epiphyte density (qualitative)',
 'sediment':'sediment type',
}
PULSE_NODES={'TBEP:seagrass:loc:S1T1','TBEP:seagrass:loc:S3T12','TBEP:seagrass:loc:S3T3','TBEP:seagrass:loc:S3T4','TBEP:seagrass:loc:S3T5'}

def git_blob_sha1(data:bytes)->str:
    return hashlib.sha1(f'blob {len(data)}\0'.encode()+data).hexdigest()

def fetch(spec):
    req=Request(spec['url'],headers={'Accept-Encoding':'identity','User-Agent':'Tampa-quant-state/1.0'})
    with urlopen(req,timeout=180) as resp: data=resp.read(spec['size']+1)
    if len(data)!=spec['size']: raise RuntimeError(f"size drift {spec['url']} {len(data)}")
    if git_blob_sha1(data)!=spec['blob']: raise RuntimeError(f"blob drift {spec['url']}")
    return data

def parse_event(data:bytes):
    reader=csv.DictReader(io.StringIO(data.decode('utf-8'),newline=''))
    if reader.fieldnames!=EVENT_HEADER: raise RuntimeError('event header drift')
    parents={}; child_to_parent={}; parent_children=defaultdict(list)
    for n,row in enumerate(reader,start=2):
        eid=row['eventID'].strip(); typ=row['eventType'].strip()
        if typ=='Transect':
            dt=datetime.strptime(row['eventDate'],'%Y-%m-%d').date()
            parents[eid]={'unit_id':eid,'node_id':row['locationID'].strip(),'year':dt.year,'date':dt.isoformat(),
                          'water_body':row['waterBody'].strip(),'longitude':float(row['decimalLongitude']),'latitude':float(row['decimalLatitude'])}
        elif typ=='Point':
            pid=row['parentEventID'].strip(); child_to_parent[eid]=pid; parent_children[pid].append(eid)
        else: raise RuntimeError(f'unsupported event type {typ} row {n}')
    candidates={pid:p for pid,p in parents.items() if len(parent_children.get(pid,[]))>=3}
    valid_children={c for p in candidates for c in parent_children[p]}
    child_to_parent={c:p for c,p in child_to_parent.items() if c in valid_children and p in candidates}
    return candidates,parent_children,child_to_parent

def parse_occ(data:bytes,child_to_parent):
    reader=csv.DictReader(io.StringIO(data.decode('utf-8'),newline=''))
    if reader.fieldnames!=OCC_HEADER: raise RuntimeError('occurrence header drift')
    occ={}; focal_by_child=defaultdict(list)
    for n,row in enumerate(reader,start=2):
        oid=row['occurrenceID']; eid=row['eventID']
        if eid not in child_to_parent: continue
        sci=row['scientificName']; status=row['occurrenceStatus']
        occ[oid]={'event_id':eid,'scientific_name':sci,'status':status}
        if sci==FOCAL:
            if status!='present': raise RuntimeError(f'focal non-present row {n}')
            focal_by_child[eid].append(oid)
    return occ,focal_by_child

def maybe_float(x):
    try:
        y=float(str(x).strip())
    except Exception: return math.nan
    return y if math.isfinite(y) else math.nan

def parse_emof(data:bytes,occ):
    reader=csv.DictReader(io.StringIO(data.decode('utf-8'),newline=''))
    if reader.fieldnames!=EMOF_HEADER: raise RuntimeError('emof header drift')
    values=defaultdict(lambda:defaultdict(list)); type_counts=defaultdict(int); unit_counts=defaultdict(lambda:defaultdict(int)); nonnumeric_cover=0
    for row in reader:
        oid=row['occurrenceID']
        info=occ.get(oid)
        if info is None or info['scientific_name']!=FOCAL: continue
        typ=row['measurementType']; val=row['measurementValue']; unit=row['measurementUnit']
        type_counts[typ]+=1; unit_counts[typ][unit]+=1
        if typ==MEASURE['cover']:
            x=maybe_float(val)
            if math.isfinite(x): values[oid]['cover'].append(x)
            else: nonnumeric_cover+=1
        elif typ==MEASURE['blade_length']:
            x=maybe_float(val)
            if math.isfinite(x): values[oid]['blade_length'].append(x)
        elif typ==MEASURE['shoot_density']:
            x=maybe_float(val)
            if math.isfinite(x): values[oid]['shoot_density'].append(x)
        elif typ==MEASURE['epiphyte']:
            values[oid]['epiphyte'].append(val)
        elif typ==MEASURE['sediment']:
            values[oid]['sediment'].append(val)
    return values,type_counts,unit_counts,nonnumeric_cover

def visit_panel(candidates,parent_children,child_to_parent,focal_by_child,meas):
    rows=[]
    for pid,p in sorted(candidates.items()):
        children=parent_children[pid]
        focal_children=[c for c in children if focal_by_child.get(c)]
        n=len(children); nf=len(focal_children)
        cover_all=[]; cover_present=[]; blade=[]; shoot=[]
        for c in children:
            oids=focal_by_child.get(c,[])
            if not oids:
                cover_all.append(0.0)
                continue
            local_cover=[]
            for oid in oids:
                local_cover.extend(meas[oid].get('cover',[])); blade.extend(meas[oid].get('blade_length',[])); shoot.extend(meas[oid].get('shoot_density',[]))
            if local_cover:
                cv=float(np.mean(local_cover)); cover_present.append(cv); cover_all.append(cv)
            else:
                cover_all.append(np.nan)
        rows.append({**p,'child_point_count':n,'focal_point_count':nf,'focal_frequency':nf/n,
                     'bb_cover_mean_all_points':float(np.nanmean(cover_all)) if np.isfinite(cover_all).any() else np.nan,
                     'bb_cover_mean_present_points':float(np.mean(cover_present)) if cover_present else np.nan,
                     'blade_length_mean_mm':float(np.mean(blade)) if blade else np.nan,
                     'shoot_density_mean_m2':float(np.mean(shoot)) if shoot else np.nan,
                     'blade_measurements':len(blade),'shoot_measurements':len(shoot)})
    return pd.DataFrame(rows)

def annualize(v):
    return (v.groupby(['node_id','year'],as_index=False)
            .agg(water_body=('water_body','first'),longitude=('longitude','first'),latitude=('latitude','first'),visits=('unit_id','size'),
                 detected=('focal_point_count',lambda x:int((x>0).any())),
                 focal_frequency=('focal_frequency','mean'),bb_cover_mean_all_points=('bb_cover_mean_all_points','mean'),
                 bb_cover_mean_present_points=('bb_cover_mean_present_points','mean'),blade_length_mean_mm=('blade_length_mean_mm','mean'),
                 shoot_density_mean_m2=('shoot_density_mean_m2','mean'),blade_measurements=('blade_measurements','sum'),shoot_measurements=('shoot_measurements','sum')))

def segment_year(a):
    return (a.groupby(['water_body','year'],as_index=False)
            .agg(n_nodes=('node_id','size'),prevalence=('detected','mean'),frequency_mean=('focal_frequency','mean'),frequency_median=('focal_frequency','median'),
                 cover_index_mean=('bb_cover_mean_all_points','mean'),cover_index_median=('bb_cover_mean_all_points','median'),
                 blade_length_mean_mm=('blade_length_mean_mm','mean'),shoot_density_mean_m2=('shoot_density_mean_m2','mean'),
                 blade_n=('blade_measurements','sum'),shoot_n=('shoot_measurements','sum')))

def slope(df,col,start,end):
    x=df[(df.year>=start)&(df.year<=end)][['year',col]].dropna()
    if len(x)<4: return {'n':len(x),'slope':None}
    b=np.polyfit(x.year.to_numpy(float),x[col].to_numpy(float),1)[0]
    return {'n':len(x),'slope':float(b),'start_mean':float(x[x.year<=start+2][col].mean()),'end_mean':float(x[x.year>=end-2][col].mean())}

def main(out:Path):
    out.mkdir(parents=True,exist_ok=True)
    raw={k:fetch(v) for k,v in FILES.items()}
    candidates,parent_children,child_to_parent=parse_event(raw['event'])
    occ,focal_by_child=parse_occ(raw['occurrence'],child_to_parent)
    meas,type_counts,unit_counts,nonnumeric_cover=parse_emof(raw['emof'],occ)
    visit=visit_panel(candidates,parent_children,child_to_parent,focal_by_child,meas)
    annual=annualize(visit); seg=segment_year(annual)
    pulse=annual[annual.node_id.isin(PULSE_NODES)&annual.year.isin([2013,2014,2015,2016,2017,2018])].sort_values(['node_id','year'])
    base=annual[(annual.year==2015)&(annual.detected==1)&(annual.water_body.isin(['Old Tampa Bay','Middle Tampa Bay']))]
    x=base[base.node_id.isin(PULSE_NODES)].focal_frequency.dropna(); y=base[~base.node_id.isin(PULSE_NODES)].focal_frequency.dropna()
    mw=mannwhitneyu(x,y,alternative='two-sided') if len(x) and len(y) else None
    trend={}
    for wb in sorted(seg.water_body.unique()):
        d=seg[seg.water_body==wb]
        trend[wb]={}
        for col in ['prevalence','frequency_mean','cover_index_mean','blade_length_mean_mm','shoot_density_mean_m2']:
            trend[wb][col]={'1998_2015':slope(d,col,1998,2015),'2016_2025':slope(d,col,2016,2025)}
    summary={
      'source':{'commit':COMMIT,'verified':True,'files':{k:{'size':v['size'],'blob':v['blob']} for k,v in FILES.items()}},
      'registry':{'candidate_visits':int(len(visit)),'annual_node_years':int(len(annual)),'nodes':int(annual.node_id.nunique()),'years':[int(annual.year.min()),int(annual.year.max())]},
      'focal_measurement_type_counts':dict(sorted(type_counts.items())),
      'focal_measurement_units':{k:dict(v) for k,v in unit_counts.items()},
      'nonnumeric_focal_cover_rows':int(nonnumeric_cover),
      'quantitative_coverage':{
        'annual_frequency_nonmissing':int(annual.focal_frequency.notna().sum()),
        'annual_cover_index_nonmissing':int(annual.bb_cover_mean_all_points.notna().sum()),
        'annual_blade_nonmissing':int(annual.blade_length_mean_mm.notna().sum()),
        'annual_shoot_nonmissing':int(annual.shoot_density_mean_m2.notna().sum()),
      },
      'pulse_2015_prestate_test':{
        'pulse_nodes_n':int(len(x)),'other_detected_otb_mtb_nodes_n':int(len(y)),
        'pulse_frequency_median':float(x.median()) if len(x) else None,'other_frequency_median':float(y.median()) if len(y) else None,
        'mannwhitney_u':float(mw.statistic) if mw else None,'p_two_sided':float(mw.pvalue) if mw else None,
      },
      'segment_year_trends':trend,
      'claim_boundary':'Exploratory quantitative-state audit. Braun-Blanquet class is ordinal, not percent cover. Segment trends are descriptive and do not identify climate causality.'
    }
    visit.to_csv(out/'quant_visit_panel.csv',index=False)
    annual.to_csv(out/'quant_annual_panel.csv',index=False)
    seg.to_csv(out/'quant_segment_year.csv',index=False)
    pulse.to_csv(out/'quant_pulse_nodes.csv',index=False)
    (out/'quantitative_state_summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True))
    print(json.dumps(summary,indent=2,sort_keys=True))

if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--out',type=Path,default=Path('results/generated')); args=ap.parse_args(); main(args.out)
