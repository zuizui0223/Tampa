function analyze(seedText,densityText,dapcText,geoText,idsText,sigmaText){
 const parse=(s,sep=",")=>{let [h,...lines]=s.trim().split(/\r\n|\n|\r/),keys=h.split(sep).map(v=>v.replace(/^"|"$/g,""));return lines.map(l=>{let v=l.split(sep).map(x=>x.replace(/^"|"$/g,""));if(v.length!==keys.length)throw Error("column count "+l);return Object.fromEntries(keys.map((k,i)=>[k,v[i]]))})};
 const seed=parse(seedText),allD=parse(densityText),density=allD.filter(r=>r.month==="June"),geo=parse(geoText);
 const sum=a=>a.reduce((s,v)=>s+v,0),mean=a=>sum(a)/a.length,uniq=a=>[...new Set(a)],group=(a,fn)=>Object.fromEntries(uniq(a.map(fn)).map(k=>[k,a.filter(x=>fn(x)===k)]));
 const names={DC:"Curlew",LP:"Lynch",WB:"West",NB:"Niles"},abbr={DC:"cur",LP:"lyn",WB:"wes",NB:"nil"},letter={DC:"D",LP:"L",WB:"W",NB:"N"};
 if(seed.length!==224||density.length!==141||seed.some(r=>!["TRUE","FALSE"].includes(r.seedTF)))throw Error("source scope");
 const num=(x)=>{if(x===""||x==="NA"||!Number.isFinite(+x))return null;return +x};
 const coreKey=r=>[r.site,r.depth,r.quad,r.core].join("|");
 const gridKey=r=>[r.site,r.depth,r.quad].join("|");
 const countPolicy=(r,strict=false)=>r.seedTF==="TRUE"&&(!strict||num(r.mass)!==null&&num(r.mass)>0);
 const cores=Object.entries(group(seed,coreKey)).map(([id,a])=>{
  const r=a[0],n=a.filter(x=>countPolicy(x)).length,strict=a.filter(x=>countPolicy(x,true)).length,zero=a.filter(x=>x.seedTF==="FALSE").length;
  if((zero&&n)||zero>1||(!zero&&!n))throw Error("ambiguous core "+id);
  return {id,site:r.site,depth:r.depth,quad:r.quad,core:r.core,n,strict,zeros:zero,rows:a.length};
 });
 if(cores.length!==90)throw Error("core grain");
 const duplicateSeedKeys=Object.entries(group(seed.filter(r=>r.seedTF==="TRUE"),r=>coreKey(r)+"|"+r.seed)).filter(([k,a])=>a.length>1).map(([k,a])=>({key:k,records:a}));
 const seedMassN=seed.filter(r=>countPolicy(r,true)).length;
 const summary=(a,k="n")=>{let c=a.map(x=>x[k]),N=sum(c),p=c.filter(x=>x>0),top=c.slice().sort((a,b)=>b-a);return {cores:c.length,count:N,mean:mean(c),positive:p.length,occupancy:p.length/c.length,conditional:p.length?mean(p):null,max:top[0],topShare:N?top[0]/N:null,top3Share:N?sum(top.slice(0,3))/N:null,effectiveCores:N?N*N/sum(c.map(x=>x*x)):null,withoutMaxMean:c.length>1?(N-top[0])/(c.length-1):null}};
 const byDepth=Object.fromEntries(Object.entries(group(cores,r=>r.depth)).map(([k,a])=>[k,summary(a)]));
 const bySiteDepth=Object.fromEntries(Object.entries(group(cores,r=>r.site+"|"+r.depth)).map(([k,a])=>[k,summary(a)]));
 const grids=Object.entries(group(cores,gridKey)).map(([id,a])=>{
  const r=a[0],d=density.filter(x=>x.site===r.site&&x.depth===r.depth&&x["perm.quadrat"]===r.quad);
  if(d.length<4||d.some(x=>num(x["f.density"])===null||num(x["veg.density"])===null||num(x["total.density"])!==num(x["f.density"])+num(x["veg.density"])))throw Error("density join "+id);
  const g=geo.find(x=>x[""]===abbr[r.site]+"."+r.depth.toLowerCase()[0]+r.quad);if(!g)throw Error("geo join "+id);
  return {id,site:r.site,depth:r.depth,quad:r.quad,lat:+g.lat,lon:+g.lon,nDensity:d.length,flowers:mean(d.map(x=>+x["f.density"])),veg:mean(d.map(x=>+x["veg.density"])),total:mean(d.map(x=>+x["total.density"])),floweringIncidence:mean(d.map(x=>+(+x["f.density"]>0))),bank:summary(a),massOnly:summary(a,"strict")};
 });
 if(grids.length!==24||uniq(grids.map(g=>g.id)).length!==24)throw Error("grid grain");
 const depthContrasts=Object.keys(names).map(site=>{
 let a=grids.filter(g=>g.site===site&&g.depth==="SH"),b=grids.filter(g=>g.site===site&&g.depth==="DP");
 const fm=r=>mean(r.map(g=>g.flowers)),bm=r=>mean(r.map(g=>g.bank.mean));
 const sa=bySiteDepth[site+"|SH"],sb=bySiteDepth[site+"|DP"];
 const a0=fm(a),b0=fm(b),A=bm(a),B=bm(b);
 return {site,name:names[site],shallowFlowers:a0,deepFlowers:b0,shallowBank:A,deepBank:B,flowerRatio:b0>0?a0/b0:null,bankRatio:B>0?A/B:null,bankPerFlowerRatio:A>0&&B>0&&a0>0&&b0>0?(A/a0)/(B/b0):null,shallowOccupancy:sa.occupancy,deepOccupancy:sb.occupancy,shallowPositiveMean:sa.conditional,deepPositiveMean:sb.conditional};
 });
 function compare(a,b){let d=b.mean-a.mean;if(a.conditional===null||b.conditional===null)return {difference:d,incidence:null,magnitude:null};let incidence=(b.occupancy-a.occupancy)*(a.conditional+b.conditional)/2,magnitude=(b.conditional-a.conditional)*(a.occupancy+b.occupancy)/2;if(Math.abs(incidence+magnitude-d)>1e-9)throw Error("closure");return {difference:d,incidence,magnitude,incidenceShare:d?incidence/d:null}}
 const aggregation={all:summary(cores),strict:summary(cores,"strict"),byDepth,strictDepth:Object.fromEntries(Object.entries(group(cores,r=>r.depth)).map(([k,a])=>[k,summary(a,"strict")])),bySiteDepth,depthContrasts,pooledDepthAccounting:compare(byDepth.DP,byDepth.SH),maxCore:cores.slice().sort((a,b)=>b.n-a.n)[0]};
 const withoutTop=cores.filter(x=>x.id!==aggregation.maxCore.id);
 aggregation.omitLargestCore={all:summary(withoutTop),SH:summary(withoutTop.filter(x=>x.depth==="SH")),DP:summary(withoutTop.filter(x=>x.depth==="DP"))};
 // Local rank concordance at fixed site x depth: three grids. Compare with flowering and vegetative density.
 const rank=x=>x.map(v=>1+x.filter(u=>u<v).length+(x.filter(u=>u===v).length-1)/2);
 const corr=(a,b)=>{let A=mean(a),B=mean(b),s=sum(a.map((x,i)=>(x-A)*(b[i]-B))),d=Math.sqrt(sum(a.map(x=>(x-A)**2))*sum(b.map(x=>(x-B)**2)));return d?s/d:null};
 const spearman=(a,b)=>corr(rank(a),rank(b));
 const concordance=(rr,field,yfield="bank")=>{let p=0,m=0,t=0;for(let i=0;i<rr.length;i++)for(let j=i+1;j<rr.length;j++){let s=(rr[i][field]-rr[j][field])*(rr[i][yfield].mean-rr[j][yfield].mean);if(s>0)p++;else if(s<0)m++;else t++;}return {positive:p,negative:m,ties:t}};
 const local=Object.entries(group(grids,g=>g.site+"|"+g.depth)).map(([k,a])=>({group:k,flower:concordance(a,"flowers"),veg:concordance(a,"veg"),total:concordance(a,"total"),flowerMass:concordance(a,"flowers","massOnly")}));
 const withinTotal=Object.fromEntries(["flower","veg","total","flowerMass"].map(k=>[k,Object.fromEntries(["positive","negative","ties"].map(s=>[s,sum(local.map(x=>x[k][s]))]))]));
 // Leave one entire meadow out: equal grid weight, train only scaling, ridge fixed penalty; exploratory.
 const features={mean:r=>[],depth:r=>[+(r.depth==="SH")],flower:r=>[Math.log1p(r.flowers)],veg:r=>[Math.log1p(r.veg)],depthFlower:r=>[+(r.depth==="SH"),Math.log1p(r.flowers)],depthVeg:r=>[+(r.depth==="SH"),Math.log1p(r.veg)],depthVegFlower:r=>[+(r.depth==="SH"),Math.log1p(r.veg),Math.log1p(r.flowers)]};
 function solve(A,b){let M=A.map((r,i)=>[...r,b[i]]),n=b.length;for(let j=0;j<n;j++){let k=j;for(let i=j+1;i<n;i++)if(Math.abs(M[i][j])>Math.abs(M[k][j]))k=i;[M[j],M[k]]=[M[k],M[j]];if(Math.abs(M[j][j])<1e-12)throw Error("singular");let z=M[j][j];M[j]=M[j].map(v=>v/z);for(let i=0;i<n;i++)if(i!==j){let q=M[i][j];M[i]=M[i].map((v,l)=>v-q*M[j][l]);}}return M.map(r=>r[n])}
 function cv(rr,fn,lam,yfield){let pred=[];for(let hold of Object.keys(names)){const train=rr.filter(g=>g.site!==hold),test=rr.filter(g=>g.site===hold);if(!test.length)continue;let raw=train.map(fn),k=raw[0].length,mu=Array.from({length:k},(_,j)=>mean(raw.map(x=>x[j]))),sd=mu.map((m,j)=>Math.sqrt(mean(raw.map(x=>(x[j]-m)**2)))||1);
 const trans=r=>[1,...fn(r).map((v,j)=>(v-mu[j])/sd[j])],X=train.map(trans),y=train.map(r=>Math.log1p(r[yfield].mean));
 const A=Array.from({length:k+1},(_,i)=>Array.from({length:k+1},(_,j)=>sum(X.map(x=>x[i]*x[j]))+(i===j&&i>0?lam:0))),b=A.map((_,i)=>sum(X.map((x,j)=>x[i]*y[j]))),w=solve(A,b);
 for(let r of test){let z=Math.max(0,sum(trans(r).map((x,j)=>x*w[j]))),obs=Math.log1p(r[yfield].mean);pred.push({id:r.id,site:r.site,observed:obs,pred:z,se:(z-obs)**2,ae:Math.abs(z-obs)});}}
 return {mse:mean(pred.map(x=>x.se)),mae:mean(pred.map(x=>x.ae)),bySite:Object.fromEntries(Object.entries(group(pred,x=>x.site)).map(([s,a])=>[s,mean(a.map(x=>x.se))])),predictions:pred};}
 const cvs={};for(let yfield of ["bank","massOnly"]){cvs[yfield]={};for(let [nm,rr] of [["all",grids],["omit_largest_core_grid",grids.filter(g=>g.id!==gridKey(aggregation.maxCore))]]){cvs[yfield][nm]={};for(let [model,fn] of Object.entries(features)){cvs[yfield][nm][model]=Object.fromEntries([.1,1,10].map(l=>[l,cv(rr,fn,l,yfield)]));}}}
 // DAPC source table orientation rows predicted adult cluster, columns collected seed group.
 const [head,...lines]=dapcText.trim().split(/\r?\n/);const dest=head.split("\t");const assign=[];
 for(let line of lines){let [src,...v]=line.split("\t");if(v.length!==dest.length)throw Error("assignment table");for(let j=0;j<v.length;j++){let n=+v[j];if(n)assign.push({src,dest:dest[j],n});}}
 const id=idsText.trim().split(/\s+/),seeds=id.filter(x=>x.endsWith("S")),adults=id.filter(x=>x.endsWith("A"));
 if(seeds.length!==99||adults.length!==214||sum(assign.map(a=>a.n))!==99)throw Error("assignment n");
 const rev=Object.fromEntries(Object.entries(names).map(([k,v])=>[v,k]));
 const dc=(s)=>{const [site,d]=s.split("_");return {site:rev[site],depth:d==="S"?"SH":"DP"}};
 const center=(s)=>{let x=dc(s),a=grids.filter(g=>g.site===x.site&&g.depth===x.depth);return {lat:mean(a.map(g=>g.lat)),lon:mean(a.map(g=>g.lon))}};
 const hav=(a,b)=>{const r=Math.PI/180,dlat=(b.lat-a.lat)*r,dlon=(b.lon-a.lon)*r,z=Math.sin(dlat/2)**2+Math.cos(a.lat*r)*Math.cos(b.lat*r)*Math.sin(dlon/2)**2;return 6371000*2*Math.asin(Math.sqrt(z))};
 for(let a of assign){let x=dc(a.src),y=dc(a.dest);a.type=x.site!==y.site?"other_meadow":x.depth!==y.depth?"same_meadow_other_depth":"same_meadow_depth";a.centroidDistanceM=hav(center(a.src),center(a.dest));}
 const byDest=Object.fromEntries(dest.map(d=>{let a=assign.filter(x=>x.dest===d),n=sum(a.map(x=>x.n)),expected=seeds.filter(id=>id.startsWith(letter[dc(d).site]+(dc(d).depth==="SH"?"S":"D"))).length;if(n!==expected)throw Error("assignment vs seed IDs "+d+" "+n+" "+expected);return [d,{n,types:Object.fromEntries(["same_meadow_depth","same_meadow_other_depth","other_meadow"].map(k=>[k,sum(a.filter(x=>x.type===k).map(x=>x.n))]))}]}));
 const totals=Object.fromEntries(["same_meadow_depth","same_meadow_other_depth","other_meadow"].map(k=>[k,sum(assign.filter(x=>x.type===k).map(x=>x.n))]));
 const sigma=parse(sigmaText,"\t").map(r=>Object.fromEntries(Object.entries(r).map(([k,v])=>[k,+v])));
 const distances=Object.keys(names).map(site=>({site,distanceM:hav(center(names[site]+"_D"),center(names[site]+"_S"))}));
 const origin={total:99,totals,byDest,assign,distances,adults:adults.length,seeds:seeds.length,sigmaRepoKm:sigma,sourcePublishedSigmaM:[111,153],warning:"Hard DAPC labels from author output, not validated true origin; no calibrated probabilities, forced assignments, no independent individual test, nuclear signal reflects both parents and local population structure; centroid distance not traveled distance."};
 return {source:{repo:"esotka/ZosteraSNPs",ref:"bec412e35b8669b2850bf8f1d525e5c0ab850d00",paper:"10.1111/mec.17565"},audit:{seedRows:seed.length,positiveSeedRows:seed.filter(x=>countPolicy(x)).length,positiveRowDepth: Object.fromEntries(["SH","DP"].map(d=>[d,seed.filter(x=>x.depth===d&&countPolicy(x)).length])),allRowDepth:Object.fromEntries(["SH","DP"].map(d=>[d,seed.filter(x=>x.depth===d).length])),massN:seedMassN,duplicateSeedKeys,coreN:cores.length,densityN:density.length,gridN:grids.length},aggregation,cores,grids,local,withinTotal,rankCorrelations:{flower:spearman(grids.map(g=>g.flowers),grids.map(g=>g.bank.mean)),veg:spearman(grids.map(g=>g.veg),grids.map(g=>g.bank.mean)),total:spearman(grids.map(g=>g.total),grids.map(g=>g.bank.mean))},cvs,origin,limits:["Repository author code counts seedTF TRUE records including seedcoats/dead/lost labels; not verified live seed counts. Keep source rows and explicit zeros. Mass-only sensitivity selected by outcome/handling; not corrected viable counts. Published prose 176 shallow and 46 deep differs; repository version not necessarily final archive.","June density quadrats and September sediment cores joined at grid (not individual plant or seed). No measured fruit output, true dispersal, survival or hydrodynamic flux. Distinct sampling area; relative ratios descriptive only.","Four meadows, three grids per depth; holdout and rank summaries exploratory, no independent validation or causal inference. DAPC hard assignment uncertain and unvalidated; no origin estimate or pooling."]};
}
const expected=["1a1dc32028592569eeeef716873570d9230450db","3a9ee3bf0c6a0be0fa2688d87a8cba6acc80f883","8b83e6473a085036a044e1a671f4aa0022bf691d","7d37d8cad640bbb294c4533bdb6aee25925ed343","080e05545930f83b2d298798b77f77596830d681","4233b972171dfd9df45466e72192778d73bc3b6e"];
if(require.main===module){const fs=require("fs"),crypto=require("crypto");if(process.argv.length!==9)throw Error("usage: node script.cjs seeds.csv density.csv dapc.txt geo.csv ids sigma.txt output.json");let x=process.argv.slice(2,8).map((path,i)=>{let b=fs.readFileSync(path);let h=crypto.createHash("sha1").update("blob "+b.length+"\0").update(b).digest("hex");if(h!==expected[i])throw Error("blob mismatch "+path);return b.toString("utf8")});fs.writeFileSync(process.argv[8],JSON.stringify(analyze(...x),null,2)+"\n")}
module.exports=analyze;
