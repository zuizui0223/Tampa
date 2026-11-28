#!/usr/bin/env python3
"""Moreton provider-table audit and independent common-cell analysis, not fixed-point survival."""
import collections as C,csv,io,importlib.util,json,math,sys,urllib.request as U
from pathlib import Path
import numpy as np
p=Path(__file__).with_name('227_independent_meadow_macro.py')
sp=importlib.util.spec_from_file_location('m227',p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
EXPECTED={0:'ID',1:'Date/Time',2:'Latitude',3:'Longitude',4:'UTM east',5:'UTM north',8:'Seagr cov',9:'Seagr in epiphyte cov',15:'C. serrulata cov',16:'H. uninervis cov',17:'H. ovalis cov',18:'H. spinulosa cov',19:'S. isoetifolium cov',20:'Z. muelleri cov',21:'Seagr detritus cov',22:'Seagr indet cov',23:'C. serrulata + algae cov',24:'H. uninervis + algae cov',25:'H. ovalis + algae cov',26:'H. spinulosa + algae cov',27:'S. isoetifolium + epiphyte cov',28:'S. isoetifolium + hairy algae cov',29:'Z. muelleri + algae cov',30:'Z. muelleri + dark cov'}
def get(yr,doi,descriptor_n,out):
    url='https://doi.pangaea.de/10.1594/PANGAEA.'+doi+'?format=textfile'
    with U.urlopen(U.Request(url,headers={'User-Agent':'Tampa-seagrass-research/1.0','Accept':'text/plain','Accept-Encoding':'identity'}),timeout=60) as r:b=r.read(30_000_001)
    assert len(b)<30_000_001
    (out/('moreton_'+str(yr)+'.tsv')).write_bytes(b)
    s=b.decode('utf-8-sig');assert '*/' in s;rr=list(csv.reader(io.StringIO(s.split('*/',1)[1].strip('\r\n')),delimiter='\t'));h=rr[0];rows=[x for x in rr[1:] if x]
    for k,v in EXPECTED.items():assert h[k].strip().lower().startswith(v.lower()),(k,h[k],v)
    assert all(len(x)==len(h) for x in rows)
    a=[];qc=C.Counter();errs=[];byurl=C.defaultdict(list);dates=C.Counter(x[1][:10] for x in rows);zones=C.Counter(x[6] for x in rows)
    for x in rows:
        if not x[1].startswith(str(yr)+'-06'):qc['outside_campaign']+=1;continue
        if not x[7].strip():qc['missing_photo_id']+=1;continue
        byurl[x[7]].append(x)
    for url,vs in sorted(byurl.items()):
        if len({tuple(x) for x in vs})>1:qc['conflicting_photo_id_rows']+=len(vs);continue
        qc['identical_duplicate_rows']+=len(vs)-1
        x=vs[0]
        try:
            east,north,lat,lon=map(float,[x[4],x[5],x[2],x[3]])
            assert all(math.isfinite(z) for z in (east,north,lat,lon))
            assert -27.6<=lat<=-27.2 and 153.2<=lon<=153.6
            assert 500000<=east<=600000 and 6900000<=north<=7100000
        except (ValueError,AssertionError):qc['invalid_coordinate']+=1;continue
        try:vals=[float(x[i]) for i in [8,9]+list(range(15,31))]
        except ValueError:qc['missing_or_nonnumeric_cover']+=1;continue
        if not all(math.isfinite(z) and 0<=z<=100 for z in vals):qc['invalid_cover']+=1;continue
        clean=np.array([float(x[i]) for i in range(15,21)])
        dark=np.array([float(x[i]) for i in (23,24,25,26)]+[float(x[27])+float(x[28]),float(x[29])+float(x[30])])
        species=clean+dark;total=float(x[8])+float(x[9]);det=float(x[21]);ind=float(x[22])
        errs.append([total-species.sum(),total-species.sum()-ind,total-species.sum()-ind-det,float(x[9])-dark.sum()])
        if total>100.001 or species.sum()>100.001:qc['invalid_sum']+=1;continue
        a.append((east,north,x[0],total,float(x[9]),species))
    assert len(a)+sum(qc.values())==len(rows),(len(a),qc,len(rows))
    return a,{'url':url,'sha256':m.sha(b),'provider_rows':len(rows),'descriptor_photos':descriptor_n,'difference':len(rows)-descriptor_n,'valid_unique_photo_rows':len(a),'qc':dict(qc),'dates':dict(dates),'zones':dict(zones),'unique_transects':len({x[2] for x in a}),'unique_locations':len({(x[0],x[1]) for x in a}),'closure_quantiles':[m.q(x) for x in np.array(errs).T] if errs else None,'closure_exact_fractions':[float(np.mean(abs(x)<=.011)) for x in np.array(errs).T] if errs else None,'header':h}
def main():
    out=Path('moreton_audit');out.mkdir(exist_ok=True)
    result={}
    try:
        a,qa=get(2011,'846143',4150,out);b,qb=get(2012,'846146',3748,out);result['source']=[qa,qb]
        if len(qa['zones'])!=1 or qa['zones']!=qb['zones'] or min(len(a),len(b))<100:raise ValueError('zone/coverage gate')
        # Keep different source totals explicit: these are provider table analyses, not paper photograph counts.
        result['grid']={}
        for w in (100,200,500):
            for s in (0,w/2):
                for n in (3,5):
                    k=str((w,s,n));v=m.photo_compare(a,b,w,s,n)
                    if v.get('details'):
                        ds=v['details'];named=[]
                        for d in ds:
                            x=np.array(d['sp0']);y=np.array(d['sp1'])
                            if x.sum()>0 and y.sum()>0 and abs(x.sum()-y.sum())<=10:named.append(float(.5*abs(x/x.sum()-y/y.sum()).sum()))
                        v['stable_named_total_n']=len(named);v['stable_named_total_bray_q']=m.q(named);v['stable_named_total_bray_ge_025']=sum(x>=.25 for x in named)
                    result['grid'][k]=v
    except Exception as e:result['STOP']=repr(e)
    result['limits']=['Actual provider rows do not match paper photograph counts; no forced subsampling to paper count. Unique image URL required, exact duplicates collapsed and conflicting URL groups excluded.','Source-label cover and named-species sum separate; epiphyte/dark categories are not measured algae load. Cell-average composition based on sampled photos, not fixed quadrats or true survival. Grid shifts and thresholds response-open sensitivity, not spatially independent replications.']
    (out/'results.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    compact=json.loads(json.dumps(result))
    for q in compact.get('source',[]):q.pop('header',None)
    for x in compact.get('grid',{}).values():x.pop('details',None)
    print('MORETON_JSON '+json.dumps(compact,allow_nan=False))
if __name__=='__main__':main()
