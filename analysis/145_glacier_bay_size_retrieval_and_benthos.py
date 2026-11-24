#!/usr/bin/env python3
"""Response-open Glacier Bay analysis. Requires source artifact 14914948367."""
import argparse, hashlib, io, json, zipfile
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import binomtest
HASH="d4b902fb8216844bb078cf9ba0e9a87f1767defc1781534245761a45c82cadfd"
def read_source(path,source,needle):
    assert hashlib.sha256(path.read_bytes()).hexdigest()==HASH
    with zipfile.ZipFile(path) as z:
        m=json.loads(z.read("manifest.json"))
        f=next(x for s in m["sources"] if s["name"]==source for x in s["files"] if needle in x["source_name"])
        b=z.read(f["file"])
        assert hashlib.sha256(b).hexdigest()==f["sha256"]
        return pd.read_csv(io.BytesIO(b)),f["sha256"]
def paired_summary(pairs,metrics,early="early",late="late"):
    rng=np.random.default_rng(20261124);out={}
    for v in metrics:
        e=np.array([x[early][v] for x in pairs],float);l=np.array([x[late][v] for x in pairs],float)
        ok=np.isfinite(e)&np.isfinite(l);e,l=e[ok],l[ok];d=l-e;n=len(d)
        assert n>0
        pos=int((d>0).sum());neg=int((d<0).sum())
        out[v]=dict(n=n,early_mean=float(e.mean()),late_mean=float(l.mean()),difference=float(d.mean()),ci=np.quantile(rng.choice(d,(20000,n),replace=True).mean(1),[.025,.975]).tolist(),positive=pos,negative=neg,sign_p=float(binomtest(pos,pos+neg).pvalue) if pos+neg else None)
    return out
def forage(path):
    raw,sha=read_source(path,"forage","bouts_1993-2019.csv")
    def calc(dedup=True,min_bouts=5,summer=False):
        d=raw.drop_duplicates().copy() if dedup else raw.copy()
        date=pd.to_datetime(d.bout_date);d["year"]=date.dt.year;d["month"]=date.dt.month
        d=d[d.site_name.notna()&~d.site_name.isin(["Dundas","Althorp","Inian","Lemesurier",""])&(d.otter_long < -135.6)&d.otter_lat.notna()].copy()
        d["size_class"]=d.preysize_cd.fillna("").astype(str).str.lower().str.strip().str[0]
        d["valid_success"]=d.success_cd.isin(["y","n"])
        d["qty_missing"]=d.success_cd.eq("y")&(d.prey_qty.isna()|d.prey_qty.lt(1))
        d["qty_failed"]=d.success_cd.eq("n")&d.prey_qty.notna()&d.prey_qty.ne(0)
        d["qty"]=d.prey_qty.where(d.success_cd.eq("y"),0).fillna(0)
        d["small"]=d.qty.where(d.size_class.eq("1"),0);d["large"]=d.qty.where(d.size_class.isin(["2","3","4"]),0)
        d["unknown"]=d.qty-d.small-d.large
        a=d.groupby(["bout_id","dive_num"],sort=False).agg(site=("site_name","first"),year=("year","first"),month=("month","first"),nsite=("site_name","nunique"),nyear=("year","nunique"),nmonth=("month","nunique"),ndt=("dive_time","nunique"),nst=("surface_time","nunique"),nsuccess=("success_cd","nunique"),dt=("dive_time","first"),st=("surface_time","first"),valid=("valid_success","all"),missing=("qty_missing","any"),failed_qty=("qty_failed","any"),qty=("qty","sum"),small=("small","sum"),large=("large","sum"),unknown=("unknown","sum"))
        valid=a.valid&~a.missing&~a.failed_qty&a.nsite.eq(1)&a.nyear.eq(1)&a.nmonth.eq(1)&a.nsuccess.eq(1)&a.ndt.eq(1)&a.nst.eq(1)&a.dt.gt(0)&a.st.gt(0)
        p=a[valid].copy()
        p["time_min"]=(p.dt+p.st)/60
        p["period"]=np.select([p.year<=2007,p.year.between(2010,2011),p.year>=2018],["early","mid","late"],default="other")
        assert not p.period.eq("other").any()
        if summer:p=p[p.month.between(6,8)]
        p=p.reset_index()
        def metrics(x):
            o=dict(bouts=int(x.bout_id.nunique()),dives=int(len(x)),hours=float(x.time_min.sum()/60),prey=float(x.qty.sum()),small=float(x.small.sum()),large=float(x.large.sum()),unknown=float(x.unknown.sum()))
            for v in ["prey","small","large","unknown"]:
                o[v+"_per_hour"]=o[v]/o["hours"];o[v+"_per_dive"]=o[v]/o["dives"]
            o["small_share_known"]=o["small"]/(o["small"]+o["large"]) if o["small"]+o["large"] else None
            o["unknown_share"]=o["unknown"]/o["prey"] if o["prey"] else None
            return o
        pairs=[]
        for site,x in p.groupby("site"):
            e=x[x.period.eq("early")];l=x[x.period.eq("late")]
            if e.bout_id.nunique()>=min_bouts and l.bout_id.nunique()>=min_bouts:pairs.append(dict(site=site,early=metrics(e),late=metrics(l)))
        return dict(n_rows=len(d),n_unique_dives=len(a),n_complete_dives=len(p),n_bouts=p.bout_id.nunique(),excluded_dives=int((~valid).sum()),min_bouts=min_bouts,summer_only=summer,drop_identical_rows=dedup,all_period={k:metrics(x) for k,x in p.groupby("period")},paired_sites=pairs,paired_summary=paired_summary(pairs,["prey_per_hour","small_per_hour","large_per_hour","unknown_per_hour","small_share_known","unknown_share","prey_per_dive"]))
    return dict(source_sha256=sha,raw_rows=len(raw),exact_duplicate_rows=int(raw.duplicated().sum()),primary=calc(),sensitivity_keep_duplicates=calc(False),sensitivity_min10_bouts=calc(True,10),sensitivity_summer=calc(True,5,True))
