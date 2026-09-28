#!/usr/bin/env python3
"""Render Tampa Supplementary Figures S1-S7 from existing analysis outputs.

No ecological model is fit here. The renderer only visualizes already-consumed analyses
and committed canonical results, preserving adverse and null results rather than
selecting favorable subsets.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
plt.rcParams.update({
    "font.family":"sans-serif",
    "font.sans-serif":["Arial","Helvetica","DejaVu Sans"],
    "font.size":8,
    "axes.titlesize":8,
    "axes.labelsize":8,
    "xtick.labelsize":7,
    "ytick.labelsize":7,
    "legend.fontsize":6.5,
    "axes.linewidth":0.6,
    "lines.linewidth":1.0,
    "ps.fonttype":42,
    "pdf.fonttype":42,
})

MARKERS=["o","s","^","D","v","P"]
LINESTYLES=["-","--","-.",":",(0,(5,1)),(0,(3,1,1,1))]
SPECIES=[
    ("Thalassia","Thalassia"),
    ("Halodule","Halodule"),
    ("Syringodium","Syringodium"),
    ("Ruppia","Ruppia"),
]
BAYS=["Old Tampa Bay","Middle Tampa Bay","Lower Tampa Bay","Boca Ciega Bay","Hillsborough Bay"]


def save(fig:plt.Figure,out:Path,number:int):
    stem=f"FigS{number}"
    fig.savefig(out/f"{stem}.eps",format="eps",bbox_inches="tight")
    fig.savefig(out/f"{stem}.tif",format="tiff",dpi=600,bbox_inches="tight")
    fig.savefig(out/f"{stem}_QA.png",format="png",dpi=220,bbox_inches="tight")
    plt.close(fig)


def letter(ax,s):
    ax.text(0,1.02,s,transform=ax.transAxes,ha="left",va="bottom",fontweight="bold",fontsize=8.5)


def fig_s1(primary:Path,out:Path):
    d=pd.read_csv(primary/"community_quant_segment_year.csv")
    fig,axes=plt.subplots(len(BAYS),2,figsize=(7.1,9.6),sharex=True)
    for r,bay in enumerate(BAYS):
        g=d[d["water_body"]==bay].sort_values("year")
        for c,scale in enumerate(["frequency","cover_index"]):
            ax=axes[r,c]
            for i,(prefix,label) in enumerate(SPECIES):
                col=f"{prefix}_{scale}"
                if col not in g.columns:
                    continue
                ax.plot(g["year"],g[col],marker=MARKERS[i],linestyle=LINESTYLES[i],
                        markersize=2.2,label=label)
            if c==0:
                ax.set_ylabel(bay.replace(" Tampa Bay","") + "\nMean frequency")
            else:
                ax.set_ylabel("Mean Braun–Blanquet\nindex")
            if r==0:
                ax.set_title("Frequency" if c==0 else "Braun–Blanquet index")
            ax.grid(alpha=0.15,linewidth=0.4)
            if r==0 and c==1:
                ax.legend(frameon=False,ncol=2)
    axes[-1,0].set_xlabel("Year")
    axes[-1,1].set_xlabel("Year")
    letter(axes[0,0],"a")
    letter(axes[0,1],"b")
    fig.tight_layout(pad=0.8)
    save(fig,out,1)


def fig_s2(primary:Path,out:Path):
    d=pd.read_csv(primary/"early_warning_year_scores.csv")
    p=d.pivot(index="target_year",columns="arm",values="log_loss").reset_index()
    losses=d[d["arm"]=="baseline"][["target_year","losses"]].drop_duplicates()
    fig,axes=plt.subplots(2,1,figsize=(7.1,5.3),sharex=True,
                         gridspec_kw={"height_ratios":[2.1,1.0]})
    ax=axes[0]
    ax.plot(p["target_year"],p["baseline"],marker="o",markersize=2.5,label="Baseline")
    ax.plot(p["target_year"],p["quantitative"],marker="s",markersize=2.5,linestyle="--",
            label="+ quantitative state")
    ax.axvline(2016,color="0.5",linestyle=":",linewidth=0.8)
    ax.set_ylabel("Target-year log loss")
    ax.legend(frameon=False)
    ax.grid(alpha=0.15,linewidth=0.4)
    letter(ax,"a")
    ax=axes[1]
    ax.bar(losses["target_year"],losses["losses"],width=0.8,facecolor="white",edgecolor="black")
    ax.axvline(2016,color="0.5",linestyle=":",linewidth=0.8)
    ax.set_ylabel("Recorded losses")
    ax.set_xlabel("Target year")
    ax.grid(axis="y",alpha=0.15,linewidth=0.4)
    letter(ax,"b")
    fig.tight_layout(pad=0.8)
    save(fig,out,2)


def fig_s3(site:Path,out:Path):
    files=[
        ("Recorded detection","site_identity_binary_detected_without_node_grid.csv",
         "site_identity_binary_detected_with_node_grid.csv"),
        ("Focal frequency","site_identity_frequency_without_node_grid.csv",
         "site_identity_frequency_with_node_grid.csv"),
        ("Braun–Blanquet","site_identity_cover_index_without_node_grid.csv",
         "site_identity_cover_index_with_node_grid.csv"),
    ]
    fig,axes=plt.subplots(1,2,figsize=(7.1,3.0),sharey=True)
    for ax,(ref,title) in zip(axes,[("without","Without stable node identity"),
                                   ("with","With stable node identity")]):
        for i,(label,no_file,yes_file) in enumerate(files):
            d=pd.read_csv(site/(no_file if ref=="without" else yes_file))
            y=d["mean_history_minus_lag1"].to_numpy(float)
            x=d["tau_years"].to_numpy(float)
            ax.plot(x,y,marker=MARKERS[i],linestyle=LINESTYLES[i],markersize=3,label=label)
            supported=d["support_rule_passed"].astype(bool).to_numpy()
            if supported.any():
                ax.scatter(x[supported],y[supported],s=32,facecolors="none",
                           edgecolors=f"C{i}",linewidths=1.0)
        ax.axhline(0,color="0.5",linestyle="--",linewidth=0.7)
        ax.set_xscale("log")
        ax.set_xlabel("History decay scale, τ (years)")
        ax.set_title(title)
        ax.grid(alpha=0.15,linewidth=0.4)
    axes[0].set_ylabel("Mean score difference\n(history − lag-1; negative is better)")
    axes[0].legend(frameon=False)
    letter(axes[0],"a"); letter(axes[1],"b")
    fig.tight_layout(pad=0.8)
    save(fig,out,3)


def fig_s4(out:Path):
    cv=json.loads((ROOT/"results/current_validation_v2.json").read_text())
    rows=[
        ("Thresholding only",cv["threshold_induced_memory_known_truth"]),
        ("Slow suitability + fast condition",cv["two_timescale_hidden_state_memory_known_truth"]),
        ("Latent occupancy + imperfect detection",cv["latent_occupancy_detection_memory_known_truth"]),
    ]
    labels=[]; observed=[]; required=[]
    for label,z in rows:
        labels.append(label)
        observed.append(z["supporting_cells"]/z["cells"])
        required.append(z["required_supporting_cells"]/z["cells"])
    y=np.arange(len(labels))
    fig,ax=plt.subplots(figsize=(7.1,2.7))
    ax.barh(y-0.17,observed,height=0.30,facecolor="white",edgecolor="black",hatch="//",label="Observed supporting-cell fraction")
    ax.barh(y+0.17,required,height=0.30,facecolor="white",edgecolor="0.5",hatch="..",label="Frozen required fraction")
    ax.set_yticks(y,labels)
    ax.invert_yaxis()
    ax.set_xlim(0,1)
    ax.set_xlabel("Fraction of parameter cells")
    ax.legend(frameon=False,loc="lower right")
    ax.grid(axis="x",alpha=0.15,linewidth=0.4)
    fig.tight_layout(pad=0.8)
    save(fig,out,4)


def fig_s5(primary:Path,out:Path):
    annual=pd.read_csv(primary/"environment_coupling_tests.csv")
    annual=annual[annual["period"]=="post2016_2017_2025"].copy()
    seasonal=pd.read_csv(primary/"seasonal_stress_tests.csv")
    seasonal=seasonal[seasonal["period"]=="post2016_target_2017_2025"].copy()

    fig,axes=plt.subplots(1,2,figsize=(7.1,3.25))
    ax=axes[0]
    annual=annual.sort_values(["outcome","exposure_mode","environment"]).reset_index(drop=True)
    x=np.arange(len(annual))
    vals=-np.log10(np.clip(annual["q_within_outcome_mode"].to_numpy(float),1e-12,1))
    ax.scatter(x,vals,s=18,facecolors="white",edgecolors="black")
    ax.axhline(-np.log10(0.05),color="0.5",linestyle="--",linewidth=0.7)
    ax.set_ylabel("−log10(FDR q)")
    ax.set_xlabel("Declared annual tests")
    ax.set_xticks([])
    ax.grid(axis="y",alpha=0.15,linewidth=0.4)
    letter(ax,"a")

    ax=axes[1]
    seasonal=seasonal.sort_values(["outcome","window_months","exposure"]).reset_index(drop=True)
    x=np.arange(len(seasonal))
    vals=-np.log10(np.clip(seasonal["q_family_bh"].to_numpy(float),1e-12,1))
    labels=[f"{r.outcome.replace('Thalassia_','')}\n{r.exposure}\n{int(r.window_months)} m"
            for r in seasonal.itertuples()]
    ax.scatter(x,vals,s=22,facecolors="white",edgecolors="black")
    ax.axhline(-np.log10(0.05),color="0.5",linestyle="--",linewidth=0.7)
    ax.set_ylabel("−log10(FDR q)")
    ax.set_xticks(x,labels,rotation=70,ha="right",fontsize=5.8)
    ax.set_xlabel("Predeclared seasonal tests")
    ax.grid(axis="y",alpha=0.15,linewidth=0.4)
    letter(ax,"b")
    fig.tight_layout(pad=0.8)
    save(fig,out,5)


def fig_s6(dynamic:Path,out:Path):
    x=json.loads((dynamic/"dynamic_neighborhood_state_v1.json").read_text())
    fig,axes=plt.subplots(1,2,figsize=(7.1,3.0),sharey=True)
    for ax,(key,title) in zip(axes,[("frequency","Focal frequency"),("cover_index","Braun–Blanquet")]):
        rows=x["results"][key]["sensitivity"]["radius_results"]
        r=np.array([z["radius_km"] for z in rows],dtype=float)
        seg=np.array([z["segment_increment"]["mean_delta"] for z in rows],dtype=float)
        loc=np.array([z["local_increment"]["mean_delta"] for z in rows],dtype=float)
        ax.axhline(0,color="0.5",linestyle="--",linewidth=0.7)
        ax.plot(r,seg,marker="o",label="+ segment state")
        ax.plot(r,loc,marker="s",linestyle="--",label="+ local residual")
        ax.set_xlabel("Frozen EOG radius (km)")
        ax.set_title(title)
        ax.grid(alpha=0.15,linewidth=0.4)
    axes[0].set_ylabel("Mean MAE increment\n(candidate − reference)")
    axes[0].legend(frameon=False)
    letter(axes[0],"a"); letter(axes[1],"b")
    fig.tight_layout(pad=0.8)
    save(fig,out,6)


def fig_s7(compound:Path,out:Path):
    d=pd.read_csv(compound/"compound_hotfresh_segment_year.csv")
    mapping={"tempcnt":"Hot ≥30 °C","salicnt":"Fresh ≤25 ppt","bothcnt":"Joint hot–fresh"}
    fig,axes=plt.subplots(2,2,figsize=(7.1,5.3),sharex=True,sharey=True)
    for ax,bay in zip(axes.ravel(),["OTB","HB","MTB","LTB"]):
        g=d[d["bay_segment"]==bay]
        for i,(raw,label) in enumerate(mapping.items()):
            z=g[g["stress_type"]==raw].sort_values("trnyr")
            ax.plot(z["trnyr"],z["mean_max_run_days"],marker=MARKERS[i],
                    linestyle=LINESTYLES[i],markersize=2.5,label=label)
        ax.set_title(bay)
        ax.grid(alpha=0.15,linewidth=0.4)
    axes[0,0].set_ylabel("Mean station maximum\nconsecutive run (days)")
    axes[1,0].set_ylabel("Mean station maximum\nconsecutive run (days)")
    axes[1,0].set_xlabel("Transect year")
    axes[1,1].set_xlabel("Transect year")
    axes[0,1].legend(frameon=False)
    for i,ax in enumerate(axes.ravel()):
        letter(ax,chr(ord("a")+i))
    fig.tight_layout(pad=0.8)
    save(fig,out,7)


def main(primary:Path,site:Path,dynamic:Path,compound:Path,out:Path):
    out.mkdir(parents=True,exist_ok=True)
    fig_s1(primary,out)
    fig_s2(primary,out)
    fig_s3(site,out)
    fig_s4(out)
    fig_s5(primary,out)
    fig_s6(dynamic,out)
    fig_s7(compound,out)


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--primary",type=Path,required=True)
    p.add_argument("--site",type=Path,required=True)
    p.add_argument("--dynamic",type=Path,required=True)
    p.add_argument("--compound",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    main(a.primary,a.site,a.dynamic,a.compound,a.out)
