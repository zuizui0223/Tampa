function analyze(input){
 const rows=input.holbrook.map(([taxon,stage,n,p,m,sd])=>{
   const ks=Array.from({length:n+1},(_,k)=>k).filter(k=>Math.abs(k/n-p)<=.005+1e-12);if(ks.length!==1)throw Error("incidence count ambiguous");
   const k=ks[0],q=k/n;
   if(!k)return {taxon,stage,n,k,p:q,m:null,sd:null,mean:0,roundedMean:0,mean_rounding:[0,0],sdStatus:"no active feeders",zeroUpper95:1-Math.pow(.05,1/n)};
   const lo=Math.max(0,m-.005),hi=Math.min(1,m+.005);
   const nearest=Math.max(lo,Math.min(.5,hi));
   const maxSD=Math.sqrt(k/(k-1)*nearest*(1-nearest));
   const feasible=sd-.005<=maxSD+1e-12;
   const mean=q*m;
   // Reconstitute sample variance only if reported SD compatible with bounded observations;
   // approximate variance from rounded summaries, not evidence of independent stage cohorts.
   const approxVar=feasible?((k-1)*sd*sd+k*m*m-n*mean*mean)/(n-1):null;
   return {taxon,stage,n,k,p:q,m,sd,mean,roundedMean:p*m,mean_rounding:[q*lo,q*hi],max_possible_active_sample_sd_allowing_rounding:maxSD,sdStatus:feasible?"passes necessary bound only":"incompatible with [0,1] active sample even after rounding",approx_unconditional_se:approxVar===null?null:Math.sqrt(approxVar/n)};
 });
 const compare=(a,b)=>{
   if(a.m===null||b.m===null)return {taxon:a.taxon,from:a.stage,to:b.stage,difference:b.mean-a.mean,components:null,reason:"conditional feeding undefined in zero-active cell"};
   let d=b.mean-a.mean,occ=(b.p-a.p)*(a.m+b.m)/2,mag=(b.m-a.m)*(a.p+b.p)/2;
   if(Math.abs(d-occ-mag)>1e-12)throw Error("closure");
   return {taxon:a.taxon,from:a.stage,to:b.stage,difference:d,occurrence:occ,magnitude:mag,occurrenceShare:d===0?null:occ/d,rounding:[b.mean_rounding[0]-a.mean_rounding[1],b.mean_rounding[1]-a.mean_rounding[0]]};
 };
 const comps=[...new Set(rows.map(r=>r.taxon))].flatMap(t=>{
   const a=rows.filter(r=>r.taxon===t);return [compare(a[0],a[1]),compare(a[1],a[2]),compare(a[0],a[2])];
 });
 const coat=input.castejon.taxa.map(t=>({name:t.name,biteRiskDifference:t.open-t.sealed,biteRiskRatio:t.open/t.sealed,relativeReduction:1-t.sealed/t.open,denominatorStatus:"separate open/sealed n not given; do not reconstruct counts or SE",rounding_sensitivity_if_nearest_tenth:[Math.max(0,t.open-.05)-Math.min(1,t.sealed+.05),Math.min(1,t.open+.05)-Math.max(0,t.sealed-.05)]}));
 const carroll=input.carroll.map(r=>{
   const partial=r.positive-r.all,lo=(10*r.all+partial)/(10*r.positive),hi=(10*r.all+9*partial)/(10*r.positive);
   return {...r,attack:r.positive/r.n,conditional_min:lo,conditional_max:hi,overall_min:lo*r.positive/r.n,overall_max:hi*r.positive/r.n};
 });
 return {status:"Executed published-summary arithmetic; not new raw-data or pooled meta-analysis",rows,comps,coat,mechanics:{open_vs_coat_reduction:1-input.castejon.puncture.open/input.castejon.puncture.coat,seed_vs_leaf_nitrogen:input.castejon.nitrogen.seed/input.castejon.nitrogen.leaf},carroll,limitations:["Holbrook 4-day stage trials: animal-trial counts, not confirmed unique animals across stages; stage dependence and individual covariance unavailable; no stage contrast p-value.","Published Holbrook table and thesis reprint disagree for attached Pugettia conditional mean; use primary article and author-uploaded text .90, not reprint .99, source ambiguity recorded.","Castejon damaged versus wax-sealed cut seeds, endpoint visible bite marks; different groups and stopping times, no actual mortality.","Carroll partial consumption bounds based on known 10 seeds and positive/full-loss animal counts; no common exposure duration or stage, no pooled effect."]};
}
const input={
  "holbrook": [
    [
      "Idotea resecata",
      "attached",
      28,
      0.21,
      0.06,
      0.05
    ],
    [
      "Pugettia producta",
      "attached",
      18,
      0.94,
      0.9,
      0.23
    ],
    [
      "Pachygrapsus crassipes",
      "attached",
      24,
      0.38,
      0.1,
      0.05
    ],
    [
      "Idotea resecata",
      "released",
      28,
      0,
      null,
      null
    ],
    [
      "Pugettia producta",
      "released",
      26,
      0.5,
      0.96,
      0.24
    ],
    [
      "Pachygrapsus crassipes",
      "released",
      25,
      0.36,
      0.69,
      0.4
    ],
    [
      "Idotea resecata",
      "seedling",
      25,
      0,
      null,
      null
    ],
    [
      "Pugettia producta",
      "seedling",
      24,
      0.83,
      0.96,
      0.16
    ],
    [
      "Pachygrapsus crassipes",
      "seedling",
      27,
      0.89,
      0.96,
      0.18
    ]
  ],
  "castejon": {
    "taxa": [
      {
        "name": "Ampithoe ramondi",
        "open": 0.8,
        "sealed": 0.6,
        "leaf": 1,
        "seed_trials_total": 16,
        "leaf_trials": 4
      },
      {
        "name": "Gammarella fucicola",
        "open": 1,
        "sealed": 0.6,
        "leaf": 0.67,
        "seed_trials_total": 14,
        "leaf_trials": 9
      }
    ],
    "puncture": {
      "leaf": 0.94,
      "open": 1.88,
      "coat": 2.21
    },
    "nitrogen": {
      "leaf": 1.14,
      "seed": 1.86
    }
  },
  "carroll": [
    {
      "name": "Dyspanopeus sayi",
      "n": 18,
      "positive": 13,
      "all": 5
    },
    {
      "name": "Pagurus longicarpus",
      "n": 20,
      "positive": 4,
      "all": 3
    }
  ]
};
if(require.main===module){const fs=require('fs'),r=analyze(input);if(process.argv[2])fs.writeFileSync(process.argv[2],JSON.stringify(r,null,2)+'\n');else console.log(JSON.stringify(r,null,2));}
module.exports=analyze;
