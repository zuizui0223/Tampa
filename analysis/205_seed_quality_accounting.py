#!/usr/bin/env python3
"""Audit published endozoochory figure coordinates and original Canadian seed-core counts."""
import hashlib, io, json, sys, zipfile
from pathlib import Path
from itertools import combinations
import fitz
import pandas as pd

def verified(path, digest):
    b = Path(path).read_bytes()
    assert hashlib.sha256(b).hexdigest() == digest
    return zipfile.ZipFile(io.BytesIO(b))

def analyze(pdf_archive, canada_archive):
    z = verified(pdf_archive, '3c3575d833558f2d86c4f5ede16969dd4a8ba21231fae64c091f25773f4661c4')
    pdf = z.read('sumoski2012.pdf')
    assert hashlib.sha256(pdf).hexdigest() == '2911eaebc4861490f8fac5347c1c94d5f0a0e7cad5f56434e473eb09b11598b8'
    page = fitz.open(stream=pdf, filetype='pdf')[4]
    b1,t1,b2,t2 = 233.63897705078125,85.71197509765625,635.97900390625,485.1520080566406
    bars = [d for d in page.get_drawings() if d['type'] in ('fs','f') and d['fill']]
    g = sorted([d['rect'] for d in bars if d['type']=='fs' and d['fill'][0]<.7 and 75<d['rect'].x0<281 and 5<d['rect'].width<6 and abs(d['rect'].y1-b1)<.001],key=lambda r:r.x0)
    e = sorted([d['rect'] for d in bars if d['type']=='fs' and d['fill'][0]==1 and 75<d['rect'].x0<281 and 5<d['rect'].width<6 and d['rect'].y0>=t1-.001],key=lambda r:r.x0)
    c = sorted([d['rect'] for d in bars if d['rect'].x0>330 and 6<d['rect'].width<7 and abs(d['rect'].y1-b2)<.07],key=lambda r:r.x0)
    assert len(g)==len(e)==10 and len(c)==24
    labels = ['Fundulus 2009','Fundulus 2010','Sphoeroides 2009','Sphoeroides 2010','Sphoeroides 2011','Lagodon 2010','Lagodon 2011','Malaclemys 2009','Malaclemys 2010','Aythya 2011']
    fig1=[]
    for label,a,b in zip(labels,g,e):
        assert abs(a.x0-b.x0)<.001 and abs(a.y0-b.y1)<.002
        G=(b1-a.y0)/(b1-t1); E=min(1,(b1-b.y0)/(b1-t1))
        assert 0<=G<=E<=1
        fig1.append(dict(trial=label,excreted=E,germinated=G,germinated_per_excreted=G/E,unrecovered=1-E,excreted_not_germinated=E-G,post_excretion_dominates=E-G>1-E,margin=(E-G)-(1-E)))
    fig2=[]
    for j,i in enumerate([0,1,8,5,6,3,4,9]):
        G,C1,C2=[(b2-r.y0)/(b2-t2)*.8 for r in c[j*3:j*3+3]]
        assert abs(G-fig1[i]['germinated'])<.002
        fig2.append(dict(trial=labels[i],consumed=G,control1=C1,control2=C2,control1_kind='matrix+dye' if i==9 else 'matrix',control2_kind='matrix' if i==9 else 'seawater',break_even1=C1/G,break_even2=C2/G,lower_break_even1=max(0,C1-.005)/(G+.005),lower_break_even2=max(0,C2-.005)/(G+.005)))
    cz=verified(canada_archive,'8026c12f40414c2f34c01966b37d1946915c30dccef808a35e8b20a20081976b')
    inner=cz.read('canada_CSV.zip');assert hashlib.sha256(inner).hexdigest()=='9993a811fa2ab88d8e31dd8484b746ac76a1eb81f6d36b68415e7358e5115564'
    s=pd.read_csv(zipfile.ZipFile(io.BytesIO(inner)).open('CSV/Seed Biomass.csv'))
    assert len(s)==337 and not s.duplicated(['Site_Location','Date','Core_ID']).any()
    a=s[s.Seeds_assessed.notna()].copy();assert len(a)==156 and a[['Full_seeds','Seeds_assessed','Viable_seeds']].notna().all().all()
    assert (a.Viable_seeds>=0).all() and (a.Viable_seeds<=a.Seeds_assessed).all() and (a.Seeds_assessed<=a.Full_seeds).all()
    a['upper']=a.Viable_seeds+a.Full_seeds-a.Seeds_assessed
    pairs=dict(concordant=0,reversed=0,unresolved_or_tied=0)
    for _,sub in a.groupby(['Site_Location','Date']):
        for r,t in combinations(sub.itertuples(),2):
            if r.Full_seeds==t.Full_seeds:continue
            if r.Full_seeds<t.Full_seeds:r,t=t,r
            k='concordant' if r.Viable_seeds>t.upper else 'reversed' if r.upper<t.Viable_seeds else 'unresolved_or_tied'
            pairs[k]+=1
    canada=dict(assessed_cores=len(a),full=int(a.Full_seeds.sum()),assessed=int(a.Seeds_assessed.sum()),viable=int(a.Viable_seeds.sum()),viable_upper=int(a.upper.sum()),positive_full_cores=int((a.Full_seeds>0).sum()),positive_confirmed_cores=int((a.Viable_seeds>0).sum()),positive_possible_cores=int((a.upper>0).sum()),full_positive_guaranteed_no_viable=int(((a.Full_seeds>0)&(a.upper==0)).sum()),within_site_date_unequal_full_count_pairs=pairs)
    return dict(fig1=fig1,fig2=fig2,post_excretion_dominant_trials=sum(x['post_excretion_dominates'] for x in fig1),canada=canada)

if __name__=='__main__':
    result=analyze(sys.argv[1],sys.argv[2]);Path(sys.argv[3]).write_text(json.dumps(result,indent=2)+'\n')
