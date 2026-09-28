#!/usr/bin/env python3
"""Test exact-point Thalassia recovery after alternative-seagrass versus no-seagrass loss states."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
C=json.loads((ROOT/"results/microsite_recovery_pathway_v1_contract.json").read_text())
H=C["primary_hypothesis"]
BOOT=int(H["bootstrap_replicates"])
SEED=int(H["random_seed"])
MIN_EVENTS=int(H["minimum_sequences_per_intermediate_class"])
MIN_NODES=int(H["minimum_nodes_per_intermediate_class"])


def taxa_set(x)->set[str]:
    s="" if pd.isna(x) else str(x).strip()
    return {v.strip() for v in s.split(";") if v.strip()} if s else set()


def build_sequences(py:pd.DataFrame)->pd.DataFrame:
    required={
        "point_id","node_id","water_body","year",
        "thalassia_present","any_seagrass_present","alternative_species"
    }
    missing=required.difference(py.columns)
    if missing:
        raise RuntimeError(f"missing point-year columns: {sorted(missing)}")

    rows=[]
    for point_id,g in py.groupby("point_id",sort=True):
        recs=g.sort_values("year").to_dict("records")
        for i in range(len(recs)-2):
            a,b,c=recs[i],recs[i+1],recs[i+2]
            y0,y1,y2=int(a["year"]),int(b["year"]),int(c["year"])
            if not (y1==y0+1 and y2==y1+1):
                continue
            if y0<2016 or y2>2025:
                continue
            if not bool(a["thalassia_present"]):
                continue
            if bool(b["thalassia_present"]):
                continue

            intermediate="other_seagrass" if bool(b["any_seagrass_present"]) else "no_seagrass"
            b_alt=taxa_set(b["alternative_species"])
            c_alt=taxa_set(c["alternative_species"])
            if intermediate=="other_seagrass" and not b_alt:
                raise RuntimeError(f"other-seagrass intermediate lacks taxon: {point_id} {y1}")
            if intermediate=="no_seagrass" and b_alt:
                raise RuntimeError(f"no-seagrass intermediate has alternative taxon: {point_id} {y1}")

            rows.append({
                "point_id":point_id,
                "node_id":a["node_id"],
                "water_body":a["water_body"],
                "source_year":y0,
                "loss_year":y1,
                "recovery_year":y2,
                "intermediate_state":intermediate,
                "thalassia_return":int(bool(c["thalassia_present"])),
                "intermediate_alternative_species":";".join(sorted(b_alt)),
                "recovery_alternative_species":";".join(sorted(c_alt)),
                "intermediate_taxon_persists_to_recovery_year":int(bool(b_alt & c_alt)),
            })
    return pd.DataFrame(rows)


def state_summary(d:pd.DataFrame,state:str)->dict:
    x=d[d["intermediate_state"]==state]
    return {
        "sequences":int(len(x)),
        "nodes":int(x["node_id"].nunique()) if len(x) else 0,
        "thalassia_return_fraction":float(x["thalassia_return"].mean()) if len(x) else None,
    }


def bootstrap_difference(d:pd.DataFrame)->dict:
    other=state_summary(d,"other_seagrass")
    bare=state_summary(d,"no_seagrass")
    estimable=bool(
        other["sequences"]>=MIN_EVENTS and bare["sequences"]>=MIN_EVENTS
        and other["nodes"]>=MIN_NODES and bare["nodes"]>=MIN_NODES
    )
    out={
        "other_seagrass":other,
        "no_seagrass":bare,
        "estimable":estimable,
        "difference_other_minus_no_seagrass":None,
        "ci95":None,
        "classification":"non_estimable" if not estimable else None,
    }
    if not estimable:
        return out

    point=float(other["thalassia_return_fraction"]-bare["thalassia_return_fraction"])
    nodes=np.asarray(sorted(d["node_id"].unique()),dtype=object)
    by_node={n:d[d["node_id"]==n] for n in nodes}
    rng=np.random.default_rng(SEED)
    vals=[]
    attempts=0
    max_attempts=BOOT*20
    while len(vals)<BOOT and attempts<max_attempts:
        attempts+=1
        sample=rng.choice(nodes,size=len(nodes),replace=True)
        b=pd.concat([by_node[n] for n in sample],ignore_index=True)
        so=state_summary(b,"other_seagrass")
        sb=state_summary(b,"no_seagrass")
        if so["sequences"]==0 or sb["sequences"]==0:
            continue
        vals.append(float(so["thalassia_return_fraction"]-sb["thalassia_return_fraction"]))
    if len(vals)!=BOOT:
        raise RuntimeError(f"could not obtain {BOOT} estimable bootstrap replicates")
    ci=np.quantile(np.asarray(vals,float),[.025,.975])
    classification=(
        "habitat_continuity" if ci[0]>0 else
        "alternative_state_lock_in" if ci[1]<0 else
        "unresolved"
    )
    out.update({
        "difference_other_minus_no_seagrass":point,
        "ci95":[float(ci[0]),float(ci[1])],
        "classification":classification,
        "bootstrap_attempts":int(attempts),
    })
    return out


def by_bay(d:pd.DataFrame)->list[dict]:
    rows=[]
    for bay,g in d.groupby("water_body",sort=True):
        a=state_summary(g,"other_seagrass")
        b=state_summary(g,"no_seagrass")
        rows.append({
            "water_body":bay,
            "sequences":int(len(g)),
            "nodes":int(g["node_id"].nunique()),
            "other_seagrass_sequences":a["sequences"],
            "other_seagrass_return_fraction":a["thalassia_return_fraction"],
            "no_seagrass_sequences":b["sequences"],
            "no_seagrass_return_fraction":b["thalassia_return_fraction"],
        })
    return rows


def taxon_return(d:pd.DataFrame)->pd.DataFrame:
    rows=[]
    x=d[d["intermediate_state"]=="other_seagrass"].copy()
    for _,r in x.iterrows():
        for taxon in sorted(taxa_set(r["intermediate_alternative_species"])):
            rows.append({
                "taxon":taxon,
                "water_body":r["water_body"],
                "node_id":r["node_id"],
                "point_id":r["point_id"],
                "loss_year":int(r["loss_year"]),
                "recovery_year":int(r["recovery_year"]),
                "thalassia_return":int(r["thalassia_return"]),
            })
    return pd.DataFrame(rows)


def main(input_dir:Path,outdir:Path):
    outdir.mkdir(parents=True,exist_ok=True)
    py=pd.read_csv(input_dir/"community_buffering_point_year_consensus.csv")
    if len(py)!=45494:
        raise RuntimeError(f"point-year registry drift: {len(py)}")
    repeated=int((py.groupby("point_id")["year"].nunique()>=3).sum())
    if repeated<=0:
        raise RuntimeError("no stable points with >=3 consensus years")

    d=build_sequences(py)
    if len(d)==0:
        raise RuntimeError("no frozen three-year recovery sequences")
    if int(d["source_year"].min())<2016 or int(d["recovery_year"].max())>2025:
        raise RuntimeError("frozen recovery period violated")

    primary=bootstrap_difference(d)
    tx=taxon_return(d)

    other=d[d["intermediate_state"]=="other_seagrass"].copy()
    persistence_by_return=[]
    for label,val in [("return",1),("no_return",0)]:
        z=other[other["thalassia_return"]==val]
        persistence_by_return.append({
            "thalassia_outcome":label,
            "sequences":int(len(z)),
            "nodes":int(z["node_id"].nunique()) if len(z) else 0,
            "intermediate_taxon_persistence_fraction":(
                float(z["intermediate_taxon_persists_to_recovery_year"].mean()) if len(z) else None
            ),
        })

    result={
        "schema":"tampa.microsite_recovery_pathway_v1.result",
        "status":primary["classification"],
        "contract":"results/microsite_recovery_pathway_v1_contract.json",
        "registry":{
            "consensus_point_years":int(len(py)),
            "points_with_at_least_three_consensus_years":repeated,
            "eligible_three_year_loss_sequences":int(len(d)),
            "nodes":int(d["node_id"].nunique()),
        },
        "primary":primary,
        "bay_segment_descriptive":by_bay(d),
        "taxon_return_descriptive":(
            tx.groupby("taxon",as_index=False)
            .agg(events=("thalassia_return","size"),
                 thalassia_return_fraction=("thalassia_return","mean"))
            .to_dict("records") if len(tx) else []
        ),
        "intermediate_taxon_persistence_by_thalassia_outcome":persistence_by_return,
        "interpretation":(
            "A positive classified difference is consistent with habitat continuity: points that retain another "
            "seagrass after focal Thalassia loss are more likely to re-record Thalassia one year later. A negative "
            "classified difference is consistent with alternative-state lock-in. An interval overlapping zero leaves "
            "the pathway unresolved."
        ),
        "claim_boundary":C["claim_boundary"],
    }

    d.to_csv(outdir/"microsite_recovery_sequences.csv",index=False)
    tx.to_csv(outdir/"microsite_recovery_taxon_rows.csv",index=False)
    pd.DataFrame(result["bay_segment_descriptive"]).to_csv(
        outdir/"microsite_recovery_by_bay.csv",index=False
    )
    (outdir/"microsite_recovery_pathway_v1.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n"
    )
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--input",type=Path,default=Path("results/generated_microsite_recovery"))
    p.add_argument("--out",type=Path,default=Path("results/generated_microsite_recovery"))
    a=p.parse_args()
    main(a.input,a.out)
