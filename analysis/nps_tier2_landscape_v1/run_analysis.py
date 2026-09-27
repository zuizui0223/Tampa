#!/usr/bin/env python3
"""NPS Tier-2 cross-scale Zostera landscape analysis under frozen semantics."""
from __future__ import annotations
import argparse,csv,io,json,math
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from urllib.request import Request,urlopen
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
C=json.loads((HERE/"analysis_contract.json").read_text())
D=json.loads((HERE/"deep_eml_result.json").read_text())
BOOT=5000; SEED=20260927

def req(s,label):
    x="" if s is None else str(s).strip()
    if not x: raise RuntimeError(f"blank_required:{label}")
    return x

def parse_cover(s,label):
    x="" if s is None else str(s).strip()
    if x==C["sample_semantics"]["missing_token"]: return None
    try: v=float(x)
    except Exception as e: raise RuntimeError(f"invalid_cover:{label}:{x!r}") from e
    lo,hi=C["sample_semantics"]["percent_cover_valid_range"]
    if not math.isfinite(v) or not(lo<=v<=hi): raise RuntimeError(f"cover_out_of_range:{label}:{v}")
    return v

def fetch():
    r=Request(C["source"]["csv_url"],headers={"Accept-Encoding":"identity","User-Agent":"Tampa-NPS-Tier2-Landscape/1.0"})
    with urlopen(r,timeout=90) as resp:
        if resp.status!=200: raise RuntimeError(f"csv_http_{resp.status}")
        return resp.read(20_000_001)

def parse(data):
    text=data.decode("utf-8-sig")
    rd=csv.DictReader(io.StringIO(text,newline=""))
    if rd.fieldnames!=C["source"]["expected_header"]:
        raise RuntimeError(f"header_drift:{rd.fieldnames!r}")
    rows=[]
    for i,row in enumerate(rd,start=2):
        park=req(row["Park_Code"],f"park row{i}")
        if park not in C["source"]["allowed_parks"]: raise RuntimeError(f"unexpected_park:{park}")
        species=req(row["Species"],f"species row{i}")
        if species not in C["source"]["allowed_species"]: raise RuntimeError(f"unexpected_species:{species}")
        date=datetime.fromisoformat(req(row["Date"],f"date row{i}")).date()
        event=req(row["Event_Code"],f"event row{i}")
        q=req(row["Quadrat_Ltr"],f"quadrat row{i}")
        if q not in {"A","B","C","D"}: raise RuntimeError(f"unexpected_quadrat:{q}")
        station=req(row["Station"],f"station row{i}")
        hexagon=req(row["Hexagon"],f"hexagon row{i}")
        cover=parse_cover(row["Percent_Cover"],f"row{i}")
        rows.append({"park":park,"event":event,"date":date,"year":date.year,"hexagon":hexagon,
                     "station":station,"quadrat":q,"species":species,"cover":cover})
    return rows

def annualize(rows):
    qmap=defaultdict(lambda: defaultdict(list))
    qmeta={}
    for r in rows:
        key=(r["event"],r["quadrat"])
        qmap[key][r["species"]].append(r["cover"])
        qmeta[key]=r
    qrows=[]
    for key,spp in qmap.items():
        collapsed={}
        for sp,vals in spp.items():
            non=[v for v in vals if v is not None]
            if non and any(v is None for v in vals):
                raise RuntimeError(f"mixed_numeric_na:{key}:{sp}")
            if len(set(non))>1:
                raise RuntimeError(f"discordant_repeated_cover_state:{key}:{sp}:{sorted(set(non))}")
            collapsed[sp]=(float(non[0]) if non else None)
        numeric_any=any(v is not None for v in collapsed.values())
        if not numeric_any: continue
        r=qmeta[key]
        focal_value=collapsed.get(C["source"]["focal_species"])
        other_value=collapsed.get("Ruppia maritima")
        if focal_value is not None:
            focal=float(focal_value)
        elif other_value is not None:
            focal=0.0
        else:
            continue
        qrows.append({**{k:r[k] for k in ("park","event","date","year","hexagon","station","quadrat")},
                      "focal_cover":focal,"focal_present":int(focal>0)})
    qdf=pd.DataFrame(qrows)
    if qdf.empty: raise RuntimeError("no_sampled_quadrats")
    # Stable station identity is park+hexagon+station; pool visits in same calendar year.
    srows=[]
    for (park,hexagon,station,year),g in qdf.groupby(["park","hexagon","station","year"]):
        events=g["event"].nunique()
        srows.append({
          "park":park,"hexagon":hexagon,"station":station,
          "station_id":f"{park}::{hexagon}::{station}","year":int(year),
          "sampled_quadrats":int(len(g)),
          "survey_count":int(events),
          "focal_presence":int(g["focal_present"].max()),
          "focal_frequency":float(g["focal_present"].mean()),
          "focal_mean_cover":float(g["focal_cover"].mean())
        })
    return qdf,pd.DataFrame(srows).sort_values(["park","station_id","year"]).reset_index(drop=True)