def benthos(path):
    raw,sha=read_source(path,"benthos","sizeCount")
    keys=["region","site_zone","site_name"];qkeys=["year"]+keys+["quad"]
    assert raw[qkeys].notna().all().all()
    quad=raw[qkeys].drop_duplicates()
    def calc(dedup=False,threshold=50):
        d=raw.drop_duplicates() if dedup else raw
        c=d[d.species_type.eq("Clam")&d["count"].gt(0)].copy()
        assert c["size"].notna().all()
        c["large"]=c["count"].where(c["size"]>=threshold,0);c["small"]=c["count"]-c["large"];c["size_sum"]=c["size"]*c["count"]
        gkeys=["year"]+keys
        a=quad.groupby(gkeys).size().rename("quadrats").to_frame().join(c.groupby(gkeys)[["count","large","small","size_sum"]].sum(),how="left").fillna(0).reset_index()
        for v in ["count","large","small"]:a[v+"_per_quad"]=a[v]/a.quadrats
        a["mean_mm"]=a.size_sum/a["count"].replace(0,np.nan)
        a["period"]=np.where(a.year<=2007,"early","late")
        res={};cols=["count_per_quad","large_per_quad","small_per_quad","mean_mm"]
        for zone,x in a.groupby("site_zone"):
            pairs=[]
            for (region,site),s in x.groupby(["region","site_name"]):
                e=s[s.period.eq("early")];l=s[s.period.eq("late")]
                if not e.empty and not l.empty:pairs.append(dict(region=region,site=site,early_years=e.year.tolist(),late_years=l.year.tolist(),early=e[cols].mean().to_dict(),late=l[cols].mean().to_dict()))
            res[zone]=dict(sites=pairs,summary=paired_summary(pairs,cols))
        return res
    return dict(raw_rows=len(raw),observed_quadrats=len(quad),duplicate_rows=int(raw.duplicated().sum()),empty_indicator_positive_count=int(((raw.species_type=="EMPTY")&(raw["count"]>0)).sum()),source_csv_sha256=sha,threshold50=calc(),threshold40=calc(threshold=40),threshold60=calc(threshold=60),dedup50=calc(True))
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("artifact",type=Path);p.add_argument("--out",type=Path,required=True);a=p.parse_args()
    data=dict(forage=forage(a.artifact),benthos=benthos(a.artifact))
    a.out.write_text(json.dumps(data,indent=2,default=lambda o:o.item() if isinstance(o,np.generic) else str(o)).replace("NaN","null")+"\n")
