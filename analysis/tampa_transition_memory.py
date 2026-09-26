#!/usr/bin/env python3
"""Reproduce annual Thalassia transect-state transitions from the pinned TBEP source."""
import argparse, csv, io, json, math, urllib.request
from datetime import date
from pathlib import Path

import pandas as pd
from scipy.stats import fisher_exact
import statsmodels.api as sm
import statsmodels.formula.api as smf

COMMIT="6c567beff95ea04f0e397101befb49d5233ace8f"
EVENT_BLOB="583b4d4e328290ab065346579eb4f29f03ea0f99"
OCC_BLOB="d34aeb5aedb72459d1e04059629cb09450df929e"
BASE=f"https://raw.githubusercontent.com/tbep-tech/obis-example/{COMMIT}/dwc"
FOCAL="Thalassia testudinum"
EXPECTED={"visits":1497,"nodes":71,"years":29,"positive":927,"negative":570,
          "ever_positive_nodes":54,"focal_rows":8726,"annual":1176,"prev_positive":688}

def fetch(name):
    req=urllib.request.Request(f"{BASE}/{name}",headers={"User-Agent":"Tampa-transition-memory/1.0"})
    with urllib.request.urlopen(req,timeout=120) as r:
        return r.read().decode("utf-8")

def reconstruct():
    parents, child_parent, seen = {}, {}, set()
    for r in csv.DictReader(io.StringIO(fetch("event.csv"))):
        eid=r["eventID"].strip(); par=r["parentEventID"].strip(); typ=r["eventType"].strip()
        if typ=="Transect" and not par:
            year=int(r["year"]); node=r["locationID"].strip(); key=(node,year)
            if key in seen: raise RuntimeError(f"duplicate node-year: {key}")
            seen.add(key)
            parents[eid]={"unit_id":eid,"node_id":node,"year":year,
                          "date":r["eventDate"].strip()[:10],"water_body":r["waterBody"].strip()}
        elif typ=="Point" and par:
            child_parent[eid]=par
    positive=set(); focal_rows=0
    for r in csv.DictReader(io.StringIO(fetch("occurrence.csv"))):
        if r["scientificName"]!=FOCAL: continue
        focal_rows+=1
        if r["occurrenceStatus"]!="present": raise RuntimeError("focal row not present")
        par=child_parent.get(r["eventID"])
        if par in parents: positive.add(par)
    states=[]
    for eid,m in parents.items():
        d=date.fromisoformat(m["date"])
        states.append({**m,"doy":d.timetuple().tm_yday,"label":int(eid in positive)})
    df=pd.DataFrame(states).sort_values(["node_id","year"]).reset_index(drop=True)
    audit={"visits":len(df),"nodes":int(df.node_id.nunique()),"years":int(df.year.nunique()),
           "positive":int(df.label.sum()),"negative":int((1-df.label).sum()),
           "ever_positive_nodes":int(df.loc[df.label.eq(1),"node_id"].nunique()),
           "focal_rows":focal_rows,
           "dec25_dates":int(((pd.to_datetime(df.date).dt.month==12)&(pd.to_datetime(df.date).dt.day==25)).sum())}
    for k in ["visits","nodes","years","positive","negative","ever_positive_nodes","focal_rows"]:
        if audit[k]!=EXPECTED[k]: raise RuntimeError(f"audit drift {k}: {audit[k]} != {EXPECTED[k]}")
    return df,audit

def transitions(states):
    out=[]
    for node,g in states.groupby("node_id"):
        g=g.sort_values("year").reset_index(drop=True)
        for i in range(1,len(g)):
            a,b=g.iloc[i-1],g.iloc[i]
            out.append({"node_id":node,"water_body":b.water_body,"from_year":int(a.year),
                        "to_year":int(b.year),"gap":int(b.year-a.year),
                        "prev":int(a.label),"curr":int(b.label)})
    return pd.DataFrame(out)

def exact(a_loss,a_ok,b_loss,b_ok):
    r=fisher_exact([[a_loss,a_ok],[b_loss,b_ok]])
    return {"odds_ratio":float(r.statistic),"p_value":float(r.pvalue)}

