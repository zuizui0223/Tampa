#!/usr/bin/env python3
"""Finite-sample paternal contribution diversity; not genetic effective population size.
Sgambelluri et al. 2024, Dryad 10.5061/dryad.dfn2z358x.
Two overlapping COLONY outputs, not independent experiments.
"""
import argparse,csv,hashlib,io,json,math
from collections import defaultdict
from pathlib import Path
FILES={
 'original':('Paternal_Heterozygosity.csv','71dcd6557604e2af34182d70deb5a6d15fb2edb8d5602e554168e2f5abf6bf89','by_spathe_dataset_slim.csv','ce02d8e5404a270177a82bc29910542406b2bbf25e4839dbc19ca0bc07746a14'),
 'high_locus':('Reduced_Paternal_Heterozygosity.csv','62c128849b0decc7e09d1e04a885aa58c7cabe33cb8d80042cf7d540e022fb8f','reduced_by_spathe.csv','15e34fc4483793a840ad20c35c898145a050b2f65d0512b10636b8fbb938a105')}

def read(root,name,sha):
    b=(root/name).read_bytes()
    if hashlib.sha256(b).hexdigest()!=sha:raise ValueError('source drift: '+name)
    reader=csv.DictReader(io.StringIO(b.decode('utf-8-sig')))
    return [{k.strip():v for k,v in row.items()} for row in reader]

def summary(counts,effort=100):
    N,G=sum(counts),len(counts)
    if not all(x>0 for x in counts) or not 1<=effort<=N:raise ValueError('invalid counts or effort')
    d2=N*N/sum(x*x for x in counts)
    q,r=divmod(N,G)
    balanced_sq=(G-r)*q*q+r*(q+1)**2
    balanced=N*N/balanced_sq
    collision=sum(x*(x-1) for x in counts)/(N*(N-1))
    min_collision=(balanced_sq-N)/(N*(N-1))
    E=sum(1-(math.comb(N-x,effort)/math.comb(N,effort) if N-x>=effort else 0) for x in counts)
    k=math.ceil(.2*G)
    return dict(sire_records=G,seed_contributions=N,observed_hill2=d2,hill2_over_sire_records=d2/G,
        maximum_hill2_fixed_N_G=balanced,hill2_over_maximum=d2/balanced,
        same_sire_probability_distinct_sampled_seeds=collision,minimum_same_sire_probability_fixed_N_G=min_collision,
        same_sire_probability_over_minimum=collision/min_collision if min_collision else None,
        top_sire_count=k,top_20pct_rounded_up_seed_share=sum(sorted(counts,reverse=True)[:k])/N,
        rarefaction_seed_effort=effort,expected_distinct_sires_at_effort=E)

def analyze(root):
    out={}
    for label,(f,h,sf,sh) in FILES.items():
        rows=read(root,f,h);sp=read(root,sf,sh)
        sites=defaultdict(list);ids=set();spids=set();spcounts=defaultdict(lambda:[0,0,0])
        for row in rows:
            site=int(row['Site']);sire=row['Sire'].strip();n=int(row['Seeds Fertilized']);st=row['Reproductive Strategy']
            if not sire or (site,sire) in ids or site not in (1,2,3) or n<1 or st not in ('Outcrossing','Selfing'):raise ValueError('unexpected sire key or contribution')
            ids.add((site,sire));sites[site].append((n,st))
        for row in sp:
            k=tuple(int(row[x]) for x in ('Site','Maternal ID','Rhipidium','Spathe'))
            if k in spids:raise ValueError('duplicate spathe key')
            spids.add(k);v=[int(row[x]) for x in ('Genotyped Seeds','Outcrossed Seeds','Selfed Seeds')]
            if v[0]!=v[1]+v[2]:raise ValueError('spathe count closure')
            for j,x in enumerate(v):spcounts[k[0]][j]+=x
        assert set(sites)==set(spcounts)=={1,2,3}
        per_site={}
        for site,values in sorted(sites.items()):
            a=summary([n for n,_ in values]);b=summary([n for n,st in values if st=='Outcrossing'])
            c=sum(n for n,st in values if st=='Selfing');s=spcounts[site]
            per_site[str(site)]={'all_sire_records':a,'outcross_labeled_sire_records':b,
                'source_labeled_selfing_seed_contributions':c,'spathe_counts_genotyped_outcrossed_selfed':s,
                'sire_minus_spathe_total':a['seed_contributions']-s[0],
                'outcross_label_minus_spathe_outcross':b['seed_contributions']-s[1],
                'self_label_minus_spathe_self':c-s[2]}
        out[label]={'source_sha256':h,'comparison_spathe_sha256':sh,'sire_records':len(rows),'spathe_records':len(sp),
            'total_seed_contributions':sum(v['all_sire_records']['seed_contributions'] for v in per_site.values()),
            'total_spathe_genotyped_seeds':sum(v['spathe_counts_genotyped_outcrossed_selfed'][0] for v in per_site.values()),'sites':per_site}
    assert out['high_locus']['sire_records']==180 and out['high_locus']['total_seed_contributions']==out['high_locus']['total_spathe_genotyped_seeds']==688
    assert out['original']['sire_records']==208 and out['original']['total_seed_contributions']==852 and out['original']['total_spathe_genotyped_seeds']==844
    return {'status':'posthoc_observed_paternal_representation','source_doi':'10.5061/dryad.dfn2z358x','datasets':out,
        'limits':['Primary high-locus cohort closes total contributions at each site; strategy-specific count closure is imperfect at two sites. Source-labeled sire strategy, not a reconstructed seed-level mating roster.',
         'Original sire table totals 852 while slim spathe table totals 844. Preserve discrepancy; use original only as separate descriptive sensitivity.',
         'Hill2 is inverse Simpson of observed contribution proportions; not effective population size, actual donor pool, true lifetime reproductive success or genetic transmission.',
         'Maximum is a deterministic integer-balanced allocation at fixed observed N and G, not a random mating null, test or bias correction.',
         'Rarefaction conditions on observed seed contribution counts; not unobserved sire richness or experimental standardization.',
         'Three sampled meadows, overlapping cohorts, no independent generality test. No seed mass or survival linked. Original paper already studied paternity skew.']}

def selftest():
    x=summary([2,2,2,2],4);assert x['observed_hill2']==4 and x['hill2_over_maximum']==1
    assert abs(x['same_sire_probability_distinct_sampled_seeds']-1/7)<1e-12
    y=summary([5,1,1,1],4);assert y['observed_hill2']<y['maximum_hill2_fixed_N_G']
    assert summary([1,1,1],3)['expected_distinct_sires_at_effort']==3

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path('external_reproductive/zostera_paternity'));a=p.parse_args();selftest()
    print(json.dumps(analyze(a.root),indent=2,sort_keys=True,allow_nan=False))
