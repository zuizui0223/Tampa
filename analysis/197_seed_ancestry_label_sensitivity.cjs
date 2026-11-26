function analyze(idText,...qTexts){
 const ids=idText.trim().split(/\s+/);if(ids.length!==313||new Set(ids).size!==313)throw Error("id grain");
 const names={D:"Curlew",L:"Lynch",W:"West",N:"Niles"},ks=[2,5,9],sum=a=>a.reduce((s,v)=>s+v,0),mean=a=>sum(a)/a.length,uniq=a=>[...new Set(a)],group=(a,fn)=>Object.fromEntries(uniq(a.map(fn)).map(k=>[k,a.filter(x=>fn(x)===k)]));
 const m=ids.map(id=>{if(!/^[DLWN][DS][123]_\d{2}[AS]$/.test(id))throw Error("id schema "+id);return {id,site:names[id[0]],depth:id[1],grid:id.slice(0,3),type:id.at(-1)}});
 const datasets=Object.fromEntries(qTexts.map((txt,j)=>{let k=ks[j],q=txt.trim().split(/\r?\n/).map(l=>l.trim().split(/\s+/).map(Number));if(q.length!==313||q.some(r=>r.length!==k||r.some(x=>!Number.isFinite(x)||x<0||x>1)||Math.abs(sum(r)-1)>1e-5))throw Error("qopt alignment");return [k,m.map((r,i)=>({...r,q:q[i]}))]}));
 const dist=(a,b,metric)=>sum(a.map((v,j)=>(metric==="hellinger"?Math.sqrt(v)-Math.sqrt(b[j]):v-b[j])**2));
 const centroid=(r,k)=>Array.from({length:k},(_,j)=>mean(r.map(x=>x.q[j])));
 const gridCentroid=(r,k)=>{let g=Object.values(group(r,x=>x.grid)).map(a=>centroid(a,k));return Array.from({length:k},(_,j)=>mean(g.map(v=>v[j])))};
 function classify(train,test,k,metric,level,weight){
   const key=r=>level==="site"?r.site:r.site+"_"+r.depth;
   const groups=group(train,key),c=Object.entries(groups).map(([name,r])=>({name,q:weight==="grid"?gridCentroid(r,k):centroid(r,k)}));
   return test.map(r=>{let d=c.map(g=>({name:g.name,d:dist(r.q,g.q,metric)})).sort((a,b)=>a.d-b.d||a.name.localeCompare(b.name));
   let nearest=d[0],truth=key(r),local=d.find(x=>x.name===truth);let siteLabel=nearest.name.split("_")[0];const tied=d.length>1&&Math.abs(d[1].d-d[0].d)<1e-12;
   return {id:r.id,site:r.site,depth:r.depth,grid:r.grid,truth,pred:nearest.name,sitePred:siteLabel,correct:nearest.name===truth,siteCorrect:siteLabel===r.site,tied,localD:local.d,nearestD:nearest.d,relativeMargin:(d[1].d-nearest.d)/(d[1].d||1)}});
 }
 const stat=a=>({n:a.length,correct:a.filter(x=>x.correct).length,siteCorrect:a.filter(x=>x.siteCorrect).length,tied:a.filter(x=>x.tied).length,balancedAccuracy:mean(Object.values(group(a,x=>x.truth)).map(r=>mean(r.map(x=>+x.correct)))),bySite:Object.fromEntries(Object.entries(group(a,x=>x.site)).map(([site,r])=>[site,{n:r.length,correct:r.filter(x=>x.correct).length,siteCorrect:r.filter(x=>x.siteCorrect).length,predicted:Object.fromEntries(Object.entries(group(r,x=>x.pred)).map(([k,x])=>[k,x.length]))}]))});
 const results=[];
 for(let k of ks){let a=datasets[k].filter(r=>r.type==="A"),s=datasets[k].filter(r=>r.type==="S");if(a.length!==214||s.length!==99)throw Error("adult/seed count");
 for(let metric of ["euclidean","hellinger"])for(let level of ["site","site_depth"])for(let weight of ["grid","individual"]){
 const folds=uniq(a.map(r=>r.grid)),held=folds.flatMap(g=>classify(a.filter(r=>r.grid!==g),a.filter(r=>r.grid===g),k,metric,level,weight));
 const seed=classify(a,s,k,metric,level,weight);results.push({k,metric,level,weight,adults:stat(held),seeds:stat(seed),adultPredictions:held,seedPredictions:seed});
 }}
 const primary=results.filter(r=>r.level==="site_depth"&&r.weight==="grid"&&r.metric==="euclidean");
 const fine=results.filter(r=>r.k>=5&&r.level==="site_depth"&&r.weight==="grid");
 const cons=m.filter(r=>r.type==="S").map(r=>{let pred=fine.map(x=>x.seedPredictions.find(y=>y.id===r.id));return {id:r.id,site:r.site,preds:pred.map(x=>x.sitePred),allSame:uniq(pred.map(x=>x.sitePred)).length===1,allLocal:pred.every(x=>x.siteCorrect),allNonlocal:pred.every(x=>!x.siteCorrect),sameNonlocal:pred.every(x=>!x.siteCorrect)&&uniq(pred.map(x=>x.sitePred)).length===1}});
 const summaryCons={n:cons.length,allLocal:cons.filter(x=>x.allLocal).length,allNonlocal:cons.filter(x=>x.allNonlocal).length,sameNonlocal:cons.filter(x=>x.sameNonlocal).length,unstable:cons.filter(x=>!x.allLocal&&!x.sameNonlocal).length,bySite:Object.fromEntries(Object.entries(group(cons,r=>r.site)).map(([k,a])=>[k,{n:a.length,allLocal:a.filter(x=>x.allLocal).length,sameNonlocal:a.filter(x=>x.sameNonlocal).length,allNonlocal:a.filter(x=>x.allNonlocal).length}]))};
 return {source:{repo:"esotka/ZosteraSNPs",ref:"bec412e35b8669b2850bf8f1d525e5c0ab850d00",paper:"10.1111/mec.17565"},nAdults:214,nSeeds:99,results,primary:primary.map(r=>({k:r.k,adults:r.adults,seeds:r.seeds})),fineConsensus:summaryCons,consensusRows:cons,limits:["Qopt row correspondence uses source author positional mapping to the 313-ID list, not IDs in the Q files. All K derived from the same already-fitted joint adult+seed genotype model; holdout excludes only adult centroid training labels, not genotype model fitting. Not out-of-sample genetic assignment validation.","Nearest centroid is descriptive resemblance, not a population-of-origin model, not DAPC accuracy. Adult site label is sampled site, not natal origin. Depth and site can overlap in ancestry; nuclear seed ancestry includes both parents.","Fine consensus compares K5/K9 and Euclidean/Hellinger with equal grid-weight centroid; no independent samples, confidence or true dispersal distance. No per-seed DAPC labels available, aggregate comparison only."]};
}
const expected=["080e05545930f83b2d298798b77f77596830d681","c5792c09d5c48708d34215e25fb87878510aaad3","9409a9f2192728e80edb4a8c6bd2a0abdaf53748","b767d3c144a0dbaae4b8d623c762ca123d4a7323"];
if(require.main===module){const fs=require("fs"),crypto=require("crypto");if(process.argv.length!==7)throw Error("usage: node script.cjs ids k2.qopt k5.qopt k9.qopt output.json");let x=process.argv.slice(2,6).map((path,i)=>{let b=fs.readFileSync(path),h=crypto.createHash("sha1").update("blob "+b.length+"\0").update(b).digest("hex");if(h!==expected[i])throw Error("blob mismatch "+path);return b.toString("utf8")});fs.writeFileSync(process.argv[6],JSON.stringify(analyze(...x),null,2)+"\n")}
module.exports=analyze;
