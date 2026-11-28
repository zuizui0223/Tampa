#!/usr/bin/env python3
"""Independent Moreton photo-survey and MarineGEO plant-animal linkage analysis."""
import collections as C,csv,hashlib,io,json,math,random,statistics as S,sys,urllib.request as U,zipfile
from pathlib import Path
import numpy as np
from scipy.stats import spearmanr
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler

def sha(b):return hashlib.sha256(b).hexdigest()
def q(v):return [float(x) for x in np.quantile(v,[.25,.5,.75])] if len(v) else None
def rho(x,y):
    if len(x)<4 or len(set(x))<2 or len(set(y))<2:return None
    return float(spearmanr(x,y).statistic)
def boot(v):
    if len(v)<5:return None
    a=np.array(v);r=np.random.default_rng(20261128);return [float(x) for x in np.quantile(r.choice(a,(5000,len(a))).mean(axis=1),[.025,.975])]
def read_photo(yr,doi,n,out):
    url='https://doi.pangaea.de/10.1594/PANGAEA.'+doi+'?format=textfile'
    with U.urlopen(U.Request(url,headers={'User-Agent':'Tampa-seagrass-research/1.0','Accept':'text/plain','Accept-Encoding':'identity'}),timeout=45) as r:b=r.read(30_000_001)
    assert len(b)<30_000_001
    text=b.decode('utf-8-sig');assert '*/' in text
    tab=text.split('*/',1)[1].strip('\r\n');rr=list(csv.reader(io.StringIO(tab),delimiter='\t'));h=rr[0];rows=[x for x in rr[1:] if x]
    assert len(rows)==n,(len(rows),n,h)
    expected={0:'ID',1:'Date/Time',2:'Latitude',3:'Longitude',4:'UTM east',5:'UTM north',8:'Seagr cov',9:'Seagr in epiphyte cov',15:'C. serrulata cov',16:'H. uninervis cov',17:'H. ovalis cov',18:'H. spinulosa cov',19:'S. isoetifolium cov',20:'Z. muelleri cov',21:'Seagr detritus cov',22:'Seagr indet cov',23:'C. serrulata + algae cov',24:'H. uninervis + algae cov',25:'H. ovalis + algae cov',26:'H. spinulosa + algae cov',27:'S. isoetifolium + epiphyte cov',28:'S. isoetifolium + hairy algae cov',29:'Z. muelleri + algae cov',30:'Z. muelleri + dark cov'}
    for k,v in expected.items():assert h[k].strip().lower().startswith(v.lower()),(k,h[k],v)
    a=[];qc=C.Counter();errs=[]
    for x in rows:
        assert len(x)==len(h) and x[1].startswith(str(yr)+'-06')
        if any(x[i].strip()=='' for i in [4,5,8,9]+list(range(15,31))):qc['missing']+=1;continue
        vals=[float(x[i]) for i in [8,9]+list(range(15,31))]
        if not all(math.isfinite(z) and 0<=z<=100 for z in vals):qc['invalid']+=1;continue
        clean=np.array([float(x[i]) for i in range(15,21)])
        dark=np.array([float(x[i]) for i in (23,24,25,26)]+[float(x[27])+float(x[28]),float(x[29])+float(x[30])])
        species=clean+dark;total=float(x[8])+float(x[9]);det=float(x[21]);ind=float(x[22])
        errs.append([total-species.sum(),total-species.sum()-ind,total-species.sum()-ind-det,float(x[9])-dark.sum()])
        a.append((float(x[4]),float(x[5]),x[0],total,float(x[9]),species))
    (out/('moreton_'+str(yr)+'.tsv')).write_bytes(b)
    return a,{'sha256':sha(b),'rows':n,'valid':len(a),'qc':dict(qc),'transects':len({x[2] for x in a}),'header':h,'zone':sorted({x[6] for x in rows}),'closure_quantiles':[q(x) for x in np.array(errs).T]}
def cellmap(a,width,shift):
    d=C.defaultdict(list)
    for x,y,tr,total,dark,sp in a:d[(math.floor((x+shift)/width),math.floor((y+shift)/width))].append((total,dark,sp))
    return {k:(len(v),float(np.mean([x[0] for x in v])),float(np.mean([x[1] for x in v])),np.mean([x[2] for x in v],axis=0)) for k,v in d.items()}
