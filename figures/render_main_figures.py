#!/usr/bin/env python3
"""Render Tampa manuscript Figures 1–4 from frozen figure-data sidecars.

The renderer performs no model fitting and no endpoint selection. It only reads the
figure-facing CSVs produced by analysis/30_main_figure_data.py and
analysis/31_nps_figure_data.py.
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

STATE_LABELS={
    "recorded_detection":"Recorded detection",
    "focal_frequency":"Focal frequency",
    "braun_blanquet_index":"Braun–Blanquet index",
    "blade_length_mm":"Blade length",
    "shoot_density_m2":"Shoot density",
}

def save(fig:plt.Figure,outdir:Path,stem:str):
    png=outdir/f"{stem}.png"
    svg=outdir/f"{stem}.svg"
    fig.savefig(png,dpi=220,bbox_inches="tight")
    fig.savefig(svg,bbox_inches="tight")
    plt.close(fig)
    return [str(png),str(svg)]

def figure1(primary:Path,outdir:Path):
    nodes=pd.read_csv(primary/"figure1A_tampa_nodes.csv")
    state=pd.read_csv(primary/"figure1B_state_hierarchy.csv")

    fig,axes=plt.subplots(1,2,figsize=(11.2,4.5),gridspec_kw={"width_ratios":[1.0,1.15]})
    ax=axes[0]
    for wb,g in nodes.groupby("water_body",sort=True):
        ax.scatter(g["longitude"],g["latitude"],s=24,label=wb,alpha=0.85)
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_title("A  Stable monitoring transects")
    ax.legend(fontsize=7,frameon=False,loc="upper left",bbox_to_anchor=(0.0,-0.12),ncol=2)
    ax.grid(alpha=0.2)

    ax=axes[1]
    d=state.copy()
    d["label"]=d["state_dimension"].map(STATE_LABELS)
    y=np.arange(len(d))
    h=0.34
    ax.barh(y-h/2,d["stable_node_r2"],height=h,label="Stable transect identity")
    ax.barh(y+h/2,d["year_r2"],height=h,label="Year")
    ax.set_yticks(y,d["label"])
    ax.invert_yaxis()
    ax.set_xlim(0,1)
    ax.set_xlabel("Descriptive $R^2$")
    ax.set_title("B  State dimensions differ in site anchoring")
    ax.legend(fontsize=8,frameon=False)
    for yi,val in enumerate(d["stable_node_r2"].to_numpy(float)):
        ax.text(min(val+0.015,0.97), yi-h/2, f"{val:.2f}", va="center", fontsize=7)
    ax.grid(axis="x",alpha=0.2)
    fig.suptitle("Figure 1. Tampa Bay monitoring resolves a hierarchy of seagrass states",fontsize=12)
    fig.subplots_adjust(bottom=0.20,wspace=0.22)
    return save(fig,outdir,"figure1_state_hierarchy")

def slope_panel(ax,d,state,title,xlabel):
    x=d[d["state"]==state].copy()
    if len(x)==0:
        ax.axis("off"); return
    x=x.sort_values("water_body")
    y=np.arange(len(x))
    err=np.vstack([x["slope"]-x["ci_low"],x["ci_high"]-x["slope"]])
    ax.errorbar(x["slope"],y,xerr=err,fmt="o",capsize=3)
    ax.axvline(0,linewidth=1,linestyle="--")
    ax.set_yticks(y,x["water_body"].str.replace(" Tampa Bay","",regex=False))
    ax.set_xlabel(xlabel)
    ax.set_title(title)
    ax.grid(axis="x",alpha=0.2)

def figure2(primary:Path,outdir:Path):
    slopes=pd.read_csv(primary/"figure2E_canonical_slopes.csv")
    fig,axes=plt.subplots(2,2,figsize=(10.5,7.2))
    slope_panel(axes[0,0],slopes,"recorded_detection","A  Recorded detection","Slope yr$^{-1}$")
    slope_panel(axes[0,1],slopes,"blade_length_mm","B  Blade length","mm yr$^{-1}$")
    slope_panel(axes[1,0],slopes,"shoot_density_m2","C  Shoot density","shoots m$^{-2}$ yr$^{-1}$")
    slope_panel(axes[1,1],slopes,"focal_frequency","D  Within-transect frequency","Slope yr$^{-1}$")
    fig.suptitle("Figure 2. Persistent occurrence conceals bay-specific quantitative degradation",fontsize=12)
    fig.tight_layout()
    return save(fig,outdir,"figure2_bay_specific_degradation")

def figure3(primary:Path,nps:Path,outdir:Path):
    lower=pd.read_csv(primary/"figure3A_lower_tampa_community.csv")
    ext=pd.read_csv(nps/"figure3B_nps_repeated_cover_trajectories.csv")

    fig,axes=plt.subplots(1,2,figsize=(11.4,4.6))
    ax=axes[0]
    for col,label in [
        ("Thalassia_frequency","Thalassia"),
        ("Syringodium_frequency","Syringodium"),
        ("Halodule_frequency","Halodule"),
    ]:
        ax.plot(lower["year"],lower[col],marker="o",label=label)
    ax.set_xlabel("Year")
    ax.set_ylabel("Mean transect frequency")
    ax.set_title("A  Lower Tampa Bay community trajectories")
    ax.legend(frameon=False,fontsize=8)
    ax.grid(alpha=0.2)

    ax=axes[1]
    loc=ext.groupby(["Location","year"],as_index=False)["focal_mean_cover"].mean()
    for name,g in loc.groupby("Location",sort=True):
        ax.plot(g["year"],g["focal_mean_cover"],marker="o",markersize=3,label=name)
    ax.set_xlabel("Year")
    ax.set_ylabel("Mean Zostera cover (%)")
    ax.set_title("B  External NPS Zostera quantitative trajectories")
    ax.legend(frameon=False,fontsize=7)
    ax.text(
        0.5,1.015,
        "Eligible annual units: recorded presence = 1; focal frequency = 1.0 throughout",
        transform=ax.transAxes,fontsize=7,ha="center",va="bottom"
    )
    ax.grid(alpha=0.2)
    fig.suptitle("Figure 3. Quantitative change occurs beneath persistent recorded presence",fontsize=12)
    fig.tight_layout()
    return save(fig,outdir,"figure3_community_and_external_decoupling")

def figure4(primary:Path,outdir:Path):
    d=pd.read_csv(primary/"figure4A_B_source_state_before_outcome.csv")
    ys=pd.read_csv(primary/"figure4C_target_year_logloss_delta.csv")
    fig,axes=plt.subplots(1,3,figsize=(12.3,4.2))

    order=["recorded_persistence","recorded_loss"]
    labels=["Persistence","Loss"]
    data=[d.loc[d["next_year_state"]==k,"focal_frequency"].dropna().to_numpy(float) for k in order]
    axes[0].boxplot(data,tick_labels=["Persistence\n(n=664)","Loss\n(n=24)"],showfliers=False)
    axes[0].set_ylabel("Source-year focal frequency")
    axes[0].set_title("A  Frequency before next-year state")
    axes[0].grid(axis="y",alpha=0.2)

    data=[d.loc[d["next_year_state"]==k,"bb_cover_mean_all_points"].dropna().to_numpy(float) for k in order]
    axes[1].boxplot(data,tick_labels=["Persistence\n(n=664)","Loss\n(n=24)"],showfliers=False)
    axes[1].set_ylabel("Braun–Blanquet all-point index")
    axes[1].set_title("B  Abundance before next-year state")
    axes[1].grid(axis="y",alpha=0.2)

    ax=axes[2]
    ax.axhline(0,linewidth=1,linestyle="--")
    ax.plot(ys["target_year"],ys["quantitative_minus_baseline"],marker="o",linewidth=1)
    row=ys[ys["target_year"]==2016]
    if len(row)==1:
        x=float(row["target_year"].iloc[0]); y=float(row["quantitative_minus_baseline"].iloc[0])
        ax.annotate("2016 adverse",xy=(x,y),xytext=(x+0.8,y),arrowprops={"arrowstyle":"->"},fontsize=8)
    ax.text(0.02,0.03,"Negative Δ = quantitative model better",transform=ax.transAxes,fontsize=7,va="bottom")
    ax.set_xlabel("Target year")
    ax.set_ylabel("Δ log loss\n(quantitative − baseline)")
    ax.set_title("C  Out-of-time predictive increment")
    ax.grid(alpha=0.2)

    fig.suptitle("Figure 4. Quantitative degradation can precede recorded-state instability",fontsize=12)
    fig.tight_layout()
    return save(fig,outdir,"figure4_early_warning")

def main(primary:Path,nps:Path,outdir:Path):
    outdir.mkdir(parents=True,exist_ok=True)
    outputs={}
    outputs["figure1"]=figure1(primary,outdir)
    outputs["figure2"]=figure2(primary,outdir)
    outputs["figure3"]=figure3(primary,nps,outdir)
    outputs["figure4"]=figure4(primary,outdir)
    manifest={
        "schema":"tampa.rendered_main_figures_v1",
        "status":"rendered_from_frozen_figure_data",
        "primary_figure_data":str(primary),
        "external_nps_figure_data":str(nps),
        "outputs":outputs,
        "claim_boundary":[
            "Rendering performs no model fitting or endpoint selection.",
            "Figure 3 NPS panel is post-hoc external ecological replication.",
            "Figure 4 retains adverse target year 2016.",
            "Braun-Blanquet is labelled as an index rather than percent cover."
        ]
    }
    (outdir/"render_manifest_v1.json").write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n")
    print(json.dumps(manifest,indent=2,sort_keys=True))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--primary",type=Path,default=Path("results/generated/figure_data"))
    p.add_argument("--nps",type=Path,default=Path("results/generated_nps_figure/figure_data"))
    p.add_argument("--out",type=Path,default=Path("results/generated_figures"))
    a=p.parse_args(); main(a.primary,a.nps,a.out)
