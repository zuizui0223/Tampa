#!/usr/bin/env python3
"""Mizutani et al 2019 Table 2 counts, visually verified original PDF p183.
Cohort-level arithmetic; no raw plot records or causal mediation."""
from pathlib import Path
import json,csv,itertools
P=Path(__file__).resolve().parent
ARCHIVE='c681e07eb99683de959e71a21151f5ff3aef8ac747a49146561b37c5f5ac880c'
PDF='560d13be5a57fafeae1bbd5ad09b7bc7bf4c65df3751f08fe9579b9fe2758c8f'
DATA=[(2014,'06/13','Jun',12,23,15,11,11,0),(2014,'07/12–13','Jul',24,32,6,6,6,0),(2014,'08/10','Aug',13,30,14,4,4,0),(2014,'09/08','Sep',8,21,18,2,2,0),(2014,'10/07–09','Oct–Nov',8,17,0,0,0,0),(2015,'06/02','Jun',15,37,25,11,10,2),(2015,'07/02','Jul',75,148,113,7,7,3),(2015,'07/30–31','Jul',269,204,111,26,24,3),(2015,'08/29','Aug',72,118,77,10,9,1),(2015,'09/26–27','Sep',55,91,29,1,0,1),(2015,'10/27','Oct–Nov',23,56,0,0,0,0),(2015,'11/26','Oct–Nov',5,17,0,0,0,0)]
KEY=['year','date','month','male','female','day3','day60','dehiscent','typhoons']
rows=[dict(zip(KEY,r)) for r in DATA]
assert all(r['female']>=r['day3']>=r['day60']>=r['dehiscent'] for r in rows)
def summ(rr):
 n={k:sum(r[k] for r in rr) for k in KEY[3:-1]};f=n['female'];a=n['day3'];b=n['day60'];c=n['dehiscent'];return n|dict(early=a/f,day60_fraction=b/f,final=c/f,post_day3=c/a if a else None,post_day60=c/b if b else None,late_to_day60=b/a if a else None)
ys=[2014,2015];ms=['Jun','Jul','Aug','Sep','Oct–Nov'];annual={str(y):summ([r for r in rows if r['year']==y]) for y in ys};all_=summ(rows);assert [all_[k] for k in KEY[3:-1]]==[579,794,408,78,73]
monthly={m:summ([r for r in rows if r['month']==m]) for m in ms};by_y_m={str(y):{m:summ([r for r in rows if r['year']==y and r['month']==m]) for m in ms} for y in ys}
factors=[]
for y in ys:
 d=by_y_m[str(y)];factors.append([[d[m]['female']/annual[str(y)]['female'] for m in ms],[d[m]['early'] for m in ms],[d[m]['post_day3'] if d[m]['post_day3'] is not None else 0 for m in ms]])
assert factors[0][1][-1]==factors[1][1][-1]==0
names=['seasonal_composition','day3_retention','post_day3_dehiscence']
def value(flags):
 w,q,r=[factors[flags[i]][i] for i in range(3)];return sum(a*b*c for a,b,c in zip(w,q,r))
parts=dict.fromkeys(names,0.)
for order in itertools.permutations(range(3)):
 flags=[0,0,0];v=value(flags)
 for i in order:
  flags[i]=1;u=value(flags);parts[names[i]]+=(u-v)/6;v=u
assert abs(value([0,0,0])-annual['2014']['final'])<1e-12 and abs(value([1,1,1])-annual['2015']['final'])<1e-12
assert abs(sum(parts.values())-(annual['2015']['final']-annual['2014']['final']))<1e-12
result=dict(status='published Table 2 transcription verified against image; descriptive counts only',doi='10.18960/hozen.1803',archive_sha256=ARCHIVE,pdf_sha256=PDF,year=annual,all=all_,month=monthly,year_month=by_y_m,shapley_accounting=parts,rate_difference=annual['2015']['final']-annual['2014']['final'],mixed_2015_weights_2014_stages=value([1,0,0]),mixed_2014_weights_2015_stages=value([0,1,1]),losses=[all_['female']-all_['day3'],all_['day3']-all_['day60'],all_['day60']-all_['dehiscent']],count_vs_reported_pct={'day3':[100*408/794,51.2],'day60':[100*78/794,9.8],'dehiscence':[100*73/794,9.3]},limits=['12 tidal flowering cohorts pooled over three quadrats/year; two years, not independent 794 plants for year effects.','Day3 retention proxy not confirmed fertilization. Stage identity not causal, month group composition includes different dates.','Shapley arithmetic only; autumn conditional post-day3 rate undefined, irrelevant because early retention zero in both years.','No raw quadrat-level counts or observed animal effect; typhoon number and years confounded, not a fitted causal contrast.'])
for name,records in [('iriomote_cohorts.csv',rows),('iriomote_months.csv',[dict(month=k,**v) for k,v in monthly.items()]),('iriomote_year_month.csv',[dict(year=y,month=m,**d) for y,v in by_y_m.items() for m,d in v.items()])]:
 with (P/name).open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
(P/'results.json').write_text(json.dumps(result,indent=2,ensure_ascii=False,allow_nan=False)+'\n')
print(json.dumps(result,indent=2,ensure_ascii=False))
