#!/usr/bin/env python3
"""Original-source pollination stage diagnostics; no individual fruit linkage in apple."""
import argparse, hashlib, json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import rankdata

FILES={
 "apple_2020/survival-data.csv":"7e90f246071cee42bbad5505cf2308c52db5f11fefc6546db2e9128bede1ad3a",
 "apple_2020/fruit-set.csv":"654eb061f11e4ba0540183aaab5a438a1ee959074659641deea95722330b780c",
 "apple_2020/seed-count.csv":"292536e1072259368f954cd15791213fa2d22f5a3f257c4d6d96e9547f4113c1",
 "gallagher_2020/gallagher&campbell_pollinatorEffectivenessData.xlsx":"bbfcbbaf43b53b0ef835b891bd8932ae3761a383e4ecb1f38440a4ba9d477c38"}
def verified(root,name):
    p=root/name
    if hashlib.sha256(p.read_bytes()).hexdigest()!=FILES[name]:raise ValueError("source drift "+name)
    return p
def flower_summary(g):
    return {"flowers":len(g),"pollen_positive":int((g.TotPollen>0).sum()),"top_positive":int((g.PTT>0).sum()),"mid_positive":int((g.PTM>0).sum()),"base_positive":int((g.PTB>0).sum()),
        "positive_pollen_base_zero":int(((g.TotPollen>0)&(g.PTB==0)).sum()),"mean_pollen":float(g.TotPollen.mean()),"mean_base_tubes":float(g.PTB.mean())}
def apple(root):
    s=pd.read_csv(verified(root,"apple_2020/survival-data.csv"));s["number of visits"]=s["number of visits"].fillna(-1)
    k=["year","farm","flower stigma","stigma ID","treatment","number of visits"]
    stages=["TotPollen","PTT","PTM","PTB"]
    assert len(s)==1948 and not s.duplicated(k+["variable"]).any() and set(s.variable)==set(stages)
    p=s.pivot(index=k,columns="variable",values="pollen value").reset_index()
    assert len(p)==487 and not p[stages].isna().any().any() and (p[stages]>=0).all().all()
    fk=[c for c in k if c!="stigma ID"]
    f=p.groupby(fk).agg(styles=("stigma ID","size"),**{v:(v,"sum") for v in stages}).reset_index()
    assert len(f)==105
    g=f[f.treatment=="Visited"]
    groups={str(t):flower_summary(v) for t,v in f.groupby("treatment")}
    by_dose={str(int(t)):flower_summary(v) for t,v in g.groupby("number of visits")}
    def thresholds(v):
        return {str(n):{"flowers":int((v.TotPollen>=n).sum()),"base_zero":int(((v.TotPollen>=n)&(v.PTB==0)).sum())} for n in (1,10,50,100,200,500,1000)}
    a=pd.read_csv(verified(root,"apple_2020/fruit-set.csv"));b=pd.read_csv(verified(root,"apple_2020/seed-count.csv"))
    assert len(a)==1357 and len(b)==1646
    assert set(a.initial)==set(a.final)=={0,1}
    fruit={}
    for t,v in a.groupby("Treatment"):
        fruit[t]={"rows":len(v),"initial_positive":int(v.initial.sum()),"final_positive":int(v.final.sum()),"final_positive_initial_zero":int((v.final>v.initial).sum())}
    one=a[(a.Treatment=="V")&(a["number of visits"]==1)]
    bs=b[(b.treatment=="v")&(b["no of visits"]==1)]
    return {"study_doi":"10.1038/s41598-020-73637-5","style_rows":len(p),"flower_contexts":len(f),"style_counts_per_flower":{str(k):int(v) for k,v in f.styles.value_counts().items()},"nonmonotonic_style_counts":int(((p.PTT>p.TotPollen)|(p.PTM>p.PTT)|(p.PTB>p.PTM)).sum()),"base_positive_mid_zero_flowers":int(((f.PTB>0)&(f.PTM==0)).sum()),"treatment":groups,"visited_dose":by_dose,"visited_pollen_thresholds":thresholds(g),"visited_exactly_five_recorded_styles":thresholds(g[g.styles==5]),"visited_by_year":{str(k):thresholds(v) for k,v in g.groupby("year")},"fruit_treatments":fruit,"one_visit_fruit_rows":len(one),"one_visit_initial":int(one.initial.sum()),"one_visit_final":int(one.final.sum()),"one_visit_seed_rows":len(bs),"one_visit_positive_seed_rows":int((bs.seeds>0).sum()),"fruit_final_exceeds_initial_rows":int((a.final>a.initial).sum()),"seed_count_above_ten_rows":int((b.seeds>10).sum()),"limits":["Four spatial count measurements on each recorded style, not tagged grains or individual developmental trajectories. Flower key is year/farm/flower number/treatment/visit count; variable numbers of observed styles including six. No repair of nonmonotonic counts.","Fruit/seed experiments use other flowers; no row-level join of microscopy to fruit/seed or assumed survival curve. Fruit table has no individual identifiers for verification; final-positive initial-zero records retained. Threshold 100 grains is descriptive posthoc, not a biological threshold."]}

