#!/usr/bin/env python3
"""Source-hash-verified trapping position reaggregation and survival crossover scenarios."""
import argparse,hashlib,io,json,zipfile
from pathlib import Path
from openpyxl import load_workbook
HASH="144aa9cbadf811e307f8c024180152e640f4a55c8f4fb19474382c69eef0ba6c"
def run(path):
    assert hashlib.sha256(path.read_bytes()).hexdigest()==HASH
    with zipfile.ZipFile(path) as z:
        m=json.loads(z.read("manifest.json"));name="meysick_seed_trapping.xlsx";b=z.read(name)
        assert hashlib.sha256(b).hexdigest()==next(x["sha256"] for x in m["sources"] if x.get("file")==name)
        raw=list(load_workbook(io.BytesIO(b),data_only=True).active.values)
    assert raw[1][:8]==("Treatment No","Description","Lateral width of objects (cm)","No objects in flume","Flow velocity (cm/s)","Scouring area (cm2)","Trapped seeds","No seeds")
    rows=[]
    for t,desc,width,nobj,v,area,k,n,*p in raw[2:]:
        assert n==30 and len(p)==9 and all(isinstance(x,int) and x>=0 for x in p) and 0<=sum(p)<=k<=n
        scour=sum(p[i] for i in (2,5,8));direct=sum(p)-scour
        rows.append(dict(t=t,desc=desc,v=v,n=n,k=k,direct=direct,scour=scour,unknown=k-sum(p)))
    assert len(rows)==160 and len({(r["t"],r["v"]) for r in rows})==160
    assert sum(r["unknown"]>0 for r in rows)==8 and sum(r["unknown"] for r in rows)==54
    def agg(rr):
        out={x:sum(r[x] for r in rr) for x in ("n","k","direct","scour","unknown")}
        out["capture_rate"]=out["k"]/out["n"];out["scour_share_bounds"]=[out["scour"]/out["k"],(out["scour"]+out["unknown"])/out["k"]] if out["k"] else None
        return out
    bins={"low_12_18":range(12,19,2),"mid_20_24":range(20,25,2),"high_26_30":range(26,31,2),"all":range(12,31,2)}
    flow={v:agg([r for r in rows if r["v"]==v]) for v in range(12,31,2)}
    pooled={b:agg([r for r in rows if r["v"] in vs]) for b,vs in bins.items()}
    selected={t:{b:agg([r for r in rows if r["t"]==t and r["v"] in vs]) for b,vs in bins.items()} for t in (2,7,16)}
    assert all(x["unknown"]==0 for d in selected.values() for x in d.values())
    comparisons={}
    for a,b in ((16,2),(16,7)):
        comparisons[f"{a}_vs_{b}"]={}
        for label in bins:
            x,y=selected[a][label],selected[b][label]
            assert x["n"]==y["n"]
            ds=x["scour"]-y["scour"];dd=x["direct"]-y["direct"]
            comparisons[f"{a}_vs_{b}"][label]={"direct_difference":dd,"scour_difference":ds,"capture_difference":x["k"]-y["k"],"min_scour_to_direct_survival_ratio_for_advantage":max(0,-dd/ds) if ds>0 else None,"status":"nonnegative routes" if dd>=0 and ds>=0 else "tradeoff" if ds>0 and dd<0 else "other"}
    scenarios=[]
    for ps,pd in [(0.44,.44),(.8,.44),(1,.44),(.5,.8)]:
        est={t:(ps*selected[t]["all"]["scour"]+pd*selected[t]["all"]["direct"])/selected[t]["all"]["n"] for t in (2,7,16)}
        scenarios.append({"scour_survival":ps,"direct_survival":pd,"surviving_trapped_fraction":est,"mixed_minus_dense":est[16]-est[7]})
    thresholds=[]
    for v in range(12,31,2):
        a=agg([r for r in rows if r["t"]==16 and r["v"]!=v]);b=agg([r for r in rows if r["t"]==7 and r["v"]!=v]);ds=a["scour"]-b["scour"];dd=a["direct"]-b["direct"]
        thresholds.append({"omitted_flow":v,"threshold":-dd/ds if ds>0 else None,"direct_difference":dd,"scour_difference":ds})
    return {"status":"response-open original flume reanalysis; survival scenarios not measured","source_sha256":HASH,"total":agg(rows),"by_flow":flow,"pooled_bins":pooled,"selected":selected,"comparisons":comparisons,"scenario_only":scenarios,"leave_one_flow_out":thresholds,"missing_location_rows":[r for r in rows if r["unknown"]],"limitations":["Position categories are not burial depths or survival. Missing locations bounded assuming recorded counts accurate and disjoint. Flow bins descriptive post hoc; no independent replicates within cells.","Conditional survival may differ across configurations and flow. Equal-flow weighting is an experimental grid, not environmental frequency.","Cross-study Infantes laboratory survival is only a numerical illustration; no local relationship between scour and burial verified."]}
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("artifact",type=Path);p.add_argument("--out",type=Path,required=True);a=p.parse_args();a.out.write_text(json.dumps(run(a.artifact),indent=2)+"\n")
