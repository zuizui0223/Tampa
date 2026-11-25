#!/usr/bin/env python3
"""Published summary audit, not raw cohorts or a causal effect. Rollon 2003 Tables 1,3,5."""
import json,csv,statistics as st
from pathlib import Path
O=Path(__file__).resolve().parent
DATA=[('1a',.35,1.52,.93,2.06,1.88,6.85,2.25,1.92,3.78,10.64),('1c',3.,0.,0.,.16,0.,.27,0.,0.,0.,.27),('4',1.2,3.54,1.22,2.29,.06,8.13,3.68,.52,4.02,12.15),('5',.58,1.22,.05,.92,.10,2.31,2.30,.82,3.03,5.35),('6',.70,.75,.06,.62,.25,1.60,.76,.32,1.15,2.74)]
rows=[]
for site,depth,f1,f2,f3,f4,ft,m1,m2,mt,tt in DATA:
    rows.append(dict(site=site,depth_datum_m=depth,female_emerging_pct=f1,female_ready_pct=f2,female_rotting_pct=f3,fruit_pct=f4,female_total_reported_pct=ft,male_bud_full_pct=m1,male_spathe_empty_pct=m2,male_total_reported_pct=mt,total_reproductive_reported_pct=tt,female_nonfruit_stage_sum_pct=f1+f2+f3,fruit_over_female_total_stock=f4/ft,fruit_over_female_ready_stock=f4/f2 if f2 else None))
r={v['site']:v for v in rows};a,b=r['1a'],r['4']
def ratio_round(n,d):
    return [max(0,n-.005)/(d+.005),(n+.005)/(d-.005)] if d>.005 else None
ratio_keys=['female_ready_pct','male_bud_full_pct','male_total_reported_pct','fruit_pct','total_reproductive_reported_pct']
compar={k:dict(ratio_site4_over_site1a=b[k]/a[k],rounding_only_range=ratio_round(b[k],a[k])) for k in ratio_keys}
compar['female_nonfruit_stage_sum_pct']={'ratio_site4_over_site1a':b['female_nonfruit_stage_sum_pct']/a['female_nonfruit_stage_sum_pct']}
compar['fruit_over_female_ready_stock']={'ratio_site4_over_site1a':b['fruit_over_female_ready_stock']/a['fruit_over_female_ready_stock'],'rounding_only_range':[(.055*.925)/(1.225*1.885),(.065*.935)/(1.215*1.875)]}
assert compar['female_ready_pct']['rounding_only_range'][0]>1 and compar['fruit_pct']['rounding_only_range'][1]<.04
scar=[]
for site,s,t,shoots,buds in [('1a',3.55,1.1,9,14),('1c',4.5,.1,12,19),('5',3.92,.7,22,47),('6',3.72,None,21,37)]:
    scar.append(dict(site=site,annual_scar_frequency=s,tagged_annual_flowering_frequency=t,scar_over_tagged_rate=s/t if t else None,harvested_standing_shoots=shoots,young_developed_flower_structures=buds,all_young_structures_show_disintegration=(site=='1c')))
pollen=[dict(hours=h,reported_pct=x,mean_pct=st.mean(x),relative_fresh=st.mean(x)/82.5) for h,x in [(0,[90,75]),(13,[50,60]),(18,[20,40]),(24,[1,0])]]
iri=[('initial',1.),('3d',.512),('60d',.098),('dehiscence',.093)]
trans=[dict(start=k,end=j,initial_loss=v-w,conditional_retention=w/v,share_non_dehiscent=(v-w)/.907) for (k,v),(j,w) in zip(iri,iri[1:])]
assert abs(sum(x['initial_loss'] for x in trans)-.907)<1e-12
out={'status':'executed published summary arithmetic only','source':'10.1016/S0304-3770(03)00070-6','source_url':'https://www.vliz.be/imisdocs/publications/57415.pdf','sites':rows,'contrast_4_vs_1a':compar,'scar_audit':scar,'deep_vs_shallow_scar_ratio':4.5/3.55,'deep_vs_shallow_tagged_flowering_ratio':.1/1.1,'deep_vs_shallow_relative_proxy_discrepancy':(4.5/.1)/(3.55/1.1),'pollen_age_previous':pollen,'iriomote_previous':{'doi':'10.18960/hozen.1803','transitions':trans,'dehiscence_among_3d_remaining':.093/.512},'limits':['Published site mean standing stocks, not paired flower fates. Ratios of stocks are not fruit-set rates, and reported total means do not exactly sum across stage rows.','Rounding-only ranges are not confidence intervals. No inference from five sites or reused mean SEs.','Tagged flowering and scar reconstruction use different sampled shoots and periods; ratio is proxy mismatch, not abortion probability.','No marine animal intervention in Rollon or Iriomote. Pollen age chapter n=2 reported flower percentages per age, not transport timing.']}
for name,items in [('bolinao_sites.csv',rows),('scar_vs_tagged.csv',scar)]:
    with (O/name).open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(items[0]));w.writeheader();w.writerows(items)
(O/'results.json').write_text(json.dumps(out,indent=2,ensure_ascii=False,allow_nan=False)+'\n')