def gallagher(root):
    path=verified(root,"gallagher_2020/gallagher&campbell_pollinatorEffectivenessData.xlsx")
    a,b,c=[pd.read_excel(path,sheet_name=i) for i in range(3)]
    assert [len(x) for x in (a,b,c)]==[232,62,232] and all(x.plantID.is_unique for x in (a,b,c))
    key=["week","plantID","site","treat","visID"]
    j=a.merge(b,on=key,suffixes=("","_source"),validate="one_to_one")
    assert len(j)==62 and a.polDepMC.notna().sum()==62
    for k in ("polDepMC","polDepNonMC"):assert np.allclose(j[k],j[k+"_source"],equal_nan=True)
    j=a.merge(c,on="plantID",suffixes=("_a","_c"),validate="one_to_one")
    for k in ("week","site","treat","seedCnt","seedPerFlr","FlrsAvail","noFlrs"):
        assert j[k+"_a"].equals(j[k+"_c"]) or np.all(j[k+"_a"].to_numpy()==j[k+"_c"].to_numpy())
    v=a[a.treat=="V"];z=v[v.polDepMC.notna()].copy()
    assert len(v)==94 and len(z)==47 and (z.polDepMC>0).all()
    assert np.allclose(v.seedCnt/v.noFlrs,v.seedPerFlr) and (v.noFlrs>0).all()
    group=[]
    for (site,tax),g in z.groupby(["site","visID"]):
        group.append({"site":site,"visitor":tax,"ramets":len(g),"mean_conspecific_pollen":float(g.polDepMC.mean()),"mean_seed_per_flower":float(g.seedPerFlr.mean()),"zero_seed_ramets":int((g.seedCnt==0).sum())})
    blocks=[]
    for _,g in z.groupby(["site","visID"]):
        x,y=rankdata(g.polDepMC),rankdata(g.seedPerFlr)
        blocks.append((x-x.mean(),y-y.mean()))
    den=np.sqrt(sum(x@x for x,y in blocks)*sum(y@y for x,y in blocks))
    obs=sum(x@y for x,y in blocks)/den
    rng=np.random.default_rng(20261124);B=9999
    null=np.array([sum(x@rng.permutation(y) for x,y in blocks)/den for _ in range(B)])
    return {"study_doi":"10.1002/ajb2.1439","ramets":len(a),"visited_ramets":len(v),"pollen_and_seed_visited_ramets":len(z),"zero_seed_with_conspecific_pollen":int((z.seedCnt==0).sum()),"pollen_sheet_matches":62,"seed_sheet_matches":232,"visitor_label_mismatches":int((j.visID_a!=j.visID_c).sum()),"zero_flower_bagged_records":int((a.noFlrs==0).sum()),"poll_observation_year_labels":[int(x) for x in a["colDate.PolObs"].dt.year.unique()],"matched_groups":group,"centered_within_site_visitor_rank_correlation":float(obs),"permutation_n":B,"two_sided_permutation_p":float((1+(np.abs(null)>=abs(obs)-1e-12).sum())/(B+1)),"null_interval":np.quantile(null,[.025,.975]).tolist(),"limits":["Marked flowers on a ramet may receive different visits in detail; reported pollen and seed endpoints are ramet aggregates, not uniquely matched pollen grains and seed fates. Group labels observational within single-visit trials, not random assignment of visitor species.","Only pollen-measured visited subset. Rank diagnostic centers ranks within site and visitor guild and permutes seed ranks within strata; exploratory exchangeability assumption, not a causal test. No additional adjustment or claim of equivalence.","Publication/sheet indicate 2016 single-visit experiment but combined table observation date labels are 2017; no year-effect inference. Retain source site labels and consolidated visitor taxonomy; seed sheet label differences not used to infer taxa."]}
def analyze(root):
    return {"status":"two_source_paired_stage_diagnostics_not_meta_analysis","source_hashes":FILES,"apple":apple(root),"gallagher":gallagher(root)}
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--root",type=Path,default=Path("cross_system_sources"));a=p.parse_args()
    print(json.dumps(analyze(a.root),indent=2,sort_keys=True,allow_nan=False))
