function analyze(src){
 const [d,r,...goose]=src;
 const rr=(a,b)=>a/b;
 const k=rr(d.seed.inside,d.seed.outside),h=rr(d.shoot.inside,d.shoot.outside),share=k/(1+k),observed=d.seedling.inside/(d.seedling.inside+d.seedling.outside);
 const areas=[.01,.05,.1,.2,.3,.5];
 // A: constant outside density (requires new input, net retention or some other source).
 // B: redistribution only, fixed total stock, solve the two-component mass balance.
 const scenarios=areas.map(f=>({f,stock_ratio_constant_outside:1+f*(k-1),outside_density_ratio_fixed_stock:1/(1+f*(k-1)),pit_density_ratio_fixed_stock:k/(1+f*(k-1)),seed_share_in_pits:f*k/(1+f*(k-1)),shoot_ratio_constant_outside:1+f*(h-1),establishment_multiplier_pits_needed_if_other_areas_penalized_20pct:(1-.8*(1-f))/(f*k)}));
 // With complete mixing / redistribution only, per-seed success ratio q relative to outside.
 // If per-seed success is equal, concentrating seeds produces no gain in total recruitment.
 const rrGrid=areas.map(f=>({f,scenario:[.5,1,1.5,2].map(q=>({q,recruit_ratio_fixed_seed_stock:(1-f+f*k*q)/(1-f+f*k)}))}));
 const sites=goose.slice(0,2).map(s=>{const c=s.center,e=s.edge;return {system:s.system,center_ratio:c.inside/c.outside,edge_ratio:e.inside/e.outside,center_difference:c.inside-c.outside,edge_difference:e.inside-e.outside,ratio_of_ratios:(e.inside/e.outside)/(c.inside/c.outside),difference_of_differences:(e.inside-e.outside)-(c.inside-c.outside),edge_pit_vs_center_pit:e.inside/c.inside}});
 const g=goose[2];let pooled=Object.fromEntries(["center","edge"].map(n=>[n,{pit_vs_sham_ratio:g[n].pit/g[n].sham,pit_vs_sham_difference:g[n].pit-g[n].sham,pit_vs_untouched_ratio:g[n].pit/g[n].untouched,pit_vs_untouched_difference:g[n].pit-g[n].untouched}]));
 if(Math.abs(scenarios[2].outside_density_ratio_fixed_stock*(1-.1)+scenarios[2].pit_density_ratio_fixed_stock*.1-1)>1e-12)throw Error("closure");
 if(rrGrid.some(s=>Math.abs(s.scenario[1].recruit_ratio_fixed_seed_stock-1)>1e-12))throw Error("neutral establishment closure");
 return {source:src,dugong:{seed_ratio:k,shoot_ratio:h,seed_per_standing_shoot_ratio:k/h,seedling_share_in_trails:observed,expected_share_equal_sampled_area:share,relative_seedling_per_seed:(d.seedling.inside/d.seedling.outside)/k,scenarios,rrGrid},stingray:{seed_ratio:r.seed.inside/r.seed.outside},goose:{sites,pooled,edge_vs_center_pit_sham_ratio_of_ratios:pooled.edge.pit_vs_sham_ratio/pooled.center.pit_vs_sham_ratio,edge_vs_center_pit_sham_difference_of_differences:pooled.edge.pit_vs_sham_difference-pooled.center.pit_vs_sham_difference},limits:["Published summary arithmetic, no original replicate-level observations.","Area and survival scenarios hypothetical, no observed pit area or survival rates.","Local seed concentration is not net seed production, seed retention or genet recruitment.","No cross-species pooled effect; no actual otter effect."]};
}
const source=[
  {
    "system": "dugong_Halodule",
    "seed": {
      "inside": 6337,
      "outside": 2218,
      "unit": "per m2"
    },
    "shoot": {
      "inside": 1120,
      "outside": 5465,
      "unit": "per m2"
    },
    "seedling": {
      "inside": 9,
      "outside": 3,
      "unit": "observed count"
    },
    "note": "Inglis 2000 DOI 10.1046/j.1365-2745.2000.00433.x, nine feeding trails, paired adjacent meadow, published means only"
  },
  {
    "system": "stingray_Halodule",
    "seed": {
      "inside": 10.1,
      "outside": 12.9,
      "unit": "per core"
    },
    "note": "Same Inglis paper; 20 paired observations, paired t=-0.98 p=.34; low power, not equivalence"
  },
  {
    "system": "goose_pit_Vogelkoje",
    "center": {
      "inside": 5.75,
      "outside": 3.7
    },
    "edge": {
      "inside": 9.25,
      "outside": 0.5
    },
    "note": "Zipperle et al. 2010 DOI 10.1016/j.aquabot.2010.05.002; thesis ch5 p126 site-specific reported means; surrounding meadow comparisons"
  },
  {
    "system": "goose_pit_Leghoern",
    "center": {
      "inside": 3.13,
      "outside": 2.6
    },
    "edge": {
      "inside": 1.38,
      "outside": 0.2
    },
    "note": "Same study; not independent article"
  },
  {
    "system": "goose_pit_pooled",
    "center": {
      "pit": 4.4,
      "sham": 2.4,
      "untouched": 1.4
    },
    "edge": {
      "pit": 5.3,
      "sham": 1.9,
      "untouched": 0.4
    },
    "note": "Same experiment pooled across two meadows. Use Results not ambiguous abstract punctuation."
  }
];
if(require.main===module){const out=analyze(source);const fs=require('fs');if(process.argv[2])fs.writeFileSync(process.argv[2],JSON.stringify(out,null,2)+'\n');else console.log(JSON.stringify(out,null,2));}
module.exports=analyze;
