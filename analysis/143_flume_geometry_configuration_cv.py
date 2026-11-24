#!/usr/bin/env python3
"""Whole-configuration CV, single published flume experiment; response-open."""
import argparse,json,zipfile,hashlib,io
from pathlib import Path
import numpy as np,pandas as pd
from openpyxl import load_workbook
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from scipy.special import xlogy
def run(artifact,C):
    sha=hashlib.sha256(artifact.read_bytes()).hexdigest()
    assert sha=="144aa9cbadf811e307f8c024180152e640f4a55c8f4fb19474382c69eef0ba6c"
    with zipfile.ZipFile(artifact) as z:
        b=z.read("meysick_seed_trapping.xlsx");m=json.loads(z.read("manifest.json"))
        assert hashlib.sha256(b).hexdigest()==next(x["sha256"] for x in m["sources"] if x.get("file")=="meysick_seed_trapping.xlsx")
        rows=list(load_workbook(io.BytesIO(b),data_only=True).active.values)[2:]
    d=pd.DataFrame([dict(id=t,desc=desc,width=w,objects=n,flow=v,scour=s,k=k,n=nt) for t,desc,w,n,v,s,k,nt,*loc in rows])
    assert len(d)==160 and d.id.nunique()==16 and all(d.n==30) and not d.duplicated(["id","flow"]).any()
    d["w"]=np.log1p(d.width);d["o"]=np.log1p(d.objects);d["v"]=(d.flow-21)/9;d["v2"]=d.v**2
    d["wv"]=d.w*d.v;d["ov"]=d.o*d.v;d["wv2"]=d.w*d.v2
    for key,word in [("short","short"),("long","long"),("oyster","oyster"),("mussel","mytilus")]:
        d[key]=d.desc.str.contains(word,case=False).astype(int);d[key+"v"]=d[key]*d.v
    mods={"flow":["v","v2"],"width":["v","v2","w","wv","wv2"],"geometry":["v","v2","w","wv","wv2","o","ov"],"identity":["v","v2","short","long","oyster","mussel","shortv","longv","oysterv","musselv"],"geometry_identity":["v","v2","w","wv","wv2","o","ov","short","long","oyster","mussel","shortv","longv","oysterv","musselv"]}
    y=d.k/d.n
    pred={name:np.zeros(len(d)) for name in mods};pred["training_flow_mean"]=np.zeros(len(d))
    for t in sorted(d.id.unique()):
        tr=d.id!=t;te=~tr
        pred["training_flow_mean"][te]=(d.loc[tr].groupby("flow").k.sum()/d.loc[tr].groupby("flow").n.sum()).reindex(d.loc[te,"flow"]).values
        for name,cols in mods.items():
            s=StandardScaler().fit(d.loc[tr,cols]);X=s.transform(d.loc[tr,cols]);Xt=s.transform(d.loc[te,cols]);k=d.loc[tr,"k"].values;n=d.loc[tr,"n"].values
            model=LogisticRegression(C=C,max_iter=1000).fit(np.vstack([X,X]),np.r_[np.ones(len(X)),np.zeros(len(X))],sample_weight=np.r_[k/n,(n-k)/n])
            pred[name][te]=model.predict_proba(Xt)[:,1]
    base=np.sum((y-pred["training_flow_mean"])**2);out={}
    for name,p in pred.items():
        p=np.clip(p,1e-9,1-1e-9)
        out[name]={"rmse":float(np.sqrt(np.mean((y-p)**2))),"skill_vs_flow_mean":float(1-np.sum((y-p)**2)/base),"cross_entropy":float(-np.mean(xlogy(y,p)+xlogy(1-y,1-p)))}
    improved=int(sum(np.mean((y[d.id==t]-pred["geometry_identity"][d.id==t])**2)<np.mean((y[d.id==t]-pred["geometry"][d.id==t])**2) for t in d.id.unique()))
    return {"C":C,"models":mods,"results":out,"configurations_improved_by_identity":improved,"predictions":[{"treatment":int(r.id),"flow":int(r.flow),"observed":float(y[i]),**{k:float(v[i]) for k,v in pred.items()}} for i,r in d.iterrows()]}
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("artifact",type=Path);p.add_argument("--out",type=Path,required=True);a=p.parse_args()
    a.out.write_text(json.dumps([run(a.artifact,c) for c in [.1,.3,1,3,10]],indent=2)+"\n")
