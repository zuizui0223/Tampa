function analyze(metaTxt,popTxt,hapTxt,fastaTxt,subsetTxt){
 const table=(s,sep)=>{let [head,...lines]=s.trim().split(/\r\n|\n|\r/);let h=head.split(sep);return lines.map(l=>{let a=l.split(sep);if(a.length!==h.length)throw Error("field count");return Object.fromEntries(h.map((k,i)=>[k,a[i]]));})};
 const meta=table(metaTxt,","),pop=table(popTxt,"\t").filter(x=>x["Site.Code"]!=="NA");
 if(meta.length!==349||new Set(meta.map(r=>r.ind)).size!==349||meta.some(r=>!["A","B","C"].includes(r.mitoClade)))throw Error("metadata grain");
 const pops=new Map(pop.map(x=>[x["Site.Code"],x]));
 if(pops.size!==pop.length||meta.some(r=>!pops.has(r.pop)))throw Error("pop mismatch");
 const haps=new Map(),hapIDs=new Map();
 for(const line of hapTxt.trim().split(/\r\n|\n|\r/)){let [key,...ids]=line.trim().split(/\s+/);let m=key.match(/^Hap_(\d+)$/);if(!m)throw Error("hap header");let h=+m[1];if(h>47)continue;if(haps.has(h))throw Error("duplicate hap");haps.set(h,ids);for(let id of ids){if(hapIDs.has(id))throw Error("duplicate sequence label "+id);hapIDs.set(id,h)}}
 const seq=new Map();for(const block of fastaTxt.trim().split(">").filter(Boolean)){let [name,...lines]=block.trim().split(/\r\n|\n|\r/);let m=name.match(/^hap(\d+)$/);if(!m||seq.has(+m[1]))throw Error("fasta header");seq.set(+m[1],lines.join("").toUpperCase());}
 if(haps.size!==47||seq.size!==47||new Set([...seq.values()].map(s=>s.length)).size!==1)throw Error("alignment mismatch");
 const clade=h=>h<=12?"A":h<=30?"C":"B"; // numbering matches original author phylogeny.R and table definitions
 const paired=meta.filter(r=>hapIDs.has(r.ind)).map(r=>({...r,hap:hapIDs.get(r.ind),sequenceClade:clade(hapIDs.get(r.ind))}));
 const missing=meta.filter(r=>!hapIDs.has(r.ind)).map(r=>r.ind);
 const mismatch=paired.filter(r=>r.mitoClade!==r.sequenceClade);
 const subset=subsetTxt.trim().split(/\s+/);if(new Set(subset).size!==subset.length||subset.some(id=>!meta.some(r=>r.ind===id)))throw Error("subset identity");
 const valid=paired.filter(r=>r.mitoClade===r.sequenceClade);
 const count=(a,k)=>Object.fromEntries([...new Set(a.map(r=>r[k]))].sort().map(v=>[v,a.filter(r=>r[k]===v).length]));
 const n=sum=>sum.reduce((a,b)=>a+b,0);
 function dist(a,b){let x=seq.get(a),y=seq.get(b),tot=0,d=0;for(let i=0;i<x.length;i++)if("ACGT".includes(x[i])&&"ACGT".includes(y[i])){tot++;d+=+(x[i]!==y[i]);}if(!tot)throw Error("no comparable positions");return d/tot}
 const matrix=new Map([...seq.keys()].flatMap(a=>[...seq.keys()].map(b=>[a+"_"+b,dist(a,b)])));
 function between(a,b){if(!a.length||!b.length)return null;let d=0,cl=0,h=0;for(let x of a)for(let y of b){d+=matrix.get(x.hap+"_"+y.hap);cl+=+(x.sequenceClade===y.sequenceClade);h+=+(x.hap===y.hap)}let N=a.length*b.length;return {meanPDistance:d/N,sameClade:cl/N,sameHaplotype:h/N,n1:a.length,n2:b.length}}
 function within(a){let d=0,h=0,N=0;for(let i=0;i<a.length;i++)for(let j=i+1;j<a.length;j++){d+=matrix.get(a[i].hap+"_"+a[j].hap);h+=+(a[i].hap===a[j].hap);N++}return N?{n:a.length,meanPDistance:d/N,haplotypeDiversity:1-h/N}:null}
 const ps=[...pops.keys()].sort();
 const byPop=Object.fromEntries(ps.map(k=>{const a=meta.filter(r=>r.pop===k),b=valid.filter(r=>r.pop===k),q=pops.get(k),c=count(a,"mitoClade");const reported=Object.fromEntries(["A","B","C"].map(x=>[x,+q["mtDNA."+x]]));return [k,{name:q.Site,region:q.Region,lat:+q.Latitude,lon:+q.Longitude,n:a.length,clade:c,reportedMtDNA:reported,reportedSNP:+q.SNPs,cladeDifference:Object.fromEntries(["A","B","C"].map(x=>[x,(c[x]||0)-reported[x]])),nLinked:b.length,haplotypes:count(b,"hap"),within:within(b)}]}));
 const cross=ps.flatMap((a,i)=>ps.slice(i+1).map(b=>({a,b,...between(valid.filter(r=>r.pop===a),valid.filter(r=>r.pop===b))})));
 const focal=["SFB","EHS","TMB","HUM","WIL","CBV","CHS","SHI","MOU","OSA"];
 const pair=(a,b)=>cross.find(x=>x.a===a&&x.b===b||x.a===b&&x.b===a);
 const comparisons=["EHS","TMB","HUM","WIL","CBV","CHS","SHI","KAE","WAJ","OSA","MNG","MOU","SOU"].map(b=>({target:b,...pair("SFB",b)}));
 const subsetValid=valid.filter(r=>subset.includes(r.ind));
 const sensitivity=["EHS","TMB","HUM","WIL","CBV","SHI","MOU"].map(b=>({target:b,...between(subsetValid.filter(r=>r.pop==="SFB"),subsetValid.filter(r=>r.pop===b))}));
 const cleanComparisons= ["EHS","TMB","HUM","CBV","SHI","MOU"].map(b=>({target:b,...between(valid.filter(r=>r.pop==="SFB"&&r.mitoClade==="B"),valid.filter(r=>r.pop===b))}));
 // Conditional potential pre-release loss model, not fitted.
 // Assume initial standing fruit stock S, constant amphipod density A, reported potential count removal rate c;
 // compare a pulse release at day T with an exponential release time of mean T and a constant per-fruit hazard lambda=c*A/S.
 // No additional seeds, predators, or postrelease loss. Hazard model calibrates initial rate only.
 const budgets=[];for(const S of [250,500])for(const A of [1300,3200])for(const c of [.01,.025])for(const T of [7,14,21]){
   let x=c*A*T/S;budgets.push({S,A,c,T,potentialDemandRatio:x,constantRemovalPulseRemaining:Math.max(0,1-x),constantHazardPulseReleased:Math.exp(-x),exponentialReleaseFraction:1/(1+x),densityFor90PctRelease_exp:S/(9*c*T),requiredDensityReduction90Pct_exp:Math.max(0,1-1/(9*x))});}
 return {source:{repo:"esotka/AmpithoeValida",commit:"0302f9d7fd2c7b6f067432a1e290c6e4ceff3143",paper:"10.1007/s10592-022-01452-8",feedingSource:"10.3354/meps09569"},audit:{metaN:meta.length,linked:paired.length,valid:valid.length,missing,mismatch,hapN:haps.size,sequenceLength:[...seq.values()][0].length,sequenceAlphabet:[...new Set([...seq.values()].join(""))].sort(),hapAssignmentCount:hapIDs.size,subsetN:subset.length,subsetLinked:subsetValid.length},byPop,cross,comparisons,sensitivity,cleanComparisons,budgets,limits:["Original deposited mitochondrial sequence/individual metadata linked by exact IDs. Clade labels from source hap numbering and author tree; no nuclear genotype inference. Sample composition not population prevalence or contemporary density.","Paper Table2 population summary and individual metadata differ in some cells/coverage; keep separate, do not reconcile or join historical accession counts to modern samples. Exclude metadata/sequence mismatches from paired sequence analysis only if found; report missing and mismatch.","Pairwise mean uncorrected p-distance on ACGT overlap; cross-pairs not independent observations, no p-values or confidence intervals; 261-subset sensitivity not independent replication.","San Francisco Bay feeding trials and genetics are different sampling dates/locations; no genotype-linked food choice, fruit survival, otter treatment or direct causal hybrid effect.","Reproductive budget is an illustrative alternative to published constant-removal extrapolation, not a fitted field model. Lab rates and field density maxima from Reynolds 2012; stock 250 observed, 500 source discussion alternative; time and release distribution assumed. No actual phenology, recruitment or threshold recommendation."]};
}
const expected=["821fed44640394da53d3ac36b45efe78239ca6fe","1f4c14916820b37c86e2373f176d518c99a54702","4e36f3df1249053541e5afa07ff281975dce0a23","4a7f8477fab878cfd82962484e08c2742aaab8e7","f390c4ddcc7e8a8da8ad46c53ee2712ea303a55f"];
if(require.main===module){const fs=require("fs"),crypto=require("crypto");if(process.argv.length!==8)throw Error("usage: node script.cjs meta_inds.txt meta_pop.txt duplicates.txt COI.fst inds261 output.json");let inputs=process.argv.slice(2,7).map((p,i)=>{let b=fs.readFileSync(p);let hash=crypto.createHash("sha1").update("blob "+b.length+"\0").update(b).digest("hex");if(hash!==expected[i])throw Error("source blob mismatch "+p);return b.toString("utf8")});fs.writeFileSync(process.argv[7],JSON.stringify(analyze(...inputs),null,2)+"\n");}
module.exports=analyze;
