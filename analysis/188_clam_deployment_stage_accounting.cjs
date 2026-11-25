function analyze(csv) {
const [header,...lines]=csv.replace(/^\uFEFF/,"").trim().split(/\r?\n/);
if(header!=="date,plot_id,seed_density,burial_treatment,clam_code,shoot_count,length_cm_1,length_cm_2,length_cm_3,length_cm_4,length_cm_5")throw Error("unexpected schema");
const rows=lines.map(x=>{const [date,id,dose,b,clam,S,...len]=x.split(",");if(!/^\d+$/.test(S)||!["0","1"].includes(b))throw Error("count or treatment");return {date,id:+id,dose:+dose,b:+b,clam,S:+S}});
const dates=[...new Set(rows.map(r=>r.date))].sort((a,b)=>Date.parse(a)-Date.parse(b));
const keys=new Set(rows.map(r=>r.date+"_"+r.id));
if(rows.length!==760||keys.size!==760||dates.length!==10)throw Error("grain changed");
const byDate=Object.fromEntries(dates.map(d=>[d,rows.filter(r=>r.date===d).length]));
const full=dates.filter(d=>byDate[d]===80);
if(full.length!==9||full.at(-1)!=="17-Apr-26"||!full.includes("17-Dec-25"))throw Error("window changed");
const early=full.indexOf("17-Dec-25"),n=full.length;
const plots=Array.from({length:80},(_,i)=>{let id=i+1,rs=full.map(d=>rows.find(r=>r.id===id&&r.date===d));if(rs.some(r=>!r)||new Set(rs.map(r=>r.dose+"_"+r.b)).size!==1)throw Error("plot identity");
const dose=rs[0].dose,b=rs[0].b,S=rs.map(r=>r.S),first=S.findIndex(x=>x>0),last=S.findLastIndex(x=>x>0),firstTwoLive=rs.slice(0,2).some(r=>r.clam==="L");
let reappear=first>=0&&S.slice(first+1).some((x,j)=>x>0&&S[first+j]===0);
return {id,dose,b,bin:dose<=30?"low":dose<=70?"mid":"high",S,first,last,ever:first>=0,final:S.at(-1),early:first>=0&&first<=early,late:first>early,transient:first>=0&&S.at(-1)===0,reappear,firstTwoLive}});
for(let dose=10;dose<=100;dose+=10)for(let b=0;b<2;b++)if(plots.filter(x=>x.dose===dose&&x.b===b).length!==4)throw Error("cell count");
const mean=x=>x.reduce((a,b)=>a+b,0)/x.length,sum=x=>x.reduce((a,b)=>a+b,0);
function stats(a){
 const N=a.length,E=a.filter(x=>x.ever),F=a.filter(x=>x.final>0),early=a.filter(x=>x.early),late=a.filter(x=>x.late),S=sum(a.map(x=>x.final)),seed=sum(a.map(x=>x.dose));
 const factors=[E.length/N,E.length?F.length/E.length:null,F.length?S/F.length:null];
 if(F.length&&Math.abs(factors.reduce((a,b)=>a*b,1)-S/N)>1e-10)throw Error("closure");
 return {N,seed,meanSeed:seed/N,ever:E.length,final:F.length,early:early.length,late:late.length,transient:E.length-F.length,reappear:a.filter(x=>x.reappear).length,earlyFinal:early.filter(x=>x.final>0).length,lateFinal:late.filter(x=>x.final>0).length,finalSum:S,finalMean:S/N,per100Seeds:100*S/seed,factors,live:a.filter(x=>x.firstTwoLive).length,series:full.map((d,i)=>({date:d,positive:a.filter(x=>x.S[i]>0).length,mean:mean(a.map(x=>x.S[i]))})),histories:a.map(x=>[x.id,x.S])};
}
const all=stats(plots),groups={all,low:stats(plots.filter(x=>x.bin==="low")),mid:stats(plots.filter(x=>x.bin==="mid")),high:stats(plots.filter(x=>x.bin==="high")),surface:stats(plots.filter(x=>x.b===0)),buried:stats(plots.filter(x=>x.b===1))};
const density=Object.fromEntries(Array.from({length:10},(_,i)=>[(i+1)*10,stats(plots.filter(x=>x.dose===(i+1)*10))]));
const binBurial=Object.fromEntries(["low","mid","high"].flatMap(bin=>[0,1].map(b=>[bin+"_"+b,stats(plots.filter(x=>x.bin===bin&&x.b===b))])));
const perms=[[0,1,2],[0,2,1],[1,0,2],[1,2,0],[2,0,1],[2,1,0]];
function contrast(a,b){
 if(a.factors.some(x=>x===null)||b.factors.some(x=>x===null))return null;
 const comp=[0,0,0],prod=a=>a.reduce((a,b)=>a*b,1);
 for(const perm of perms){const f=a.factors.slice();for(const i of perm){const before=prod(f);f[i]=b.factors[i];comp[i]+=(prod(f)-before)/6}}
 const delta=b.finalMean-a.finalMean;
 if(Math.abs(sum(comp)-delta)>1e-9)throw Error("shapley closure");
 return {delta,ratio:a.finalMean?b.finalMean/a.finalMean:null,seedRatio:b.meanSeed/a.meanSeed,efficiencyRatio:a.per100Seeds?b.per100Seeds/a.per100Seeds:null,component:comp,relativeComponent:delta?comp.map(x=>x/delta):null,ratioFactors:a.factors.map((v,i)=>v?b.factors[i]/v:null)};
}
const contrasts={lowHigh:contrast(groups.low,groups.high),surfaceBuried:contrast(groups.surface,groups.buried),lowMid:contrast(groups.low,groups.mid),midHigh:contrast(groups.mid,groups.high)};
const leaveDoseOut=[];for(let dose of [10,20,30,80,90,100]){let a=stats(plots.filter(x=>x.bin==="low"&&x.dose!==dose)),b=stats(plots.filter(x=>x.bin==="high"&&x.dose!==dose));leaveDoseOut.push({dose,contrast:contrast(a,b)})}
const arms=Object.fromEntries([0,1].map(b=>[b,contrast(binBurial["low_"+b],binBurial["high_"+b])]));
const adjacent=[];for(let i=1;i<n;i++){const both=plots.filter(x=>x.S[i-1]>0);adjacent.push({from:full[i-1],to:full[i],positiveBefore:both.length,positiveAfter:plots.filter(x=>x.S[i]>0).length,loss:both.filter(x=>x.S[i]===0).length,appearance:plots.filter(x=>x.S[i-1]===0&&x.S[i]>0).length});}
const paired=Array.from({length:10},(_,i)=>{const dose=(i+1)*10,a=stats(plots.filter(x=>x.dose===dose&&x.b===0)),b=stats(plots.filter(x=>x.dose===dose&&x.b===1));return {dose,liveDifference:b.live/4-a.live/4,everDifference:b.ever/4-a.ever/4,finalDifference:b.final/4-a.final/4,countDifference:b.finalMean-a.finalMean}});
const forecastTable=full.map((d,i)=>{const current=plots.filter(x=>x.S[i]>0),absent=plots.filter(x=>x.S[i]===0),ever=plots.filter(x=>x.S.slice(0,i+1).some(y=>y>0));return {date:d,current:current.length,finalAmongCurrent:current.filter(x=>x.final>0).length,finalAmongAbsent:absent.filter(x=>x.final>0).length,ever:ever.length,finalAmongEver:ever.filter(x=>x.final>0).length}});
return {status:"Executed response-open reanalysis of original CSV; observed plot histories, not tracked seed cohorts",source:{doi:"10.5061/dryad.cnp5hqcmx",commit:"90e5e193c9db7efb75c3244f52b1585c9e93718e",blob:"d0f7ae365ae91641d34718c761e67ced1823032e"},byDate,full,plots,groups,density,binBurial,contrasts,arms,leaveDoseOut,adjacent,paired,forecastTable,limits:["Both density row and burial grid side spatially confounded, no causal contrast.","Ever-positive and terminal-positive at scheduled visits are observation states, not actual emergence or survival of individuals.","Shoot counts can include clonal proliferation or immigration; per seed is arithmetic per initial supplied seed, not per-seed survival.","No physical seed retention measured; no clam-free control; all plots initially received live clam.","Same study as prior analysis/149; not independent replication or pooled meta-analysis."]};
}
if(require.main===module){const fs=require("fs"),crypto=require("crypto");if(process.argv.length!==4)throw Error("usage: node script.cjs seed-density.csv output.json");const b=fs.readFileSync(process.argv[2]);const hash=crypto.createHash("sha1").update("blob "+b.length+"\0").update(b).digest("hex");if(hash!=="d0f7ae365ae91641d34718c761e67ced1823032e")throw Error("Git blob mismatch "+hash);fs.writeFileSync(process.argv[3],JSON.stringify(analyze(b.toString("utf8")),null,2)+"\n");}
module.exports=analyze;