def stat_table(sdf,ycol):
    rows=[]
    for (park,node),g in sdf.groupby(["park","station_id"]):
        if len(g)<C["trend_estimands"]["minimum_repeated_years_per_station"]: continue
        x=g["year"].to_numpy(float); y=g[ycol].to_numpy(float)
        xc=x-x.mean(); yc=y-y.mean(); sxx=float(xc@xc)
        if sxx<=0: continue
        sxy=float(xc@yc)
        rows.append({"park":park,"station_id":node,"n":len(g),"sxx":sxx,"sxy":sxy,"slope":sxy/sxx})
    return pd.DataFrame(rows)

def pooled(st):
    return float(st["sxy"].sum()/st["sxx"].sum())

def boot(st,seed):
    rng=np.random.default_rng(seed); a=[]
    sxx=st["sxx"].to_numpy(float); sxy=st["sxy"].to_numpy(float); n=len(st)
    for _ in range(BOOT):
        idx=rng.integers(0,n,n); den=sxx[idx].sum()
        a.append(sxy[idx].sum()/den if den>0 else np.nan)
    return [float(np.nanquantile(a,.025)),float(np.nanquantile(a,.975))]

def metric_by_park(sdf,ycol,seed):
    st=stat_table(sdf,ycol); out={}
    for i,(park,g) in enumerate(st.groupby("park")):
        out[park]={"repeated_stations":int(len(g)),"within_station_slope_per_year":pooled(g),
                   "station_bootstrap_ci95":boot(g,seed+i),
                   "negative_station_slopes":int((g.slope<0).sum()),
                   "positive_station_slopes":int((g.slope>0).sum())}
    return out,st

def main(outdir:Path):
    if D["fingerprint"]!=C["requires_deep_eml_fingerprint"]: raise RuntimeError("deep_eml_drift")
    outdir.mkdir(parents=True,exist_ok=True)
    data=fetch(); rows=parse(data); qdf,sdf=annualize(rows)
    py=sdf.groupby(["park","year"],as_index=False).agg(
      stations=("station_id","nunique"),
      prevalence=("focal_presence","mean"),
      mean_station_frequency=("focal_frequency","mean"),
      mean_station_cover=("focal_mean_cover","mean"))
    cover,cover_nodes=metric_by_park(sdf,"focal_mean_cover",SEED)
    freq,freq_nodes=metric_by_park(sdf,"focal_frequency",SEED+100)
    pres,pres_nodes=metric_by_park(sdf,"focal_presence",SEED+200)
    summary={
      "schema":"tampa.nps_tier2_landscape_state_v1.result",
      "status":"observational_cross_scale_ecology",
      "source":{"csv_bytes":len(data),"raw_rows":len(rows),"sampled_quadrats":int(len(qdf)),
                "station_years":int(len(sdf)),"years":[int(sdf.year.min()),int(sdf.year.max())],
                "parks":sorted(sdf.park.unique().tolist())},
      "park_trends":{"mean_station_cover":cover,"mean_station_frequency":freq,"station_presence":pres},
      "interpretation":"Tier-2 describes bay-wide/random-station temporal change, complementary to Tier-3 persistent-transect thinning. Directional agreement or disagreement is interpreted as cross-scale degradation structure, not as directly exchangeable effect sizes.",
      "claim_boundary":C["claim_boundary"]
    }
    qdf.to_csv(outdir/"nps_tier2_quadrat_state.csv",index=False)
    sdf.to_csv(outdir/"nps_tier2_station_year.csv",index=False)
    py.to_csv(outdir/"nps_tier2_park_year.csv",index=False)
    cover_nodes.to_csv(outdir/"nps_tier2_cover_station_slopes.csv",index=False)
    freq_nodes.to_csv(outdir/"nps_tier2_frequency_station_slopes.csv",index=False)
    pres_nodes.to_csv(outdir/"nps_tier2_presence_station_slopes.csv",index=False)
    (outdir/"nps_tier2_landscape_state_v1.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
    print(json.dumps(summary,indent=2,sort_keys=True))

if __name__=="__main__":
    p=argparse.ArgumentParser(); p.add_argument("--out",type=Path,default=Path("results/generated_nps_tier2"))
    a=p.parse_args(); main(a.out)
