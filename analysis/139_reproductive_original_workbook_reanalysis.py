#!/usr/bin/env python3
"""Compact reproduction of main original-workbook results; exploratory."""
import argparse,hashlib,io,itertools,json,zipfile
from collections import defaultdict
from pathlib import Path
import numpy as np
from openpyxl import load_workbook
p=argparse.ArgumentParser()
p.add_argument("artifact",type=Path)
a=p.parse_args()
h="144aa9cbadf811e307f8c024180152e640f4a55c8f4fb19474382c69eef0ba6c"
assert hashlib.sha256(a.artifact.read_bytes()).hexdigest()==h
z=zipfile.ZipFile(a.artifact)
manifest=json.loads(z.read("manifest.json"))
def rows(name):
    b=z.read(name)
    m=next(s for s in manifest["sources"] if s.get("file")==name)
    assert hashlib.sha256(b).hexdigest()==m["sha256"]
    return list(load_workbook(io.BytesIO(b),data_only=True).active.values)
rng=np.random.default_rng(20261124)
def boot(x,y):
    return np.quantile(rng.choice(x,(20000,len(x)),replace=True).mean(1)-rng.choice(y,(20000,len(y)),replace=True).mean(1),[.025,.975]).tolist()
r=rows("infantes_burial.xlsx")
g=defaultdict(list)
errors=[]
for sp,s,e,i,j,k in [("Carcinus",3,37,7,8,9),("Pagurus",41,70,2,3,4),("Strongylocentrotus",73,102,3,4,5)]:
    for idx in range(s,e+1):
        a=r[idx-1]
        assert a[i]==10 and 0<=a[j]<=10 and a[1] in (0,1,2)
        loss=1-a[j]/a[i]
        g[sp,a[1]].append(loss)
        if not np.isclose(loss*100,a[k]): errors.append(idx)
assert sum(map(len,g.values()))==95 and errors==[57]
out={"burial":{},"percent_mismatch":errors}
for (sp,d),v in g.items():
    a=np.array(v)
    out["burial"][f"{sp}_{d}"]=dict(n=len(a),mean=float(a.mean()),any_loss=int(sum(a>0)),conditional_mean=float(a[a>0].mean()) if any(a>0) else None)
x,y,w=[np.array(g["Carcinus",d]) for d in (0,1,2)]
p0,p1=np.mean(x>0),np.mean(y>0);m0,m1=x[x>0].mean(),y[y>0].mean()
out["carcinus"]={"0_minus_1":float(x.mean()-y.mean()),"ci01":boot(x,y),"0_minus_2":float(x.mean()-w.mean()),"ci02":boot(x,w),"incidence_component":float((p0-p1)*(m0+m1)/2),"conditional_component":float((m0-m1)*(p0+p1)/2),"zero_any_upper95":1-.05**.1}
r=rows("infantes_one_week.xlsx")
g=defaultdict(list);by=defaultdict(list);ids=[]
for a in r[3:]:
    tr,lab,_,t,k,m=a[:6]
    assert 0<=k<=200 and 0<=m<=20
    ids.append((tr,lab));g[t].append([k/200,m/20]);by[t,tr].append(k/200)
assert len(ids)==30 and len(set(ids))==29
out["week"]={t:np.mean(v,0).tolist() for t,v in g.items()}
out["week_blocked"]={}
for t,ref in [("CAGE-SAND","CAGE-HAND"),("CAGE","CAGE-HAND"),("CAGE","CAGE-SAND")]:
    a=[np.asarray(by[t,j]) for j in (2,3)];b=[np.asarray(by[ref,j]) for j in (2,3)]
    assert all(len(x)==3 for x in a+b)
    diff=[float(x.mean()-y.mean()) for x,y in zip(a,b)]
    draws=np.mean([rng.choice(x,(20000,len(x)),replace=True).mean(1)-rng.choice(y,(20000,len(y)),replace=True).mean(1) for x,y in zip(a,b)],0)
    out["week_blocked"][t+"__"+ref]={"trial_differences":diff,"mean":float(np.mean(diff)),"ci":np.quantile(draws,[.025,.975]).tolist()}
g=defaultdict(list)
for a in rows("infantes_one_month.xlsx")[4:]:
    _,t,n,k,_,_,_,nm,km=a[:9];assert n==200 and nm==20
    g[t].append([k/n,km/nm])
out["month"]={t:np.mean(v,0).tolist() for t,v in g.items()}
g=defaultdict(list)
for a in rows("infantes_eight_month.xlsx")[4:]:
    _,t,k,percent=a[:4];assert np.isclose(k,percent);g[t].append(k)
x,y=np.array(g["Close cage"]),np.array(g["Open cage"]);u=np.r_[x,y]
obs=abs(x.mean()-y.mean())
diff=[]
for c in itertools.combinations(range(len(u)),len(x)):
    mask=np.zeros(len(u),bool);mask[list(c)]=True
    diff.append(abs(u[mask].mean()-u[~mask].mean()))
out["eight"]={"counts":dict(g),"ratio":float(x.mean()/y.mean()),"difference":float(x.mean()-y.mean()),"exact_p":float(np.mean(np.array(diff)>=obs-1e-10)),"ci":boot(x,y),"denominator_conflict":True}
g=defaultdict(dict);errors=[]
for a in rows("meysick_seed_trapping.xlsx")[2:]:
    i,_,_,_,v,_,k,n,*loc=a;assert n==30 and v not in g[i] and 0<=k<=n
    g[i][v]=k/n
    if sum(x or 0 for x in loc)!=k:errors.append((i,v))
assert len(g)==16 and all(set(v)==set(range(12,31,2)) for v in g.values()) and len(errors)==8
out["flume"]={i:{"mean":float(np.mean(list(v.values()))),"min":min(v.values())} for i,v in g.items()}
out["flume_mixes"]={}
for i,cs in [(12,[2,5]),(13,[2,9]),(14,[2,11]),(15,[6,11]),(16,[2,9,11])]:
    v=sorted(g[i]);m=np.array([g[i][j] for j in v]);c=np.array([[g[k][j] for j in v] for k in cs]);best=c.max(0);union=1-np.prod(1-c,0)
    out["flume_mixes"][i]=dict(mean_gain=float(np.mean(m-best)),above_best=int(sum(m>best)),union_residual=float(np.mean(m-union)),minimum=float(m.min()),best_component_minimum=float(max(row.min() for row in c)))
out["flume_location_mismatch"]=errors
print(json.dumps(out,indent=2))