def photo_compare(a,b,width,shift,minn):
    aa=cellmap(a,width,shift);bb=cellmap(b,width,shift)
    kk=sorted(k for k in aa.keys()&bb.keys() if min(aa[k][0],bb[k][0])>=minn)
    if not kk:return {'n':0}
    x=[aa[k] for k in kk];y=[bb[k] for k in kk]
    v=np.array([r[3] for r in x]);w=np.array([r[3] for r in y]);s=v.sum(axis=1);t=w.sum(axis=1)
    total=np.array([r[1] for r in x]);other=np.array([r[1] for r in y])
    eligible=(s>0)&(t>0);stable=eligible&(abs(other-total)<=10)
    diff=w-v;den=np.abs(diff).sum(axis=1);mask=eligible&(den>1e-10)
    cancel=1-abs(diff.sum(axis=1)[mask])/den[mask]
    prop_v=v[eligible]/s[eligible,None];prop_w=w[eligible]/t[eligible,None];bc=.5*abs(prop_v-prop_w).sum(axis=1)
    sc=.5*abs(v[stable]/s[stable,None]-w[stable]/t[stable,None]).sum(axis=1)
    return {'n':len(kk),'photos':[sum(r[0] for r in x),sum(r[0] for r in y)],'total_abs_change_q':q(abs(other-total)),'named_both_positive':int(eligible.sum()),'total_cover_rho':rho(total.tolist(),other.tolist()),'composition_bray_q':q(bc),'stable_cover_both_named_n':int(stable.sum()),'stable_cover_bray_q':q(sc),'stable_cover_bray_ge_0_25':int((sc>=.25).sum()),'stable_cover_bray_ge_0_5':int((sc>=.5).sum()),'cancellation_q':q(cancel),'species_mean_change':diff.mean(axis=0).tolist(),'details':[{'cell':list(k),'n0':aa[k][0],'n1':bb[k][0],'total0':aa[k][1],'total1':bb[k][1],'sp0':aa[k][3].tolist(),'sp1':bb[k][3].tolist()} for k in kk]}
