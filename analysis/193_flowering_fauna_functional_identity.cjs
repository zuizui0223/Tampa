function analyze(src,traits){
const rows=src.rows,sites=[...new Set(rows.map(r=>r.site))],idx=Object.fromEntries(src.taxa.map((x,i)=>[x,i]));
if(rows.length!==14||sites.length!==5||traits.some(t=>!Object.hasOwn(idx,t.name)))throw Error("source scope");
const sum=a=>a.reduce((x,y)=>x+y,0),mean=a=>sum(a)/a.length;
const eq=(rr,f)=>mean([...new Set(rr.map(r=>r.site))].map(s=>mean(rr.filter(r=>r.site===s).map(f))));
const geo=a=>Math.exp(mean(a.map(Math.log)));
const n=a=>a.length;
const roleIdx=traits.filter(t=>t.localEvidence).map(t=>idx[t.name]),traitIdx=traits.filter(t=>t.traitEvidence).map(t=>idx[t.name]);
const focal=idx.Ampithoe_valida;
const summary=(rr)=>{
 const totalV=eq(rr,r=>r.V),totalF=eq(rr,r=>r.F);
 const per=traits.map(t=>{let i=idx[t.name];let V=eq(rr,r=>r.v[i]),F=eq(rr,r=>r.f[i]),vp=eq(rr,r=>r.v[i]/r.V),fp=eq(rr,r=>r.f[i]/r.F);
 const both=rr.filter(r=>r.v[i]>0&&r.f[i]>0);
 return {name:t.name,V,F,ratio:F/V||null,shareV:vp,shareF:fp,shareDiff:fp-vp,pooledShareV:V/totalV,pooledShareF:F/totalF,pooledShareRatio:(F/totalF)/(V/totalV)||null,shareIncrease:rr.filter(r=>r.f[i]/r.F>r.v[i]/r.V).length,shareDecrease:rr.filter(r=>r.f[i]/r.F<r.v[i]/r.V).length,abundanceIncrease:rr.filter(r=>r.f[i]>r.v[i]).length,abundanceDecrease:rr.filter(r=>r.f[i]<r.v[i]).length,positiveBoth:both.length,bothGeoRatio:both.length?Math.exp(eq(both,r=>Math.log(r.f[i]/r.v[i]))):null,netTotalIncreaseShare:(F-V)/(totalF-totalV)};});
 const roleCoverage={V:eq(rr,r=>sum(roleIdx.map(i=>r.v[i])))/totalV,F:eq(rr,r=>sum(roleIdx.map(i=>r.f[i])))/totalF};
 const movementCoverage={V:eq(rr,r=>sum(traitIdx.map(i=>r.v[i])))/totalV,F:eq(rr,r=>sum(traitIdx.map(i=>r.f[i])))/totalF};
 const partialTrait=(arm)=>{const a=traits.filter(t=>t.traitEvidence).map(t=>({count:eq(rr,r=>r[arm][idx[t.name]]),...t})),tot=sum(a.map(t=>t.count));return {matchedCount:tot,meanMaxLengthMM:sum(a.map(t=>t.count*t.maxLengthMM))/tot,meanMaxWidthMM:sum(a.map(t=>t.count*t.maxWidthMM))/tot,meanUlvaMgDay:sum(a.map(t=>t.count*t.ulvaMgDay))/tot,meanFishPredationDay:sum(a.map(t=>t.count*t.fishPredationDay))/tot,tubeBuilderShare:sum(a.filter(t=>t.movement==="tube building").map(t=>t.count))/tot};};
 return {n:rr.length,totalV,totalF,totalRatio:totalF/totalV,per,roleCoverage,movementCoverage,partialTraits:{V:partialTrait("v"),F:partialTrait("f")}};
};
const paired=rows.map(r=>{let a=r.v[focal],b=r.f[focal],aShare=a/r.V,bShare=b/r.F;
return {site:r.site,month:r.month,totalRatio:r.F/r.V,Aveg:a,Aflower:b,A_ratio:a>0?b/a:null,A_shareVeg:aShare,A_shareFlower:bShare,A_shareDiff:bShare-aShare,A_relativeEnrichment:a>0?(b/r.F)/(a/r.V):null,A_half_threshold:a+b>0?a/(a+b):null,all_half_threshold:r.V/(r.V+r.F),A_positive_both:a>0&&b>0};});
const byMonth=Object.fromEntries([...new Set(rows.map(r=>r.month))].map(m=>[m,summary(rows.filter(r=>r.month===m))]));
const bySite=Object.fromEntries(sites.map(s=>[s,summary(rows.filter(r=>r.site===s))]));
const overall=summary(rows),A=overall.per.find(x=>x.name==="Ampithoe_valida");
const focalScenarios=[.01,.05,.1,.2,.3,.5].map(f=>({f,allAnimalFlowerShare:f*overall.totalF/(f*overall.totalF+(1-f)*overall.totalV),AmpithoeFlowerShare:f*A.F/(f*A.F+(1-f)*A.V)}));
const lab={expt1:{leaf:.07,early:.1,late:.3,spent:.3,looseSeed:.0001,attachedFruit:.09},expt2:{leaf:.1,early:.005,late:.7,macroalga:.6,attachedFruit:.2},bicoastal:{CA_leaf:.3,VA_leaf:.03,CA_late:.5,VA_late:.002,Gracilaria:1.8}};
const ratios={lateEarly1:lab.expt1.late/lab.expt1.early,lateEarly2:lab.expt2.late/lab.expt2.early,lateLeaf1:lab.expt1.late/lab.expt1.leaf,lateLeaf2:lab.expt2.late/lab.expt2.leaf,attachedFruitVsLooseSeed1:lab.expt1.attachedFruit/lab.expt1.looseSeed,CA_VA_leaf:lab.bicoastal.CA_leaf/lab.bicoastal.VA_leaf,CA_VA_late:lab.bicoastal.CA_late/lab.bicoastal.VA_late};
return {status:"Executed cross-source species-label matched descriptive calculation and source-audited laboratory aggregate ratios, not a direct net reproductive effect",sources:{carr:"10.1111/j.1439-0485.2010.00411.x",carr_derived_blob:"77aa45f9230e7ca4167dce19e05d94889824a1aa",carr_derived_commit:"df76c504ab80cbe201dc6806608adc93cb0ec900",reynolds:"10.3354/meps09569",lewis:"10.3390/d6040751",best:"10.3354/meps09678"},traits,overall,byMonth,bySite,paired,leaveOneSiteOut:sites.map(s=>({omitted:s,summary:summary(rows.filter(r=>r.site!==s))})),focalScenarios,lab,ratios,limits:["Species-level labels only, no genus or juvenile trait transfer. Local net biomass effects are context specific; not net reproductive effects. Only A. valida has local direct reproductive consumption evidence in matched categories, unknowns not assumed neutral.","Maximum reported body dimensions are species traits from Bodega Harbor, not observed size distribution in Carr; partial matched-only community composition metrics, not representative whole assemblage.","Bodega Harbor assay rates are not measured SF Bay rates; numerical partial-trait means are standardized indices only, no realized consumption or cascade.","A. valida and total abundance per shoot not encounter probabilities; field and feeding studies overlap region and possibly samples; not independent meta-analysis.","Flowering fractions are scenarios, not observed site-month shoot density. No transfer to Thalassia animal pollination or direct otter benefit.","Zeros in previous ledger are reported/omitted-category bookkeeping, not true absence. Ratio over zero denominator undefined; no pseudocounts."]};
}
const traits=[
  {
    "name": "Ampithoe_valida",
    "localVegetative": "negative (biomass reduction)",
    "localReproductive": "direct consumption of spathes and attached fruits in feeding trials",
    "movement": "tube building",
    "maxLengthMM": 13,
    "maxWidthMM": 4,
    "ulvaMgDay": 2.9,
    "fishPredationDay": 0.9,
    "localEvidence": "10.3354/meps09569; 10.3390/d6040751",
    "traitEvidence": "10.3354/meps09678"
  },
  {
    "name": "Idotea_resecata",
    "localVegetative": "positive biomass; epiphyte removal; induced phenolic defenses against A. valida; also observed leaf grazing",
    "localReproductive": "unmeasured for Zostera marina in local studies",
    "movement": "swimming/clinging",
    "maxLengthMM": 45,
    "maxWidthMM": 8,
    "ulvaMgDay": 5.5,
    "fishPredationDay": 1.3,
    "localEvidence": "10.3390/d6040751",
    "traitEvidence": "10.3354/meps09678"
  },
  {
    "name": "Caprella_cf_drepanochir",
    "localVegetative": "no detected biomass effect in tested mesocosm (not equivalence)",
    "localReproductive": "unmeasured",
    "movement": null,
    "maxLengthMM": null,
    "maxWidthMM": null,
    "ulvaMgDay": null,
    "fishPredationDay": null,
    "localEvidence": "10.3390/d6040751",
    "traitEvidence": null
  },
  {
    "name": "Caprella_californica",
    "localVegetative": "unassigned (Bodega Harbor feeding assays not SF Bay net effect)",
    "localReproductive": "unmeasured",
    "movement": "clinging",
    "maxLengthMM": 30,
    "maxWidthMM": 1,
    "ulvaMgDay": 0.1,
    "fishPredationDay": 2.7,
    "localEvidence": null,
    "traitEvidence": "10.3354/meps09678"
  }
];
if(require.main===module){const fs=require("fs"),crypto=require("crypto");if(process.argv.length!==4)throw Error("usage: node script.cjs source.json output.json");const b=fs.readFileSync(process.argv[2]);const hash=crypto.createHash("sha1").update("blob "+b.length+"\0").update(b).digest("hex");if(hash!=="77aa45f9230e7ca4167dce19e05d94889824a1aa")throw Error("source mismatch");fs.writeFileSync(process.argv[3],JSON.stringify(analyze(JSON.parse(b.toString("utf8")),traits),null,2)+"\n");}
module.exports=analyze;
