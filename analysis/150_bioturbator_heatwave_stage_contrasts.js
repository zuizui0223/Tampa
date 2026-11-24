#!/usr/bin/env node
// Source: https://github.com/SimonaLaukaityte/heatwave-on-animal-plant-interactions/blob/ea4679016e8bddcd083cd93fe2fd6f33b6b1025e/data.txt
// node analysis/150_bioturbator_heatwave_stage_contrasts.js data.txt
const fs=require("node:fs"),crypto=require("node:crypto");
const b=fs.readFileSync(process.argv[2]);
const hash=crypto.createHash("sha1").update("blob "+b.length+"\0").update(b).digest("hex");
if(hash!=="cb12f65a477078f3980a381b5251a635db312d53")throw Error("Git blob mismatch "+hash);
function analyze(txt){
 const lines=txt.trim().split(/\r?\n/),h=lines[0].split("\t"),raw=lines.slice(1).map(l=>Object.fromEntries(l.split("\t").map((v,i)=>[h[i],v]))),data=raw.slice(80);
 if(raw.length!==240||data.length!==160||data.some(r=>!["2","3"].includes(r.run)))throw Error("published selection mismatch");
 let groups={};let bad=[];let gt10=0;let seedTotal=0;let germTotal=0;
 for(const r of data){const n=+r.seed_nb, g=+r.germ_nb, a=Array.from({length:6},(_,i)=>+r[`${i}_nb`]),ga=Array.from({length:6},(_,i)=>+r[`${i}_germ_nb`]);if(!(n>0)||a.reduce((x,y)=>x+y,0)!==n||ga.reduce((x,y)=>x+y,0)!==g||a.some((x,i)=>!Number.isInteger(x)||x<0||ga[i]<0||ga[i]>x||!Number.isInteger(ga[i])))bad.push(r["Sample ID"]);
 gt10+=n>10;seedTotal+=n;germTotal+=g;
 const k=[r.run,r.temp,r.block].join("|");const b=groups[k]??={run:r.run,temp:r.temp,block:r.block,fauna:{}};if(b.fauna[r.fauna])throw Error("duplicate");b.fauna[r.fauna]={n,buried:n-a[0],germ:g,deepG:g-ga[0],surf:a[0],surfG:ga[0],id:r["Sample ID"]}}
 const vals=Object.values(groups),names=["NO","COCKLE","SHRIMP","WORM","MIX"],avg=a=>a.reduce((s,x)=>s+x,0)/a.length; if(bad.length||vals.length!==32||vals.some(b=>names.some(s=>!b.fauna[s])))throw Error("schema");
 const metrics={buried:r=>r.buried/r.n,germ:r=>r.germ/r.n,buried_germ:r=>r.deepG/r.n,surface_germ:r=>r.surfG/r.n,germ_per_nominal:r=>r.germ/10};
 let seed=20261124;const rng=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296;};const quant=a=>{a.sort((a,b)=>a-b);return [a[Math.floor(.025*a.length)],a[Math.ceil(.975*a.length)-1]]};
 const result={status:"response-open original-data within-block contrasts, conditional on two runs and four run-temperature baths",counts:{raw_rows:raw.length,selected_rows:data.length,blocks:vals.length,gt_nominal_10:gt10,recovered_seed_records:seedTotal,germinated_seed_records:germTotal,depth_count_failures:bad},group_means:{},contrasts:[],decomposition:[]};
 for(const t of ["COLD","WARM"]){let rr=vals.filter(b=>b.temp===t);result.group_means[t]={};for(const s of names){const a=rr.map(b=>b.fauna[s]);const n=a.reduce((z,r)=>z+r.n,0),bur=a.reduce((z,r)=>z+r.buried,0),g=a.reduce((z,r)=>z+r.germ,0),bg=a.reduce((z,r)=>z+r.deepG,0);result.group_means[t][s]={n_cores:a.length,recovered:n,buried:bur,germinated:g,buried_germinated:bg,mean_core:Object.fromEntries(Object.entries(metrics).map(([m,fn])=>[m,avg(a.map(fn))])),pooled:{buried:bur/n,germ:g/n,conditional_buried_germ:bg/bur,conditional_surface_germ:(g-bg)/(n-bur)}}}
 for(const [s,ref] of [["COCKLE","NO"],["SHRIMP","NO"],["WORM","NO"],["MIX","NO"],["MIX","COCKLE"]]){const byrun=["2","3"].map(r=>rr.filter(b=>b.run===r));if(byrun.some(a=>a.length!==8))throw Error("strata");const row={temp:t,treatment:s,control:ref,metrics:{}};for(const [m,fn] of Object.entries(metrics)){const ds=byrun.map(a=>a.map(b=>fn(b.fauna[s])-fn(b.fauna[ref])));const all=ds.flat();const samples=Array.from({length:20000},()=>avg(ds.map(a=>avg(Array.from({length:a.length},()=>a[Math.floor(rng()*a.length)])))));const strict=rr.filter(b=>b.fauna[s].n<=10&&b.fauna[ref].n<=10);row.metrics[m]={difference:avg(all),conditional_bootstrap95:quant(samples),by_run:ds.map(avg),strict_n:strict.length,strict_diff:strict.length?avg(strict.map(b=>fn(b.fauna[s])-fn(b.fauna[ref]))):null,positive:all.filter(v=>v>1e-10).length,negative:all.filter(v=>v<-1e-10).length}}
 result.contrasts.push(row);
 const a=result.group_means[t][ref].pooled,b=result.group_means[t][s].pooled;const p0=a.buried,p1=b.buried,b0=a.conditional_buried_germ,b1=b.conditional_buried_germ,s0=a.conditional_surface_germ,s1=b.conditional_surface_germ;
 const redistribution=(p1-p0)*((b0+b1-s0-s1)/2),buriedQuality=(b1-b0)*(p0+p1)/2,surfaceQuality=(s1-s0)*(1-(p0+p1)/2);
 if(Math.abs(redistribution+buriedQuality+surfaceQuality-(b.germ-a.germ))>1e-10)throw Error("decomposition");
 result.decomposition.push({temp:t,treatment:s,control:ref,pooled_germ_difference:b.germ-a.germ,redistribution,buried_quality:buriedQuality,surface_quality:surfaceQuality});}}
 return result;
}
const result=analyze(b.toString("utf8"));
result.source={"doi":"10.1007/s00442-025-05662-y","repo":"SimonaLaukaityte/heatwave-on-animal-plant-interactions","commit":"ea4679016e8bddcd083cd93fe2fd6f33b6b1025e","path":"data.txt","blob_sha":"cb12f65a477078f3980a381b5251a635db312d53","author_code_ref":"14286c76bf40a5416060b32e29c9e57f9ec51bd2"};
result.limits=["Rows 81–240 per author code; excluded source run 1 is not treated as another independent run.","34 cores have >10 recovered seed records despite nominal 10 planted; do not model as binomial with nominal n=10 or interpret recovered fractions as per-sown establishment. Germination count per nominal ten is only a scaling sensitivity.","Water bath shared within temperature/run; conditional block bootstrap does not generalize thermal effects beyond two runs.","Burial is post-treatment; arithmetic decomposition is not causal mediation, and no seed survival or emergence after removal was measured.","Recovered-seed germination includes all recovered seed records in denominator; source precomputed germination percentages differ, possibly due to viability denominators. Distinct estimand; not a reproduction of original significance tests.","Exploratory unadjusted comparisons, no evidence of equivalence where interval crosses zero."];
console.log(JSON.stringify(result,null,2));