def marinegeo(path):
    z=zipfile.ZipFile(path);b=z.read(next(x for x in z.namelist() if x.endswith('marinegeo.zip')));assert sha(b)=='d54938eed357e27ebd456dfd7d50c0506e60e8345b524809711b91f8c0cee29e'
    z=zipfile.ZipFile(io.BytesIO(b));h={'event.txt':'3bef0b191f395141bb926f2c3d277e2bbe42d1f7f12861c9a5f28e06663cf048','occurrence.txt':'6656a636f74e5658dac1c9393e41f424cf31e95cc691ceaab901fb0d35b03a55','extendedmeasurementorfact.txt':'264070846a202902cd5aa5799a82f8c94295119d790de130b78b5df5cab5824d'}
    def read(n):raw=z.read(n);assert sha(raw)==h[n];return list(csv.DictReader(io.StringIO(raw.decode('utf-8-sig')),delimiter='\t'))
    e,o,m=map(read,h);assert (len(e),len(o),len(m))==(492,2534,2976)
    ev={x['id']:x for x in e};occ={x['occurrenceID']:x for x in o}
    grass={'Thalassia','Syringodium','Halodule','Halophila'}
    d=C.defaultdict(lambda:C.defaultdict(dict));qc=C.Counter()
    for x in m:
        eid=x['id'];a=occ[x['occurrenceID']];assert a['id']==eid and eid in ev
        typ=x['measurementType'];sp=a['scientificName'];status=a['occurrenceStatus']
        if a['kingdom']=='Animalia' and typ=='epifaunaAbundance':key='fauna';assert x['measurementUnit']=='number g-1 macrophyte'
        elif a['genus'] in grass and typ in ('percentCover','shootDensity','shootLength'):key=typ
        else:continue
        try:v=float(x['measurementValue']);assert math.isfinite(v) and v>=0
        except Exception:qc['invalid_numeric']+=1;continue
        if status=='absent' and v!=0:qc['absent_nonzero']+=1;continue
        if status not in ('present','absent'):qc['unknown_status']+=1;continue
        if sp in d[eid][key] and d[eid][key][sp]!=v:raise ValueError('duplicate conflicting measurement '+eid+' '+sp)
        d[eid][key][sp]=v
    rows=[]
    for eid,t in sorted(d.items()):
        if not t.get('percentCover') or not t.get('fauna'):continue
        parts=eid.split(':');assert len(parts)==5
        loc=':'.join([parts[1].rsplit('_',1)[0],parts[2]])
        year=int(ev[eid]['eventDate'][:4]);tran=':'.join(parts[:4])
        cover=sum(t['percentCover'].values());av=sum(t['fauna'].values())
        den=sum(t['shootDensity'].values()) if t.get('shootDensity') else None
        le=[v for k,v in t.get('shootLength',{}).items() if v>0 and t['percentCover'].get(k,0)>0]
        rows.append({'eid':eid,'site':loc,'country':ev[eid]['countryCode'],'year':year,'transect_visit':tran,'cover':cover,'density':den,'length':S.mean(le) if le else None,'positive_fauna_taxa':sum(v>0 for v in t['fauna'].values()),'animal_per_g_sum':av,'cover_richness':sum(v>0 for v in t['percentCover'].values()),'thalassia_cover':t['percentCover'].get('Thalassia testudinum',0),'animal_positive_names':sorted(k for k,v in t['fauna'].items() if v>0)})
    def compare(xfield,yfield):
        rr=[x for x in rows if x[xfield] is not None and x[yfield] is not None]
        g=C.defaultdict(list)
        for x in rr:g[x['transect_visit']].append(x)
        rs=[]
        for k,v in g.items():
            a=rho([x[xfield] for x in v],[x[yfield] for x in v])
            if a is not None:rs.append((v[0]['site'],k,a,len(v)))
        by=C.defaultdict(list)
        for s,k,r,n in rs:by[s].append(r)
        sr=[S.mean(v) for v in by.values()]
        return {'rows':len(rr),'sites':len({x['site'] for x in rr}),'pooled_rho':rho([x[xfield] for x in rr],[x[yfield] for x in rr]),'within_transect_correlations':len(rs),'within_site_clusters':len(sr),'equal_site_rho':S.mean(sr) if sr else None,'site_boot_ci':boot(sr),'transect_rows':rs}
    def cv(features,target):
        rr=[x for x in rows if all(x[k] is not None for k in features+[target])]
        sites=sorted({x['site'] for x in rr})
        if len(sites)<4:return {'sites':len(sites),'rows':len(rr),'estimable':False}
        per=[]
        for s in sites:
            train=[x for x in rr if x['site']!=s];test=[x for x in rr if x['site']==s]
            def X(a,add):return np.array([[int(x['country']=='PA'),x['year']-2021]+([math.log1p(x[k]) for k in features] if add else []) for x in a])
            yt=np.array([math.log1p(x[target]) for x in train]);yv=np.array([math.log1p(x[target]) for x in test])
            e=[]
            for add in [False,True]:
                a,b=X(train,add),X(test,add);sc=StandardScaler().fit(a);m=Ridge(alpha=3).fit(sc.transform(a),yt);p=m.predict(sc.transform(b));e.append(float(np.mean((p-yv)**2)))
            per.append({'site':s,'n':len(test),'base_mse':e[0],'aug_mse':e[1]})
        aa=S.mean(x['base_mse'] for x in per);bb=S.mean(x['aug_mse'] for x in per)
        return {'estimable':True,'rows':len(rr),'sites':len(sites),'relative_skill':1-bb/aa if aa else None,'base_mse':aa,'aug_mse':bb,'sites_improved':sum(x['aug_mse']<x['base_mse'] for x in per),'per_site':per}
    return {'qc':dict(qc),'rows':len(rows),'sites':len({x['site'] for x in rows}),'country_year_counts':{str(k):v for k,v in C.Counter((x['country'],x['year']) for x in rows).items()},'site_counts':dict(C.Counter(x['site'] for x in rows)),'correlations':{x+'|'+y:compare(x,y) for x in ('cover','density','length','cover_richness','thalassia_cover') for y in ('animal_per_g_sum','positive_fauna_taxa')},'cv':{'+'.join(xs)+'|'+y:cv(list(xs),y) for xs in [('cover',),('cover','length'),('cover','density')] for y in ('animal_per_g_sum','positive_fauna_taxa')},'ledger':rows}
def main():
    out=Path('macro_new');out.mkdir(exist_ok=True)
    result={}
    try:result['marinegeo']=marinegeo(sys.argv[1])
    except Exception as e:result['marinegeo']={'STOP':repr(e)}
    try:
        a,qa=read_photo(2011,'846143',4150,out);b,qb=read_photo(2012,'846146',3748,out)
        result['moreton']={'source':[qa,qb],'grid':{str((w,s,n)):photo_compare(a,b,w,s,n) for w in (100,200,500) for s in (0,w/2) for n in (3,5)}}
    except Exception as e:result['moreton']={'STOP':repr(e)}
    (out/'results.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    compact=json.loads(json.dumps(result))
    if 'ledger' in compact['marinegeo']:del compact['marinegeo']['ledger']
    for x in compact['marinegeo'].get('correlations',{}).values():x.pop('transect_rows',None)
    for x in compact['marinegeo'].get('cv',{}).values():x.pop('per_site',None)
    for x in compact['moreton'].get('grid',{}).values():x.pop('details',None)
    print('MACRO_JSON '+json.dumps(compact,allow_nan=False))
if __name__=='__main__':main()
