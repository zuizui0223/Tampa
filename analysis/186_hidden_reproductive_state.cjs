function analyze(shootCSV,gainCSV){
 const parse=s=>{const lines=s.trim().split(/\r?\n/),h=lines.shift().split(",");return lines.map(l=>Object.fromEntries(l.split(",").map((v,i)=>[h[i],v===""||v==="NA"?null:(i<3?v:Number(v))])))};
 const rows=parse(shootCSV),gains=parse(gainCSV),key=r=>r.block+":"+r.plot;
 const gm=new Map(gains.map(r=>[key(r),r]));
 if(rows.length!==36||gm.size!==36||new Set(rows.map(key)).size!==36)throw Error("grain");
 const dates=Object.keys(rows[0]).filter(k=>/^\d+\/\d+\/\d+$/.test(k));
 const trts=["0X","1X","2X","4X"], blocks=[...new Set(rows.map(r=>r.block))].sort((a,b)=>+a-+b);
 const mean=x=>x.reduce((a,b)=>a+b,0)/x.length;
 const av=(r,ks)=>ks.every(k=>Number.isFinite(r[k]))?mean(ks.map(k=>r[k])):null;
 const sym=(a,b)=>a+b===0?0:(a-b)/(a+b);
 const exact=(ds)=>{let obs=Math.abs(mean(ds)),n=0;for(let m=0;m<2**ds.length;m++){let x=0;for(let i=0;i<ds.length;i++)x+=ds[i]*((m>>i)&1?1:-1);if(Math.abs(x/ds.length)>=obs-1e-12)n++}return n/2**ds.length};
 for(const r of rows){const g=gm.get(key(r));if(!g||g.trt!==r.trt||g.initial!==r[dates[0]]||g.final!==r[dates.at(-1)]||g.S_may!==r["5/21/2018"]||g.S_jun!==r["6/18/2018"]||g.F_may!==r["no.flowers.may.2018"]||g.F_jun!==r["no.flowers.june.2018"])throw Error("source mismatch");r.gain=g.gain;r.common_gain=g.common_gain;r.rare=g.expected_gain_k28;r.F=av(r,["no.flowers.may.2018","no.flowers.june.2018"]);r.G1=g.G1;}
 const pairs=(trt)=>blocks.map(b=>{let a=rows.find(r=>r.block===b&&r.trt===trt),c=rows.find(r=>r.block===b&&r.trt==="0X");if(!a||!c)throw Error("pair");return {b,a,c}});
 const windows={baseline:[dates[0]],pre2017:[...dates.slice(0,3)],growing2017:dates.slice(5,9),pre2018:dates.slice(10,14),mayJun2018:["5/21/2018","6/18/2018"],post2018:["7/16/2018","10/29/2018"],final:[dates.at(-1)]};
 const diag=(ps,ks,g="gain",adjust=false)=>{const u=ps.map(({b,a,c})=>{let A=av(a,ks),C=av(c,ks);if(A===null||C===null)return null;let a0=a[dates[0]],c0=c[dates[0]];if(adjust){A/=a0;C/=c0;}const ds=sym(A,C),dg=sym(a[g],c[g]),df=sym(a.F,c.F);return {b,A,C,ds,dg,df,d:ds-dg,gain_a:a[g],gain_c:c[g],F_a:a.F,F_c:c.F}}).filter(Boolean);let loss=u.filter(x=>x.gain_a<x.gain_c),notLower=u.filter(x=>x.A>=x.C);return {n:u.length,mean_shoot_sym:mean(u.map(x=>x.ds)),mean_gain_sym:mean(u.map(x=>x.dg)),gap:mean(u.map(x=>x.d)),p_gap_label_swap:exact(u.map(x=>x.d)),lower_gain:loss.length,shoot_ge_control:notLower.length,missed_lower_gain:loss.filter(x=>x.A>=x.C).length,strict_joint_lower_F_and_gain:u.filter(x=>x.A>=x.C&&x.F_a<x.F_c&&x.gain_a<x.gain_c).length,blocks_missed:loss.filter(x=>x.A>=x.C).map(x=>x.b),details:u}};
 const arms={};for(const t of trts.slice(1)){const ps=pairs(t);arms[t]={windows:Object.fromEntries(Object.entries(windows).map(([k,v])=>[k,diag(ps,v)])),dates:Object.fromEntries(dates.map(d=>[d,diag(ps,[d])])),sensitivity:{mayJunBaselineAdjusted:diag(ps,windows.mayJun2018,"gain",true),finalBaselineAdjusted:diag(ps,windows.final,"gain",true),mayJunCommonGain:diag(ps,windows.mayJun2018,"common_gain"),mayJunRare:diag(ps,windows.mayJun2018,"rare"),mayJunDropBlocks59:diag(ps.filter(x=>!["5","9"].includes(x.b)),windows.mayJun2018)}};}
 // Retrospective held-block binary prediction, fixed ridge logistic regression via gradient descent; no tuning.
 // Outcome any detected new MLG over full experiment. Features overlap outcome interval.
 const features={baseline:r=>[Math.log1p(r[dates[0]]),Math.log1p(r.G1)],standing:r=>[Math.log1p(r[dates[0]]),Math.log1p(r.G1),Math.log1p(av(r,windows.mayJun2018)),Math.log1p(r[dates.at(-1)])],history:r=>[Math.log1p(r[dates[0]]),Math.log1p(r.G1),Math.log1p(av(r,windows.growing2017)),Math.log1p(av(r,windows.pre2018)),Math.log1p(av(r,windows.mayJun2018)),Math.log1p(r[dates.at(-1)])],flowers:r=>[Math.log1p(r[dates[0]]),Math.log1p(r.G1),Math.log1p(av(r,windows.mayJun2018)),Math.log1p(r[dates.at(-1)]),Math.log1p(r.F)],historyFlowers:r=>[Math.log1p(r[dates[0]]),Math.log1p(r.G1),Math.log1p(av(r,windows.growing2017)),Math.log1p(av(r,windows.pre2018)),Math.log1p(av(r,windows.mayJun2018)),Math.log1p(r[dates.at(-1)]),Math.log1p(r.F)],treatment:r=>[Math.log1p(r[dates[0]]),Math.log1p(r.G1),...trts.slice(1).map(t=>+(r.trt===t))]};
 const sigmoid=z=>1/(1+Math.exp(-Math.max(-30,Math.min(30,z))));
 const cv=(pop,fn,lambda)=>{let scores=[];for(const b of blocks){let train=pop.filter(r=>r.block!==b),test=pop.filter(r=>r.block===b);let preds;if(!fn){preds=test.map(()=> (train.filter(r=>r.gain>0).length+.5)/(train.length+1));}else{let raw=train.map(fn),d=raw[0].length,mu=Array.from({length:d},(_,j)=>mean(raw.map(x=>x[j]))),sd=mu.map((m,j)=>Math.sqrt(mean(raw.map(x=>(x[j]-m)**2)))||1),scale=x=>[1,...x.map((v,j)=>(v-mu[j])/sd[j])],X=raw.map(scale),y=train.map(r=>+(r.gain>0)),w=Array(d+1).fill(0);
 const dot=(a,b)=>a.reduce((s,x,i)=>s+x*b[i],0);const step=.2/(1+lambda+Math.max(...X.map(x=>dot(x,x))));for(let iter=0;iter<6000;iter++){let grad=w.map((v,j)=>j?lambda*v:0);for(let i=0;i<X.length;i++){let err=sigmoid(dot(X[i],w))-y[i];for(let j=0;j<w.length;j++)grad[j]+=err*X[i][j]}w=w.map((v,j)=>v-step*grad[j]);}preds=test.map(r=>sigmoid(dot(scale(fn(r)),w)));}
 for(let i=0;i<test.length;i++){let y=+(test[i].gain>0),pr=preds[i];scores.push({b,trt:test[i].trt,y,p:pr,brier:(y-pr)**2,logloss:-(y*Math.log(pr)+(1-y)*Math.log1p(-pr))});}}
 return {n:scores.length,events:scores.reduce((a,x)=>a+x.y,0),brier:mean(scores.map(x=>x.brier)),logloss:mean(scores.map(x=>x.logloss)),predictions:scores}};
 const cvs={};for(const [nm,pop] of [["all",rows],["recurrent_and_control",rows.filter(r=>["0X","2X"].includes(r.trt))]]){cvs[nm]={mean:cv(pop,null,1)};for(const [f,fn] of Object.entries(features)){cvs[nm][f]=Object.fromEntries([.1,1,10].map(l=>[l,cv(pop,fn,l)]));}}
 return {status:"Executed secondary analysis; block-paired diagnostic and retrospective held-block prediction, not causal mediation or prospective forecast",source:{shoot_commit:"eeff76e6a68f73db8d5c2afd3225e17ebf2b4d7e",shoot_blob:"b4f417bc95f21a3828399e3a54943031759ace32",gain_commit:"58600bd10b5e53d90cc551fd08e5d9be97d3a996",gain_blob:"046acb03b5cbd6baa1972430ba15eaf584cd97a1"},n:rows.length,dates,windows,arms,cvs};
}
if (require.main===module){
 const fs=require("fs"),crypto=require("crypto");
 if(process.argv.length!==5)throw Error("usage: node script.cjs ORIGINAL_SHOOTS.csv FROZEN_GAIN.csv output.json");
 function read(path,expected){const b=fs.readFileSync(path),hash=crypto.createHash("sha1").update("blob "+b.length+"\0").update(b).digest("hex");if(hash!==expected)throw Error("Git blob mismatch "+path+" "+hash);return b.toString("utf8")}
 const s=read(process.argv[2],"b4f417bc95f21a3828399e3a54943031759ace32"),g=read(process.argv[3],"046acb03b5cbd6baa1972430ba15eaf584cd97a1");
 fs.writeFileSync(process.argv[4],JSON.stringify(analyze(s,g),null,2)+"\n");
}
module.exports=analyze;
