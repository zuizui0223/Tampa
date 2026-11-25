function analyze(input){
 const calc=(a)=>{const s=1-a.peak_loss_surface/100,b=1-a.peak_loss_buried/100,final=a.final_buried/a.final_surface,post=b/s,peak=final/post;return {final_ratio:final,final_difference_pp:a.final_buried-a.final_surface,postpeak_stock_ratio:post,implied_peak_ratio:peak,implied_peak_surface_pct:a.final_surface/s,implied_peak_buried_pct:a.final_buried/b,log_peak_share:Math.log(peak)/Math.log(final),log_postpeak_share:Math.log(post)/Math.log(final),separate_recovery_ratio:a.recover_buried/a.recover_surface}};
 const sites=input.map(a=>{const point=calc(a),keys=["final_surface","final_buried","peak_loss_surface","peak_loss_buried"],samples=[];for(let i=0;i<16;i++){const c={...a};keys.forEach((k,j)=>c[k]+=((i>>j)&1?1:-1)*(k.startsWith("final")?.05:.5));samples.push(calc(c));}if(Math.abs(point.implied_peak_ratio*point.postpeak_stock_ratio-point.final_ratio)>1e-10)throw Error("identity");const rounding=Object.fromEntries(["final_ratio","postpeak_stock_ratio","implied_peak_ratio","log_postpeak_share"].map(k=>[k,[Math.min(...samples.map(x=>x[k])),Math.max(...samples.map(x=>x[k]))]]));return {...a,...point,rounding}});return {source:{doi:"10.3354/meps09612",url:"https://www.int-res.com/articles/theme/m448p197.pdf",pages:"201–203 Results/Discussion; printed abstract p197"},sites,limits:["Published rounded aggregate values; no original plot-level covariance or standard errors. Rounding sensitivity is not inferential uncertainty.","Peak date may differ by treatment; peak stock is back-calculated from reported mean peak loss, not independent measured individual transition. Stock retention may reflect detection and cohort changes.","Recovery experiments use independent destructive plots, 50 seeds per plot and four blocks; later video plots have 200 seeds per plot and six plots per arm/site. Never divide final establishment by recovered seed fraction to infer conditional survival.","Three sites in one paper; not three independent studies, no causal animal treatment. Original paper already documented burial and post-germination loss."]};
}
const input=[
  {
    "site": "Piankatank River",
    "recover_surface": 10,
    "recover_buried": 56,
    "final_surface": 1.2,
    "final_buried": 40.4,
    "peak_loss_surface": 93,
    "peak_loss_buried": 1
  },
  {
    "site": "Mumfort Island",
    "recover_surface": 9,
    "recover_buried": 27,
    "final_surface": 3.8,
    "final_buried": 16.8,
    "peak_loss_surface": 26,
    "peak_loss_buried": 21
  },
  {
    "site": "Spider Crab Bay",
    "recover_surface": 45,
    "recover_buried": 55,
    "final_surface": 2.8,
    "final_buried": 10.3,
    "peak_loss_surface": 80,
    "peak_loss_buried": 50
  }
];
if(require.main===module){const r=analyze(input),fs=require('fs');if(process.argv[2])fs.writeFileSync(process.argv[2],JSON.stringify(r,null,2)+'\n');else console.log(JSON.stringify(r,null,2));}
module.exports=analyze;
