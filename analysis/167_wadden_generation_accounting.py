#!/usr/bin/env python3
"""Plot-level two-generation restoration accounting; no causal mediation."""
import argparse,zipfile,json,hashlib,io,numpy as np,pandas as pd
from pathlib import Path
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge
def run(MAP,OUT):
    OUT.mkdir(exist_ok=True,parents=True)
    assert hashlib.sha256(MAP.read_bytes()).hexdigest()=='ad0097d3e14373bf0cb7babef0dd4aa26678d6bb97c7e5d94af5f7e534bc05e1'
    with zipfile.ZipFile(MAP) as z:
        m=json.loads(z.read('manifest.json'));f=next(x for x in m if x.get('doi')=='10.34894/FKSY2M')['files'][0];raw=z.read(f['file']);assert hashlib.sha256(raw).hexdigest()==f['sha256'];wb=pd.ExcelFile(io.BytesIO(raw));r=pd.read_excel(wb,sheet_name='Recruitment_success&efficiency');pl=pd.read_excel(wb,sheet_name='Plantdata_August2020');e=pd.read_excel(wb,sheet_name='Elevationchange');em=pd.read_excel(wb,sheet_name='Plotemergence%')
    k=['Plot_ID','Block','Restoration_scale_m²','Seeding_density/m²'];assert len(r)==144 and not r.duplicated(['Plot_ID','Year','Replicate']).any() and r.groupby(['Plot_ID','Year']).size().eq(4).all();assert np.allclose(r.Recruitment_success/r['Seeding_density/m²'],r.Recruitment_efficiency)
    p=r.groupby(k+['Year']).Recruitment_success.mean().unstack().reset_index().rename(columns={2020:'G1',2021:'G2'});assert len(p)==18 and p.groupby(k[1:]).size().eq(1).all() and (p[['G1','G2']]>0).all().all()
    assert len(pl)==90 and not pl.duplicated(['Plot_ID','Replicate_plant']).any() and pl.groupby('Plot_ID').size().eq(5).all()
    p=p.merge(pl.groupby(k)[['Spathes/plant','Plant_totaldryweight']].mean().reset_index(),on=k,validate='one_to_one').merge(e[k+['Elevationchange_March_July_centre_plot_m']],on=k,validate='one_to_one').merge(em[k+['%centre_plot_emerged_over_lowtide_waterlevel']],on=k,validate='one_to_one')
    p=p.rename(columns={k[2]:'scale',k[3]:'density','Spathes/plant':'spathes','Plant_totaldryweight':'mass','Elevationchange_March_July_centre_plot_m':'sediment_change','%centre_plot_emerged_over_lowtide_waterlevel':'dry_pct'})
    p['ratio']=p.G2/p.G1;p['log_ratio']=np.log(p.ratio);p['spathe_proxy']=p.G1*p.spathes;p['G2_per_proxy']=p.G2/p.spathe_proxy;p['log_spathes']=np.log(p.spathes);p['log_conversion']=np.log(p.G2_per_proxy);assert np.allclose(p.log_ratio,p.log_spathes+p.log_conversion)
    q=p.pivot(index=['Block','density'],columns='scale',values=['log_ratio','log_spathes','log_conversion','G1','G2','ratio']);assert len(q)==6
    contrasts={}
    for small in [4,40]:
        v={}
        for metric in ['log_ratio','log_spathes','log_conversion']:
            x=q[metric][400]-q[metric][small];v[metric]={'by_block_density':x.tolist(),'mean':float(x.mean()),'ratio':float(np.exp(x.mean())),'block_means':x.groupby(level=0).mean().tolist()}
        v['same_direction_ratio']=int((q['log_ratio'][400]>q['log_ratio'][small]).sum());contrasts[str(small)]=v
    for t in ['G1','G2','spathe_proxy','scale','density']:p['log_'+t]=np.log(p[t])
    mods={'training_mean':[],'initial_density':['log_density'],'design':['log_density','log_scale'],'first_generation':['log_G1'],'first_gen_scale':['log_G1','log_scale'],'spathe_proxy':['log_spathe_proxy'],'first_gen_plus_spathes':['log_G1','log_spathes'],'first_gen_spathes_scale':['log_G1','log_spathes','log_scale'],'first_gen_dry':['log_G1','dry_pct'],'first_gen_spathes_dry':['log_G1','log_spathes','dry_pct']}
    cv={}
    for alpha in [.1,1,10]:
        cv[str(alpha)]={}
        for name,cols in mods.items():
            pred=[];obs=[];fold=[]
            for block in sorted(p.Block.unique()):
                a=p[p.Block.ne(block)];b=p[p.Block.eq(block)];y=b.log_G2.to_numpy();yp=np.full(len(b),a.log_G2.mean()) if not cols else make_pipeline(StandardScaler(),Ridge(alpha=alpha)).fit(a[cols],a.log_G2).predict(b[cols]);obs.extend(y);pred.extend(yp);fold.append(float(np.mean((y-yp)**2)))
            cv[str(alpha)][name]={'rmse_log':float(np.sqrt(np.mean((np.array(obs)-np.array(pred))**2))),'fold_mse':fold}
    res={'source':f,'plots':len(p),'blocks':3,'means':p.groupby(['scale','density'])[['G1','G2','ratio','spathes','dry_pct','sediment_change','G2_per_proxy']].mean().reset_index().to_dict('records'),'contrasts_400_vs':contrasts,'cv':cv,'notes':['Ratios use observed density at July 2020 and August 2021, not individual reproduction or survival.','Spathe production proxy uses July density times August spathes per plant, not actual seed input.','Accounting not mediation. Three blocks, no external validation.']}
    p.to_csv(OUT/'generation_plot.csv',index=False);(OUT/'generation.json').write_text(json.dumps(res,indent=2,allow_nan=False)+'\n');return res
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('map',type=Path);a.add_argument('--out',type=Path,required=True);v=a.parse_args();print(json.dumps(run(v.map,v.out),indent=2))
