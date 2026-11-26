function analyze(input){
 const sum=a=>a.reduce((s,v)=>s+v,0),mean=a=>sum(a)/a.length,day=(a,b)=>(Date.parse(b+"T00:00:00Z")-Date.parse(a+"T00:00:00Z"))/86400000;
 const rows=input.map(r=>({...r,lagDays:day(r.peak,r.winter),calculatedPotential:r.shoots*r.pistils*r.fert,bankPerPotential:r.bank/r.potential,logRatio:Math.log(r.bank/r.potential),coatsPerSeed:r.coats/r.bank,excessOverPotential:Math.max(0,r.bank-r.potential),excessShareOfBank:Math.max(0,1-r.potential/r.bank)}));
 const pairs=[["L3F","PH-1"],["TH shallow","TH deep"],["Sambro shallow","Sambro deep"]].map(([a,b])=>{
  let A=rows.find(r=>r.site===a),B=rows.find(r=>r.site===b);
  let p=B.potential/A.potential, q=B.bankPerPotential/A.bankPerPotential, bank=B.bank/A.bank;
  if(Math.abs(p*q-bank)>1e-10)throw Error("ratio closure");
  let days=B.lagDays-A.lagDays,mu=days===0?null:-Math.log(q)/days;
  return {a,b,peakDateDifferenceDays:day(A.peak,B.peak),lagDifferenceDays:days,potentialRatio:p,bankRatio:bank,bankPerPotentialRatio:q,herbivoryDifferencePP:100*(B.herb-A.herb),reproductiveShootRatio:B.shoots/A.shoots,pistilRatio:B.pistils/A.pistils,fertilizationRatio:B.fert/A.fert,impliedCommonHazardPerDay:mu,impliedHalfLifeDays:mu!==null&&mu>0?Math.log(2)/mu:null,bankDifference:B.bank-A.bank};
 });
 const fit=(train,key,constrained=false)=>{
  let my=mean(train.map(r=>r.logRatio));
  if(key===null)return {a:my,b:0,key};
  let mx=mean(train.map(r=>r[key])),ss=sum(train.map(r=>(r[key]-mx)**2));
  let b=ss>1e-12?sum(train.map(r=>(r[key]-mx)*(r.logRatio-my)))/ss:0;
  if(constrained)b=Math.min(0,b);
  return {a:my-b*mx,b,key};
 };
 const cv=(rr,group,key,constrained=false)=>{
  let out=[];
  for(let hold of [...new Set(rr.map(r=>r[group]))]){
    let train=rr.filter(r=>r[group]!==hold);if(train.length<2)throw Error("train too small");
    const model=fit(train,key,constrained);
    for(let r of rr.filter(r=>r[group]===hold)){let lp=model.a+(key===null?0:model.b*r[key]);out.push({site:r.site,group:hold,observed:r.logRatio,predicted:lp,error:lp-r.logRatio,predictedBank:r.potential*Math.exp(lp),slope:model.b});}
  }
  return {rmseLogBank:Math.sqrt(mean(out.map(r=>r.error**2))),maeLogBank:mean(out.map(r=>Math.abs(r.error))),predictions:out};
 };
 const models=[{name:"constant bank/potential ratio",key:null},{name:"peak-to-winter lag",key:"lagDays"},{name:"lag with nonpositive slope",key:"lagDays",constrained:true},{name:"observed spathe herbivory",key:"herb"}];
 const cvResults={};for(let [name,rr] of [["all",rows],["omit_PH1_response_open_sensitivity",rows.filter(r=>r.site!=="PH-1")]]){cvResults[name]={};for(let group of ["site","bay"]){cvResults[name][group]=Object.fromEntries(models.map(m=>[m.name,cv(rr,group,m.key,m.constrained)]));}}
 const fullFits=Object.fromEntries(models.map(m=>[m.name,fit(rows,m.key,m.constrained)]));
 const fiveFits=Object.fromEntries(models.map(m=>[m.name,fit(rows.filter(r=>r.site!=="PH-1"),m.key,m.constrained)]));
 // separate scenario only: treating potential estimate as upper bound on local new-seed input.
 const ph=rows.find(r=>r.site==="PH-1");
 const PH1={bankToPotential:ph.bankPerPotential,excess:ph.excessOverPotential,excessShare:ph.excessShareOfBank,sensitivityPotentialMultiplier:[1,2,3,4].map(k=>({k,minimumUnaccountedStock:Math.max(0,ph.bank-k*ph.potential),share:Math.max(0,1-k*ph.potential/ph.bank)}))};
 return {source:{paper:"10.1016/j.aquabot.2021.103444",tables:"2 and 3; methods 2.4; results 3.3–3.5",url:"https://www.researchgate.net/publication/354307476_Reproductive_ecology_of_Zostera_marina_L_eelgrass_across_varying_environmental_conditions",dataset:"https://open.canada.ca/data/en/dataset/56cfea6f-aeca-47ed-94ab-c519d9e63c91"},status:"Executed published site-mean accounting, not raw cohort data or validated forecast",rows,pairs,cvResults,fullFits,fiveFits,PH1,limits:["Six site means, four parent bays, one year. Peak reproductive shoot density date is NOT first flowering or seed release date. Lag is an observation-window proxy only.","Potential density is a rounded product of peak stock and fertilized pistils, not annual measured release flux. Bank is separate sampled stock including imports or older seeds. Bank/potential ratio is not individual seed retention or survival; PH1 >100% documented by original authors.","Closed-stock excess and common hazard values are conditional arithmetic scenarios, not verified imports, decay rates or predation.","Observed spathe damage not cause-specific seed loss. Seed coats cannot be assigned to current cohort or predation. Spring germination uses a different sampled denominator; no multiplication with winter bank.","Leave-site and leave-bay models use tiny sample and response-open predictors; descriptive predictive diagnostics only, not prospective or independent validation. Omission PH1 based on response is sensitivity only, not primary. No uncertainty from aggregate means or pseudoreplication."]};
}
const input=[
  {
    "site": "L3F",
    "bay": "L3F",
    "peak": "2018-07-09",
    "winter": "2018-11-28",
    "shoots": 107.4,
    "pistils": 241.7,
    "fert": 0.882,
    "herb": 0.0095,
    "potential": 22913,
    "bank": 1546.4,
    "bankSE": 298.8,
    "coats": 909.7,
    "germ": 0.565,
    "germPooled": false
  },
  {
    "site": "PH-1",
    "bay": "PH",
    "peak": "2018-07-12",
    "winter": "2018-12-06",
    "shoots": 0.8,
    "pistils": 108.2,
    "fert": 0.771,
    "herb": 0.1234,
    "potential": 67,
    "bank": 218.3,
    "bankSE": 69,
    "coats": 927.9,
    "germ": 0.667,
    "germPooled": true
  },
  {
    "site": "TH shallow",
    "bay": "TH",
    "peak": "2018-08-02",
    "winter": "2018-12-10",
    "shoots": 5.6,
    "pistils": 102.7,
    "fert": 0.939,
    "herb": 0.0107,
    "potential": 540,
    "bank": 18.2,
    "bankSE": 18.2,
    "coats": 272.9,
    "germ": 0.333,
    "germPooled": true
  },
  {
    "site": "TH deep",
    "bay": "TH",
    "peak": "2018-08-02",
    "winter": "2018-12-10",
    "shoots": 4.4,
    "pistils": 78.8,
    "fert": 0.882,
    "herb": 0.0359,
    "potential": 306,
    "bank": 36.4,
    "bankSE": 23,
    "coats": 1655.6,
    "germ": 0.5,
    "germPooled": true
  },
  {
    "site": "Sambro shallow",
    "bay": "Sambro",
    "peak": "2018-08-09",
    "winter": "2018-12-20",
    "shoots": 23.2,
    "pistils": 89.3,
    "fert": 0.927,
    "herb": 0.0297,
    "potential": 1920,
    "bank": 121.3,
    "bankSE": 46.2,
    "coats": 715.6,
    "germ": 0.05,
    "germPooled": false
  },
  {
    "site": "Sambro deep",
    "bay": "Sambro",
    "peak": "2018-09-17",
    "winter": "2018-12-11",
    "shoots": 9.6,
    "pistils": 126.4,
    "fert": 0.841,
    "herb": 0.0514,
    "potential": 1020,
    "bank": 236.5,
    "bankSE": 124.2,
    "coats": 927.9,
    "germ": 0.213,
    "germPooled": false
  }
];
if(require.main===module){const fs=require('fs'),r=analyze(input);if(process.argv[2])fs.writeFileSync(process.argv[2],JSON.stringify(r,null,2)+'\n');else console.log(JSON.stringify(r,null,2));}
module.exports=analyze;
