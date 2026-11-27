#!/usr/bin/env python3
"""Separate recorded uninterrupted presence and re-recording on complete annual triples."""
import collections as C, importlib.util, json, math, statistics as ST, sys
from pathlib import Path
p=Path(__file__).with_name('223_life_history_common_support.py')
sp=importlib.util.spec_from_file_location('p223',p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
def summarize(rows,step):
    counts=C.defaultdict(C.Counter);pair_clusters=C.defaultdict(lambda:C.defaultdict(list));tr=0;co=0
    for key,ys in rows.items():
        for y,(s,d) in ys.items():
            if not {y+step,y+step*2}<=ys.keys():continue
            t,d1=ys[y+step];u,d2=ys[y+step*2];assert d==d1==d2
            tr+=1
            for x in s:counts[x]['1'+str(int(x in t))+str(int(x in u))]+=1
            p={x for x in s if m.m.TRAIT[x]=='P'};q=s-p
            if not p or not q:continue
            co+=1
            for label,f in [('endpoint',lambda a:a in u),('continuous',lambda a:a in t and a in u),('reappearance',lambda a:a not in t and a in u),('first_loss',lambda a:a not in t)]:
                diff=ST.mean(f(x) for x in p)-ST.mean(f(x) for x in q)
                pair_clusters[label][key[0]].append(diff)
    stats={k:m.m.boot_cluster(v,seed=20261128) for k,v in pair_clusters.items()}
    if stats:assert abs(stats['endpoint']['mean']-stats['continuous']['mean']-stats['reappearance']['mean'])<1e-10
    def rates(c):
        n=sum(c.values());g=c['100']+c['101'];r=c['110']+c['111']
        return {'n':n,'counts':{k:c[k] for k in ('100','101','110','111')},'continuous':c['111']/n,'reappearance_joint':c['101']/n,'endpoint':(c['111']+c['101'])/n,'first_nonrecord':g/n,'rerecord_after_nonrecord':c['101']/g if g else None,'retention_after_record':c['111']/r if r else None}
    byclass=C.defaultdict(C.Counter)
    for x,v in counts.items():byclass[m.m.TRAIT[x]].update(v)
    return {'step':step,'complete_triples':tr,'initial_cooccurrence_triples':co,'paired_equal_station':stats,'taxa':{x:rates(v) for x,v in sorted(counts.items())},'classes':{x:rates(v) for x,v in sorted(byclass.items())}}
def main():
    rows=m.read(sys.argv[1]);res={name:summarize(rows[n],k) for name,n,k in [('A_annual','A',1),('A_two_year','A',2),('B_two_year','B',2)]}
    out={'archive':m.m.A,'panels':res,'limits':['Three actual observation years required, no imputation. 101 denotes re-recording after non-recording, not demographic recolonization. 111 denotes consecutive detections, not survival of the same individual.','Class-level rates are pooled taxon incidences. Paired analysis uses initial cooccurring P and nonP taxa and equal coordinate means; source richness, detectability, species identity and spatial dependence remain. No inference from small B panel.','Existing Torres data, post-hoc. No new Tampa mechanism mining.']}
    Path(sys.argv[2]).write_text(json.dumps(out,indent=2,allow_nan=False)+'\n');print('TRAJECTORY_JSON '+json.dumps(out,allow_nan=False))
if __name__=='__main__':main()
