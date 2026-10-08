#!/usr/bin/env python3
"""Reference-saturation falsification of Tampa early-warning state predictors.

Unlike the original space/time baseline, both comparison arms include the
stable transect node identity. The target-year walk-forward splits, endpoint,
logistic learner and source-year quantitative predictors remain unchanged.

Registered contract: results/early_warning_site_identity_saturation_v1_contract.json
Evidence: post-hoc developmental audit of already-opened source outcomes.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import binomtest, wilcoxon
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, log_loss, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "results/early_warning_site_identity_saturation_v1_contract.json"
FROZEN = ROOT / "results/quantitative_early_warning_v1.json"
BASE = ROOT / "analysis/09_quantitative_early_warning.py"

spec = importlib.util.spec_from_file_location("tampa_early_warning_original", BASE)
orig = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(orig)

ARMS = {
    "space": orig.BASE_NUMERIC + orig.CATEGORY,
    "space_quant": orig.BASE_NUMERIC + orig.CATEGORY + orig.QUANTITATIVE,
    "node": orig.BASE_NUMERIC + orig.CATEGORY + ["node_id"],
    "node_quant": orig.BASE_NUMERIC + orig.CATEGORY + ["node_id"] + orig.QUANTITATIVE,
}
CATS = ["water_body", "node_id"]


def make_model(features):
    if "node_id" not in features:
        return orig.make_model(features)
    cats = [c for c in CATS if c in features]
    numeric = [c for c in features if c not in cats]
    pre = ColumnTransformer([
        ("numeric", StandardScaler(), numeric),
        ("categorical", OneHotEncoder(handle_unknown="ignore"), cats),
    ])
    return Pipeline([
        ("preprocess", pre),
        ("model", LogisticRegression(C=1.0, max_iter=2000)),
    ])


def replay(transitions):
    scores=[]
    predictions=[]
    for year in sorted(transitions.target_year.unique()):
        train = transitions.loc[transitions.target_year < year]
        test = transitions.loc[transitions.target_year == year]
        if int(train.loss.sum()) < orig.MIN_TRAIN_LOSSES or (len(train) - int(train.loss.sum())) < orig.MIN_TRAIN_PERSISTENCE:
            continue
        pred={}
        for name,columns in ARMS.items():
            model=make_model(columns)
            model.fit(train[columns],train.loss)
            values=np.asarray(model.predict_proba(test[columns])[:,1],float)
            pred[name]=values
            scores.append({
                "target_year":int(year),
                "arm":name,
                "n":int(len(test)),
                "losses":int(test.loss.sum()),
                "log_loss":float(log_loss(test.loss,values,labels=[0,1])),
                "brier":float(brier_score_loss(test.loss,values)),
            })
        for i,(_,row) in enumerate(test.iterrows()):
            predictions.append({
                "node_id":str(row.node_id),
                "target_year":int(year),
                "loss":int(row.loss),
                **{f"p_{key}":float(v[i]) for key,v in pred.items()}
            })
    return pd.DataFrame(scores),pd.DataFrame(predictions)


def summarize(years, predictions, omit_2016=False):
    ys=years.loc[years.target_year!=2016].copy() if omit_2016 else years.copy()
    pr=predictions.loc[predictions.target_year!=2016].copy() if omit_2016 else predictions.copy()
    pivot=ys.pivot(index="target_year",columns="arm",values="log_loss")
    original=pivot["space_quant"]-pivot["space"]
    delta=pivot["node_quant"]-pivot["node"]
    wins=int((delta<0).sum())
    ties=int((delta==0).sum())
    paired=wilcoxon(delta,alternative="less",zero_method="wilcox")
    metrics={}
    for arm in ARMS:
        prob=pr[f"p_{arm}"]
        metrics[arm]={
            "macro_log_loss":float(pivot[arm].mean()),
            "pooled_log_loss":float(log_loss(pr.loss,prob,labels=[0,1])),
            "pooled_brier":float(brier_score_loss(pr.loss,prob)),
            "pooled_auc":float(roc_auc_score(pr.loss,prob)),
        }
    return {
        "n_scored_target_years":int(len(pivot)),
        "target_year_range":[int(pivot.index.min()),int(pivot.index.max())],
        "scored_rows":int(len(pr)),
        "recorded_losses":int(pr.loss.sum()),
        "metrics":metrics,
        "node_increment":{
            "macro_delta_log_loss":float(delta.mean()),
            "median_target_year_delta":float(delta.median()),
            "wins_node_quant":wins,
            "wins_node":int((delta>0).sum()),
            "ties":ties,
            "sign_test_one_sided_p":float(binomtest(wins,len(delta)-ties,0.5,alternative="greater").pvalue),
            "wilcoxon_one_sided_p":float(paired.pvalue),
            "support_rule_passed":bool(float(delta.mean())<0 and wins>=16 and binomtest(wins,len(delta)-ties,0.5,alternative="greater").pvalue<0.05),
        },
        "original_space_delta_log_loss":float(original.mean()),
        "original_space_wins_quant":int((original<0).sum()),
        "comparison_by_year":[
            {
                "target_year":int(year),
                "space_delta":float(original.loc[year]),
                "node_delta":float(delta.loc[year]),
            }
            for year in pivot.index
        ]
    }


def main(input_dir:Path,outdir:Path):
    contract=json.loads(CONTRACT.read_text(encoding="utf-8"))
    frozen=json.loads(FROZEN.read_text(encoding="utf-8"))
    quant=pd.read_csv(input_dir/"quant_annual_panel.csv")
    community=pd.read_csv(input_dir/"community_quant_annual.csv")
    rows=orig.build_transitions(quant,community)
    assert int(len(rows))==frozen["transition_registry"]["source_positive_consecutive_transitions"]==688
    assert int(rows.loss.sum())==frozen["transition_registry"]["recorded_losses"]==24
    years,pr=replay(rows)
    primary=summarize(years,pr,omit_2016=False)
    sensitivity=summarize(years,pr,omit_2016=True)

    old=frozen["primary"]
    assert primary["n_scored_target_years"]==old["target_years"]==23
    assert primary["scored_rows"]==old["pooled_rows"]==570
    assert primary["recorded_losses"]==old["pooled_losses"]==19
    assert primary["original_space_wins_quant"]==old["quantitative_wins"]==17
    for key,orig_key in [("space","baseline"),("space_quant","quantitative")]:
        observed=primary["metrics"][key]
        assert abs(observed["macro_log_loss"]-old[f"macro_{orig_key}_log_loss"])<1e-9,(key,observed["macro_log_loss"])
        assert abs(observed["pooled_auc"]-old[f"pooled_{orig_key}_auc"])<1e-9

    result={
      "schema":"tampa.early_warning_site_identity_saturation_v1",
      "evidence_class":contract["evidence_class"],
      "contract":str(CONTRACT.relative_to(ROOT)),
      "source":"tbep-tech/obis-example at the previously pinned commit",
      "question":contract["scientific_question"],
      "registry":{"transitions":int(len(rows)),"recorded_loss_transitions":int(rows.loss.sum()),"nodes":int(rows.node_id.nunique())},
      "reproduces_original_space_comparison":True,
      "primary":primary,
      "sensitivity_exclude_2016":sensitivity,
      "status":"NODE_SATURATED_QUANT_WARNING_SUPPORTED" if primary["node_increment"]["support_rule_passed"] else "NODE_SATURATED_QUANT_WARNING_NOT_SUPPORTED",
      "claim_boundary":contract["boundary"]
    }
    outdir.mkdir(parents=True,exist_ok=True)
    (outdir/"early_warning_site_identity_saturation_v1.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    years.to_csv(outdir/"early_warning_site_identity_year_scores.csv",index=False)
    pr.to_csv(outdir/"early_warning_site_identity_predictions.csv",index=False)
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--input",type=Path,default=Path("results/generated_site_warning"))
    parser.add_argument("--out",type=Path,default=Path("results/generated_site_warning"))
    args=parser.parse_args()
    main(args.input,args.out)
