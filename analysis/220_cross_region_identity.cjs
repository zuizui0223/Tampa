// Reaggregate two exact-ref source summaries; no new raw observations.
const fs=require('fs'),crypto=require('crypto');
function analyze(t,a){
 const tampa={panel:"Tampa Thalassia 1y, target years 2016–2025",loss:t.registry.exact_point_thalassia_loss_transitions,selective:t.H3b_preexisting_species_persistence.target_occupied_events};
 tampa.bare=tampa.loss-tampa.selective;tampa.fraction=tampa.selective/tampa.loss;
 const panels=["lobster_1y","cucumber_2y"].map(panel=>{
 const taxa=a[panel].map(([code,n,any,same,bare,selective])=>{if(n!==any+bare||any!==same+selective||n<=0||same<0||bare<0||selective<0)throw Error("count closure");return {code,n,any,same,bare,selective,loss:n-same,fraction:n>same?selective/(n-same):null}});
 const total=Object.fromEntries(["n","any","same","bare","selective","loss"].map(k=>[k,taxa.reduce((s,x)=>s+x[k],0)]));
 total.fraction=total.selective/total.loss;
 const q=taxa.filter(x=>x.n>=20&&x.loss>0), loo=taxa.filter(x=>total.loss>x.loss).map(x=>(total.selective-x.selective)/(total.loss-x.loss));
 return {panel,total,taxa,equal_taxon_initial20:q.reduce((s,x)=>s+x.fraction,0)/q.length,range_initial20:[Math.min(...q.map(x=>x.fraction)),Math.max(...q.map(x=>x.fraction))],leave_one_taxon_range:[Math.min(...loo),Math.max(...loo)]};
 });return {tampa,panels,limits:["Secondary reaggregation of already opened source-verified summaries, not a new independent data collection or meta-analysis.","Tampa single focal taxon and repeated meter marks; Torres pooled taxon-by-station transitions, not independent events. Survey units, taxon richness, detectability, geography and lags differ; no regional or lag effect inference.","Conditional masking fraction is not evidence of a mechanism or excess over a richness-controlled null. It does not identify mortality, replacement or functional equivalence."]};
}
const paths=["results/community_insurance_v1.json","results/taxon_habitat_memory_summary_20261127.json"],hashes=["b224670af6e95a0c44bf44c697c315107ebf9902","76fdbf64c435370e65aa38d7a06865510a08d6dd"];
const rows=paths.map((p,i)=>{let b=fs.readFileSync(p);let h=crypto.createHash('sha1').update('blob '+b.length+'\0').update(b).digest('hex');if(h!==hashes[i])throw Error('source drift '+p);return JSON.parse(b)});
const r={source_commit:"19e659ca8d9527fc48b0dccebdda34ee7a6c1835",sources:paths.map((path,i)=>({path,git_blob:hashes[i]})),...analyze(...rows)};
fs.writeFileSync(process.argv[2]||'cross_region_identity.json',JSON.stringify(r,null,2)+'\n');