def analyse(states,audit):
    annual=transitions(states)
    annual=annual.loc[annual.gap.eq(1)].copy()
    if len(annual)!=EXPECTED["annual"] or int(annual.prev.sum())!=EXPECTED["prev_positive"]:
        raise RuntimeError("annual transition audit drift")
    pp=annual.loc[annual.prev.eq(1)].copy()
    pp["loss"]=1-pp.curr; pp["is2016"]=pp.to_year.eq(2016).astype(int)
    pp["middle"]=pp.water_body.eq("Middle Tampa Bay").astype(int)
    n11=int(((annual.prev==1)&(annual.curr==1)).sum()); n10=int(((annual.prev==1)&(annual.curr==0)).sum())
    n01=int(((annual.prev==0)&(annual.curr==1)).sum()); n00=int(((annual.prev==0)&(annual.curr==0)).sum())
    m_state=smf.gee("curr ~ prev",groups="node_id",data=annual,family=sm.families.Binomial(),
                    cov_struct=sm.cov_struct.Exchangeable()).fit()
    m_pulse=smf.gee("loss ~ is2016 + middle",groups="node_id",data=pp,family=sm.families.Binomial(),
                    cov_struct=sm.cov_struct.Exchangeable()).fit()
    y16=pp.loc[pp.to_year.eq(2016)]; other=pp.loc[~pp.to_year.eq(2016)]
    mid16=y16.loc[y16.water_body.eq("Middle Tampa Bay")]
    mid0=pp.loc[pp.water_body.eq("Middle Tampa Bay") & ~pp.to_year.eq(2016)]
    pre=pp.loc[pp.to_year.le(2015)]; later=pp.loc[pp.to_year.ge(2017)]
    lost=sorted(y16.loc[y16.loss.eq(1),"node_id"].tolist())
    rec17=annual.loc[annual.node_id.isin(lost)&annual.from_year.eq(2016)&annual.to_year.eq(2017)]
    summary={
      "schema":"tampa.thalassia_transition_memory.v1",
      "source":{"repository":"tbep-tech/obis-example","commit":COMMIT,"event_blob":EVENT_BLOB,
                "occurrence_blob":OCC_BLOB,"years":[int(states.year.min()),int(states.year.max())]},
      "source_audit":audit,
      "annual_transitions":{"n":len(annual),"persistence_1_to_1":n11,"loss_1_to_0":n10,
          "recolonization_0_to_1":n01,"persistent_absence_0_to_0":n00,
          "persistence_probability":n11/(n11+n10),"recolonization_probability":n01/(n01+n00)},
      "state_dependence_gee":{"logit_coef_previous_presence":float(m_state.params["prev"]),
          "odds_ratio":float(math.exp(m_state.params["prev"])),
          "ci95_or":[float(math.exp(x)) for x in m_state.conf_int().loc["prev"]],
          "p_value":float(m_state.pvalues["prev"])},
      "pulse_2016":{"previously_positive_n":len(y16),"losses":int(y16.loss.sum()),
          "loss_rate":float(y16.loss.mean()),"other_years_previous_positive_n":len(other),
          "other_years_losses":int(other.loss.sum()),"other_years_loss_rate":float(other.loss.mean()),
          "risk_ratio":float(y16.loss.mean()/other.loss.mean()),
          "fisher":exact(int(y16.loss.sum()),len(y16)-int(y16.loss.sum()),int(other.loss.sum()),len(other)-int(other.loss.sum())),
          "gee_is2016_logit_coef":float(m_pulse.params["is2016"]),
          "gee_is2016_odds_ratio":float(math.exp(m_pulse.params["is2016"])),
          "gee_is2016_ci95_or":[float(math.exp(x)) for x in m_pulse.conf_int().loc["is2016"]],
          "gee_is2016_p":float(m_pulse.pvalues["is2016"]),
          "gee_middle_logit_coef":float(m_pulse.params["middle"]),"gee_middle_p":float(m_pulse.pvalues["middle"])},
      "middle_tampa_2016":{"previously_positive_n":len(mid16),"losses":int(mid16.loss.sum()),
          "loss_rate":float(mid16.loss.mean()),"other_middle_previous_positive_n":len(mid0),
          "other_middle_losses":int(mid0.loss.sum()),"other_middle_loss_rate":float(mid0.loss.mean()),
          "fisher":exact(int(mid16.loss.sum()),len(mid16)-int(mid16.loss.sum()),int(mid0.loss.sum()),len(mid0)-int(mid0.loss.sum()))},
      "persistence_after_pulse":{"pre_2016_previous_positive_n":len(pre),"pre_2016_losses":int(pre.loss.sum()),
          "pre_2016_loss_rate":float(pre.loss.mean()),"years_2017_2025_previous_positive_n":len(later),
          "years_2017_2025_losses":int(later.loss.sum()),"years_2017_2025_loss_rate":float(later.loss.mean()),
          "fisher":exact(int(later.loss.sum()),len(later)-int(later.loss.sum()),int(pre.loss.sum()),len(pre)-int(pre.loss.sum()))},
      "lost_2016_nodes":lost,"lost_2016_reobserved_positive_2017":int(rec17.curr.sum()),
      "lost_2016_reobserved_2017_n":len(rec17),
      "claim_boundary":{"supported":"strong annual transect-state dependence plus a concentrated 2016 loss pulse followed by rapid reappearance",
        "not_supported":["biomass loss or mortality","a causal temperature/salinity mechanism","a persistent post-2016 regime shift","exact survey-season effects from eventDate"],
        "date_quality_note":"eventDate contains many Dec-25 values; day-of-year is not used in the primary pulse model."}}
    return summary,annual

def write(summary,states,annual,out):
    out=Path(out); out.mkdir(parents=True,exist_ok=True)
    (out/"summary.json").write_text(json.dumps(summary,indent=2)+"\n")
    yr=[]
    for y,g in annual.groupby("to_year"):
        pp=g.loc[g.prev.eq(1)]; pn=g.loc[g.prev.eq(0)]
        yr.append({"to_year":int(y),"annual_pairs":len(g),"previously_positive":len(pp),
                   "losses":int(pp.curr.eq(0).sum()),"loss_rate":float(pp.curr.eq(0).mean()) if len(pp) else None,
                   "previously_negative":len(pn),"recolonizations":int(pn.curr.eq(1).sum()),
                   "recolonization_rate":float(pn.curr.eq(1).mean()) if len(pn) else None})
    pd.DataFrame(yr).to_csv(out/"yearly_transition_rates.csv",index=False)
    lost=set(summary["lost_2016_nodes"])
    states.loc[states.node_id.isin(lost)&states.year.isin([2015,2016,2017]),
               ["node_id","water_body","year","date","label"]].sort_values(["node_id","year"]).to_csv(out/"lost_2016_nodes.csv",index=False)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--out",default="results"); args=ap.parse_args()
    states,audit=reconstruct(); summary,annual=analyse(states,audit); write(summary,states,annual,args.out)
    print(json.dumps(summary,indent=2))

if __name__=="__main__": main()
