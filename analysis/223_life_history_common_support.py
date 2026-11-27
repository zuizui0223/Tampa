#!/usr/bin/env python3
"""Common-support comparison of the same co-occurring species pairs, with matched intervals."""
import collections as C, hashlib, importlib.util, itertools, json, math, statistics as ST, sys, zipfile
from pathlib import Path
p=Path(__file__).with_name('222_life_history_persistence.py')
sp=importlib.util.spec_from_file_location('life222',p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
def read(path):
    b=Path(path).read_bytes();assert hashlib.sha256(b).hexdigest()==m.A
    with zipfile.ZipFile(path) as z:raw=z.read('torres_survey_points.geojson')
    assert hashlib.sha256(raw).hexdigest()==m.HASH['torres']
    rows=C.defaultdict(lambda:C.defaultdict(dict))
    for f in json.loads(raw)['features']:
        p=f['properties'];nm={'Torres Strait lobster surveys':'A','Torres Strait sea cucumber surveys':'B'}.get(p['Survey'])
        if nm is None:continue
        vals=[p[k] for k in m.CODES];assert all(v in (0,1) for v in vals)
        s=frozenset(k for k,v in zip(m.NAMES,vals) if v)
        assert len(s)==p['SG_species'] and bool(s)==bool(p['SG_present'])
        key=(tuple(f['geometry']['coordinates']),p['Method'],p['Custodian'],p['Month'])
        y=int(p['Year']);depth=float(p['Depth_MSL']);assert math.isfinite(depth)
        v=(s,depth)
        assert y not in rows[nm][key] or rows[nm][key][y]==v
        rows[nm][key][y]=v
    return rows
def build(rows,lag):
    pairs=[]
    for key,ys in sorted(rows.items(),key=lambda x:str(x[0])):
        for y,(s,d) in sorted(ys.items()):
            if y+lag not in ys:continue
            t,d1=ys[y+lag];assert d==d1
            if not s:continue
            pp=sorted(x for x in s if m.TRAIT[x]=='P');qq=sorted(s-set(pp))
            for a,b in itertools.product(pp,qq):
                pairs.append((key[0],y,d,a,b,int(a in t)-int(b in t),bool(t)))
    return pairs
def cells(p,year=False,width=None,both=False):
    r=C.defaultdict(lambda:C.defaultdict(list))
    for st,y,d,a,b,x,t in p:
        if both and not t:continue
        k=(a,b,y if year else None,math.floor(d/width) if width is not None else None)
        r[k][st].append(x)
    return r
def compare(a,b,year=False,width=None,min_st=1,both=False):
    aa=cells(a,year,width,both);bb=cells(b,year,width,both)
    shared=[k for k in sorted(aa.keys()&bb.keys()) if len(aa[k])>=min_st and len(bb[k])>=min_st]
    if not shared:return {'shared_cells':0,'A_cells':len(aa),'B_cells':len(bb),'estimable':False}
    rr=[]
    for k in shared:
        x=ST.mean(ST.mean(z) for z in aa[k].values());y=ST.mean(ST.mean(z) for z in bb[k].values())
        rr.append({'key':k,'A_stations':len(aa[k]),'B_stations':len(bb[k]),'A_diff':x,'B_diff':y,'A_incidences':sum(map(len,aa[k].values())),'B_incidences':sum(map(len,bb[k].values()))})
    return {'shared_cells':len(rr),'A_cells':len(aa),'B_cells':len(bb),'estimable':True,'A_equal_cell_diff':ST.mean(x['A_diff'] for x in rr),'B_equal_cell_diff':ST.mean(x['B_diff'] for x in rr),'A_incidence_fraction':sum(x['A_incidences'] for x in rr)/sum(len(z) for v in aa.values() for z in v.values()),'B_incidence_fraction':sum(x['B_incidences'] for x in rr)/sum(len(z) for v in bb.values() for z in v.values()),'rows':rr}
def main():
    rows=read(sys.argv[1]);a1=build(rows['A'],1);a2=build(rows['A'],2);b2=build(rows['B'],2)
    out={'pair_incidence_counts':{k:len(v) for k,v in [('A1',a1),('A2',a2),('B2',b2)]},'depth':{},'comparison':{}}
    for k,v in [('A1',a1),('A2',a2),('B2',b2)]:
        dd=sorted(x[2] for x in v);out['depth'][k]={'median':ST.median(dd),'range':[min(dd),max(dd)],'stations':len({x[0] for x in v}),'years':sorted({x[1] for x in v})}
    for name,a in [('A1_vs_B2',a1),('A2_vs_B2',a2)]:
        o={}
        for yr in [False,True] if name=='A2_vs_B2' else [False]:
            for width in [None,5,2]:
                for minimum in [1,3]:
                    for both in [False,True]:
                        o[str((yr,width,minimum,both))]=compare(a,b2,yr,width,minimum,both)
        out['comparison'][name]=o
    # Source-grounded Ruppia genus C sensitivity (Kilminster continuum); previously excluded pairs.
    # Use the original function again with explicit added genus rather than silently altering primary.
    m.GENUS['Ruppia']='C'
    tp,trait,audit=m.read_tampa();r=m.summarize(tp,trait)
    out['tampa_ruppia_sensitivity']={'audit':audit,'mapping':trait,'all':r['all'],'both_positive':r['both_positive'],'loss':r['loss'],'reference':m.reference(tp,trait),'reference_Halodule_C':m.reference(tp,{k:('C' if k.split()[0]=='Halodule' else v) for k,v in trait.items()})}
    out['limits']=['Post-hoc common support, not independent validation. Equal exact species-pair cells, station means within cells; multiple species pairs from same sites and calendar intervals are not independent. No inferential p-value.','2y endpoints allowed even if an intervening survey exists, unlike prior adjacent-visit diagnostic; no imputation. Exact calendar start year and coarse depth bins are references only. Sparse overlap cannot distinguish study protocol, species identity, environmental sorting or true stage-specific persistence.','Tampa Ruppia classified by genus, not local measured trait; no new causal model.']
    Path(sys.argv[2]).write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
    compact={**out,'comparison':{k:{j:{kk:vv for kk,vv in x.items() if kk!='rows'} for j,x in v.items()} for k,v in out['comparison'].items()}}
    print('MATCH_JSON '+json.dumps(compact,allow_nan=False))
if __name__=='__main__':main()
