function analyze(input,japan,harwell){
 const rows=input.map(r=>({...r,calcP:r.F*r.spadix*r.seedsPerSpadix,PPerF:r.P/r.F,BPerF:r.B/r.F,BPerP:r.B/r.P,developed:r.adultVegFromSeedlings+r.reproFromSeedlings,developedPerRecordedSeedling:(r.adultVegFromSeedlings+r.reproFromSeedlings)/r.seedlingInYear}));
 const contrasts=[2008,2009].map(year=>{
 const a=rows.find(x=>x.year===year&&x.depth==="shallow"),b=rows.find(x=>x.year===year&&x.depth==="deep");
 const r={year,flowers:b.F/a.F,seedPotential:b.P/a.P,bank:b.B/a.B,seedsPerShoot:b.PPerF/a.PPerF,bankPerPotential:b.BPerP/a.BPerP,bankPerFlower:b.BPerF/a.BPerF};
 if(Math.abs(r.flowers*r.seedsPerShoot*r.bankPerPotential-r.bank)>1e-10)throw Error("closure");
 return {...r,logComponents:[Math.log(r.flowers),Math.log(r.seedsPerShoot),Math.log(r.bankPerPotential)],commonYieldPredictionOverstatement:r.flowers/r.seedPotential,commonBankPerFlowerPredictionOverstatement:r.flowers/r.bank};
 });
 const transition=["shallow","deep"].map(depth=>{
 const a=rows.find(x=>x.year===2008&&x.depth===depth),b=rows.find(x=>x.year===2009&&x.depth===depth);return {depth,potential2008:a.P,bank2008:a.B,seedlings2008_09:b.seedlingInYear,developed2009:b.developed,bankOverPotential:a.B/a.P,seedlingOverBank:b.seedlingInYear/a.B,developedOverSeedling:b.developed/b.seedlingInYear,developedOverPotential:b.developed/a.P};});
 const a=transition[0],b=transition[1],ratios={potential:b.potential2008/a.potential2008,bank:b.bank2008/a.bank2008,seedlings:b.seedlings2008_09/a.seedlings2008_09,developed:b.developed2009/a.developed2009};
 const factors={bankPerPotential:b.bankOverPotential/a.bankOverPotential,seedlingPerBank:b.seedlingOverBank/a.seedlingOverBank,developedPerSeedling:b.developedOverSeedling/a.developedOverSeedling};
 if(Math.abs(ratios.potential*Object.values(factors).reduce((x,y)=>x*y,1)-ratios.developed)>1e-9)throw Error("lag closure");
 const ja=japan.annual,jp=japan.perennial,localA=ja.P*ja.authorLocalFraction,localP=jp.P*jp.authorLocalFraction;
 const j={potentialRatio:ja.P/jp.P,tankAnnualFloatDensitySum:ja.tankFloatShoot+ja.tankFloatBranch,tankAnnualFloatShare:(ja.tankFloatShoot+ja.tankFloatBranch)/ja.tankReproductiveDensity,tankAnnualCompleteShare:ja.tankCompleted/ja.tankReproductiveDensity,tankAnnualFateResidual:ja.tankReproductiveDensity-ja.tankFloatShoot-ja.tankFloatBranch-ja.tankCompleted,authorExtrapolatedLocalA:localA,authorExtrapolatedLocalP:localP,localRatio:localA/localP,breakEvenAnnualLocalFraction:localP/ja.P,fieldSeedsPerShoot:[ja.spadix*ja.seedsPerSpadix,jp.spadix*jp.seedsPerSpadix]};
 return {status:"Executed published aggregate stage-ratio comparison and source audit; independent study from Massachusetts, not same-design replication",sources:{korea:"10.3354/meps10899",japan:"10.11233/aquaculturesci.57.531",harwell:"10.1016/S0304-3770(00)00147-9"},rows,contrasts,transition,ratios,factors,japan:{input:japan,...j},harwell:{...harwell,plugInOccupiedTubesPerM2:harwell.tubesPerM2*harwell.occupiedFraction},limits:["Korean potential seed production and peak sediment bank are aggregate estimates and separate samples, not tracked cohort; 2008/09 recruitment matched only to preceding 2008 seed bank as in authors' life table; seedling-to-developed counts derived from monthly quadrat observations, not individually marked seed fates. 2009 potential/seed bank not combined with earlier recruitment. Two years of same two populations, no independent replication or sampling covariance.","Depth and life history confounded in Korean study, no animal manipulation. Source already reports seed output differences and life-cycle strategy; ratio accounting additional, no novel claim of annual/perennial biology.","Japanese field potential production and tank shoot/branch fate are separate experiments; author extrapolated fractions are not direct field seed survival or observed export rates. Different branch/shoot units, rounding, unequal source sediments and separate tanks; do not count tank fragments as independent seeds.","Harwell one observational transect, 70% refers to tubes containing reproductive fragments, not fraction of all drifting fragments captured. Plug-in occupied tube density not causal seed capture or recruitment estimate. No pooled effect, no otter effect."]};
}
const k=[
  {
    "year": 2008,
    "depth": "shallow",
    "type": "perennial",
    "F": 27,
    "spadix": 23,
    "seedsPerSpadix": 9.7,
    "P": 6024,
    "B": 1834,
    "seedlingInYear": 587,
    "adultVegFromSeedlings": 19,
    "reproFromSeedlings": 0
  },
  {
    "year": 2008,
    "depth": "deep",
    "type": "annual",
    "F": 230,
    "spadix": 5.5,
    "seedsPerSpadix": 6.5,
    "P": 8223,
    "B": 2138,
    "seedlingInYear": 891,
    "adultVegFromSeedlings": 17,
    "reproFromSeedlings": 230
  },
  {
    "year": 2009,
    "depth": "shallow",
    "type": "perennial",
    "F": 30,
    "spadix": 22.8,
    "seedsPerSpadix": 10.4,
    "P": 7114,
    "B": 3274,
    "seedlingInYear": 158,
    "adultVegFromSeedlings": 7,
    "reproFromSeedlings": 0
  },
  {
    "year": 2009,
    "depth": "deep",
    "type": "annual",
    "F": 179,
    "spadix": 8.2,
    "seedsPerSpadix": 6.8,
    "P": 9981,
    "B": 3120,
    "seedlingInYear": 603,
    "adultVegFromSeedlings": 7,
    "reproFromSeedlings": 179
  }
],m={
  "annual": {
    "P": 7286,
    "spadix": 10,
    "seedsPerSpadix": 3.6,
    "tankFloatShoot": 88,
    "tankFloatBranch": 60,
    "tankCompleted": 20,
    "tankReproductiveDensity": 168.1,
    "authorLocalFraction": 0.12
  },
  "perennial": {
    "P": 4100,
    "spadix": 12.5,
    "seedsPerSpadix": 4.4,
    "tankFloatShoot": 0,
    "tankFloatBranch": 0,
    "tankReproductiveDensity": 45.4,
    "authorLocalFraction": 1
  }
},h={
  "tubesPerM2": 1.8,
  "occupiedFraction": 0.7,
  "plots": 55,
  "transectLengthM": 100,
  "shootTubeR2": 0.76,
  "seedlingTubeR2": 0.39
};
if(require.main===module){const fs=require('fs'),out=analyze(k,m,h);if(process.argv[2])fs.writeFileSync(process.argv[2],JSON.stringify(out,null,2)+'\n');else console.log(JSON.stringify(out,null,2));}
module.exports=analyze;
