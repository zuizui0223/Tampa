#!/usr/bin/env python3
"""Three-year exact-point test of community continuity and Thalassia return."""
from __future__ import annotations
import argparse, json, math
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
C=json.loads((ROOT/"results/community_recovery_v1_contract.json").read_text())
SEED=2026092808
BOOT=5000


def sset(x):
    if pd.isna(x): return set()
    return {v for v in str(x).split(";") if v}


def build_sequences(py):
    rows=[]
    by_point={p:g.sort_values("year").set_index("year") for p,g in py.groupby("point_id")}
    for point,g in by_point.items():
        years=sorted(g.index.astype(int).tolist())
        for y in years:
            if not (2016<=y<=2024): continue
            if (y-1) not in g.index or (y+1) not in g.index: continue
            a=g.loc[y-1]; b=g.loc[y]; c=g.loc[y+1]
            if isinstance(a,pd.DataFrame) or isinstance(b,pd.DataFrame) or isinstance(c,pd.DataFrame):
                raise RuntimeError(f"duplicate point-year {point} {y}")
            if not bool(a["thalassia_present"]) or bool(b["thalassia_present"]):
                continue
            src_alt=sset(a.get("alternative_species",""))
            loss_alt=sset(b.get("alternative_species",""))
            retained=src_alt & loss_alt
            new=loss_alt-src_alt
            rows.append({
                "point_id":point,"node_id":a["node_id"],"water_body":a["water_body"],
                "source_year":int(y-1),"loss_year":int(y),"recovery_year":int(y+1),
                "loss_year_vegetated":bool(b["any_seagrass_present"]),
                "loss_year_alternative_species":";".join(sorted(loss_alt)),
                "retained_preexisting_alternative":bool(retained),
                "new_only_alternative":bool(loss_alt and not retained),
                "thalassia_return_next_year":bool(c["thalassia_present"]),
            })
    return pd.DataFrame(rows)


def frac(d,col):
    return float(d[col].astype(bool).mean()) if len(d) else math.nan


def diff_boot(d,group_col,group_true_label,min_events,min_nodes,seed):
    a=d[d[group_col]].copy(); b=d[~d[group_col]].copy()
    an=set(a.node_id); bn=set(b.node_id)
    estimable=len(a)>=min_events and len(b)>=min_events and len(an)>=min_nodes and len(bn)>=min_nodes
    out={
      f"{group_true_label}_events":int(len(a)),
      f"{group_true_label}_nodes":int(len(an)),
      f"{group_true_label}_return_fraction":frac(a,"thalassia_return_next_year"),
      "comparison_events":int(len(b)),
      "comparison_nodes":int(len(bn)),
      "comparison_return_fraction":frac(b,"thalassia_return_next_year"),
      "estimable":bool(estimable),"supported":False,"difference":None,"ci95":None
    }
    if not estimable: return out
    obs=out[f"{group_true_label}_return_fraction"]-out["comparison_return_fraction"]
    nodes=sorted(d.node_id.unique())
    by={n:d[d.node_id==n] for n in nodes}
    rng=np.random.default_rng(seed); vals=[]
    for _ in range(BOOT):
        chosen=rng.choice(nodes,size=len(nodes),replace=True)
        x=pd.concat([by[n] for n in chosen],ignore_index=True)
        aa=x[x[group_col]]; bb=x[~x[group_col]]
        if len(aa)==0 or len(bb)==0: continue
        vals.append(frac(aa,"thalassia_return_next_year")-frac(bb,"thalassia_return_next_year"))
    arr=np.asarray(vals,float); ci=np.quantile(arr,[.025,.975])
    out.update({"difference":float(obs),"ci95":[float(ci[0]),float(ci[1])],
                "bootstrap_replicates_used":int(len(arr)),"supported":bool(ci[0]>0)})
    return out


def main(input_dir:Path,outdir:Path):
    outdir.mkdir(parents=True,exist_ok=True)
    py=pd.read_csv(input_dir/"community_buffering_point_year_consensus.csv")
    seq=build_sequences(py)
    if len(seq)==0: raise RuntimeError("no eligible three-year sequences")

    h4a_cfg=C["hypotheses"]["H4a_habitat_continuity_recovery"]
    h4a=diff_boot(seq,"loss_year_vegetated","vegetated",
                  int(h4a_cfg["minimum_events_per_group"]),int(h4a_cfg["minimum_nodes_per_group"]),SEED)

    occ=seq[seq["loss_year_vegetated"]].copy()
    # H4b compares retained-preexisting to new-only; exclude any logically unclassified occupied row.
    occ=occ[occ["retained_preexisting_alternative"] | occ["new_only_alternative"]].copy()
    h4b_cfg=C["hypotheses"]["H4b_preexisting_insurance_recovery"]
    h4b=diff_boot(occ,"retained_preexisting_alternative","retained_preexisting",
                  int(h4b_cfg["minimum_events_per_group"]),int(h4b_cfg["minimum_nodes_per_group"]),SEED+1)

    byseg=(seq.groupby("water_body").agg(
        sequences=("point_id","size"),nodes=("node_id","nunique"),
        loss_year_vegetated_fraction=("loss_year_vegetated","mean"),
        thalassia_return_fraction=("thalassia_return_next_year","mean")
    ).reset_index())

    result={
      "schema":"tampa.community_recovery_v1.result",
      "status":(
        "both_recovery_hypotheses_supported" if h4a["supported"] and h4b["supported"] else
        "habitat_continuity_recovery_supported" if h4a["supported"] else
        "preexisting_insurance_recovery_supported" if h4b["supported"] else
        "community_recovery_not_supported"
      ),
      "contract":"results/community_recovery_v1_contract.json",
      "registry":{
        "three_year_thalassia_loss_sequences":int(len(seq)),
        "nodes":int(seq.node_id.nunique()),
        "loss_year_vegetated":int(seq.loss_year_vegetated.sum()),
        "loss_year_bare":int((~seq.loss_year_vegetated).sum())
      },
      "overall_one_year_thalassia_return_fraction":frac(seq,"thalassia_return_next_year"),
      "H4a_habitat_continuity_recovery":h4a,
      "H4b_preexisting_insurance_recovery":h4b,
      "interpretation":"Tests whether retaining seagrass habitat/community continuity in the focal-loss year predicts recorded Thalassia return one year later at the same meter mark.",
      "claim_boundary":C["claim_boundary"]
    }
    seq.to_csv(outdir/"community_recovery_sequences.csv",index=False)
    byseg.to_csv(outdir/"community_recovery_by_segment.csv",index=False)
    (outdir/"community_recovery_v1.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--input",type=Path,default=Path("results/generated_community_recovery"))
    p.add_argument("--out",type=Path,default=Path("results/generated_community_recovery"))
    a=p.parse_args(); main(a.input,a.out)
