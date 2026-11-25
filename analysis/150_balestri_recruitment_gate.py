#!/usr/bin/env python3
"""Post-hoc pot-level survival accounting, Balestri et al. 2021.
Original DOI 10.1111/1365-2664.13980, data DOI 10.5061/dryad.t76hdr81n.
Separate germination and seedling experiments, not linked seed trajectories.
"""
import argparse, hashlib, io, itertools, json, math, statistics as st
from collections import defaultdict
from pathlib import Path
import openpyxl
SHA='cbfc07553ee6e071e83579784171c66d6dab8dcc589e2bdb92ee11d74d1aa2b1'
DENSITY={'Low':1,'Medium':2,'High':4}
def describe(counts,n):
    positive=[x for x in counts if x>0]
    return dict(pots=len(counts),initial_seedlings=n*len(counts),survivors=sum(counts),
        surviving_pots=len(positive),mean_survival_fraction=st.mean(counts)/n,
        occupied_pot_fraction=len(positive)/len(counts),mean_surviving_seedlings_per_pot=st.mean(counts),
        mean_survivors_per_occupied_pot=st.mean(positive) if positive else None,observed_counts=counts)
def perm(a,b):
    # Descriptive two-sided exchangeability sensitivity for fixed density.
    allv=a+b;n=len(a);obs=abs(st.mean(b)-st.mean(a));vals=[]
    for ids in itertools.combinations(range(len(allv)),n):
        k=set(ids);vals.append(abs(st.mean(allv[i] for i in k)-st.mean(v for i,v in enumerate(allv) if i not in k)))
    return sum(v>=obs-1e-12 for v in vals)/len(vals)
def analyze(raw):
    if hashlib.sha256(raw).hexdigest()!=SHA:raise ValueError('source drift')
    w=openpyxl.load_workbook(io.BytesIO(raw),read_only=True,data_only=True)
    assert w.sheetnames==['P. oceanica germination exp','P. oceanica seedling exp','C. nodosa data']
    gr=list(w.worksheets[0].values);sr=list(w.worksheets[1].values);cr=list(w.worksheets[2].values);w.close()
    assert gr[0]==('Planting density','Replicate','Germination percentage') and len(gr)==37
    assert sr[0][:3]==('Seedling density','Cymodocea','Final survival (%)') and len(sr)==25
    assert cr[0]==('Seedling density','Replicate','Final number of shoots','Leaf length (cm)','Total biomass (g)') and len(cr)==17
    germ=defaultdict(list);ids=set()
    for d,i,x in gr[1:]:
        assert d in {'low','medium','high'} and 0<=x<=100 and (d,i) not in ids;ids.add((d,i));germ[d].append(x)
    assert all(len(germ[k])==12 for k in ('low','medium','high'))
    pots=defaultdict(list);inconsistent=[]
    for i,r in enumerate(sr[1:],2):
        d,c,x=r[:3];assert d in DENSITY and c in {'absence','presence'}
        n=DENSITY[d];k=round(x*n/100);assert 0<=k<=n and math.isclose(k/n*100,x,abs_tol=1e-9)
        pots[d,c].append(k)
        if (k>0)!=(r[9]>0):inconsistent.append({'excel_row':i,'density':d,'partner':c,'surviving_seedlings':k,'reported_biomass_g':r[9]})
    assert len(pots)==6 and all(len(v)==4 for v in pots.values())
    result={}
    for d,n in DENSITY.items():
        a,b=[describe(pots[d,c],n) for c in ('absence','presence')]
        p,q=a['occupied_pot_fraction'],b['occupied_pot_fraction'];u,v=a['mean_survivors_per_occupied_pot'],b['mean_survivors_per_occupied_pot']
        delta=b['mean_surviving_seedlings_per_pot']-a['mean_surviving_seedlings_per_pot']
        decomp=None if u is None or v is None else {'occupied_pot_component':(q-p)*(u+v)/2,'conditional_survivor_count_component':(v-u)*(p+q)/2}
        if decomp is not None:assert math.isclose(sum(decomp.values()),delta,abs_tol=1e-12)
        result[d]={'absence':a,'presence':b,'difference_individual_survival_pp':100*(b['mean_survival_fraction']-a['mean_survival_fraction']),
          'difference_occupied_pot_pp':100*(q-p),'difference_survivors_per_pot':delta,
          'symmetric_accounting':decomp,'two_sided_pot_label_permutation_p_unadjusted':perm(pots[d,'absence'],pots[d,'presence'])}
    comp=defaultdict(list)
    for d,i,shoots,length,b in cr[1:]:comp[d].append((shoots,b))
    assert set(comp)=={'Alone','Low','Medium','High'} and all(len(v)==4 for v in comp.values())
    return {'status':'posthoc_original_pot_level_recruitment_accounting','source_sha256':SHA,
        'germination_mean_pct':{k:st.mean(v) for k,v in germ.items()},'seedling_results':result,
        'companion_group_means':{k:{'shoots':st.mean(x[0] for x in v),'biomass_g':st.mean(x[1] for x in v)} for k,v in comp.items()},
        'survival_biomass_positive_status_disagreements':inconsistent,
        'boundaries':['Four pots per cell within one outdoor tank; pot is experimental unit, not seedlings or independent meadows.',
          'Occupancy means at least one surviving planted seedling per pot, not meadow extent or probability in nature.',
          'Symmetric product accounting is descriptive, not causal mediation. Conditional survivor count undefined if no pots survive.',
          'Pairwise exact permutations are exploratory and unadjusted, under pot-label exchangeability; do not substitute for original factorial analysis.',
          'Germination and seedling experiments use distinct batches and densities; no multiplication of stages.',
          'Two source rows disagree on survival vs positive biomass; no repair, biomass-survival fit or joined cross-species pot outcomes.',
          'No genetic marker data or genotype-specific survival; not postzygotic genetic selection.']}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--input',type=Path,default=Path('reproductive_input/balestri/Copia_di_Dataset_publication.xlsx'));a=p.parse_args()
    print(json.dumps(analyze(a.input.read_bytes()),indent=2,sort_keys=True,allow_nan=False))
