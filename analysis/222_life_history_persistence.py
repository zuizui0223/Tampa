#!/usr/bin/env python3
"""Cross-program life-history persistence: observed taxon histories, not demographic survival."""
import collections as C, csv, hashlib, importlib.util, itertools, json, math, random, statistics as ST, sys, zipfile
from pathlib import Path
A='31d4831e2efa3552e58db32a70fefccf6dcad5049e2bed4f2ca09d984b547e06'
HASH={'torres':'9727c28d4dafcd225a754f2439e010fe09f2835dfbeefe03b28cc5d8f940facf','shoalwater':'6a57c41ad14db93d64293214ca51fc76db3326eab38141c8c61f504ed58df552'}
CODES=['CR_PA','CS_PA','EA_PA','HC_PA','HD_PA','HO_PA','HS_PA','HT_PA','HU_PA','SI_PA','TC_PA','TH_PA','ZC_PA']
GBR=['C_ROTUNDAT','C_SERRULAT','E_ACOROIDE','H_CAPRICOR','H_DECIPIEN','H_OVALIS','H_SPINULOS','H_TRICOSTA','H_UNINERVI','S_ISOETIFO','T_CILIATUM','T_HEMPRICH','Z_CAPRICOR']
NAMES=['Cymodocea rotundata','Cymodocea serrulata','Enhalus acoroides','Halophila capricorni','Halophila decipiens','Halophila ovalis','Halophila spinulosa','Halophila tricostata','Halodule uninervis','Syringodium isoetifolium','Thalassodendron ciliatum','Thalassia hemprichii','Zostera muelleri subsp. capricorni']
# Udy et al 2018, Fig 5; H. capricorni not illustrated -> genus-based assignment, sensitivity excludes it.
TRAIT=dict(zip(NAMES,['O','O','P','C','C','C','C','C','O','O','P','P','O']))
GENUS={'Thalassia':'P','Enhalus':'P','Thalassodendron':'P','Posidonia':'P','Halophila':'C','Halodule':'O','Syringodium':'O','Cymodocea':'O','Zostera':'O'}
MONTHS={m.lower() for m in ['January','February','March','April','May','June','July','August','September','October','November','December']}
def read_australia(path):
    b=Path(path).read_bytes();assert hashlib.sha256(b).hexdigest()==A
    panels={};audit={}
    with zipfile.ZipFile(path) as z:
        for reg,expected in [('torres',28732),('shoalwater',27227)]:
            raw=z.read(reg+'_survey_points.geojson');assert hashlib.sha256(raw).hexdigest()==HASH[reg]
            fs=json.loads(raw)['features'];assert len(fs)==expected
            rows=C.defaultdict(lambda:C.defaultdict(list));qc=C.Counter();groups=C.Counter()
            for f in fs:
                p=f['properties'];st=tuple(f['geometry']['coordinates'])
                if reg=='torres':
                    program=p['Survey'];method=p['Method'];cust=p['Custodian'];month=str(p['Month']).lower().strip()
                    y=int(p['Year']);v=[p[k] for k in CODES];present=p['SG_present']
                    known=program in ('Torres Strait lobster surveys','Torres Strait sea cucumber surveys')
                    # For the two earlier audited programs month is unspecified, retain separate panels.
                    if not known and month not in MONTHS:qc['month_unknown']+=1;continue
                    if not all(x in (0,1) for x in v) or present not in (0,1):qc['missing_species']+=1;continue
                    if sum(v)!=p['SG_species'] or bool(sum(v))!=bool(present):qc['inconsistent']+=1;continue
                    key=(program,st,month,method,cust)
                else:
                    program=p['LOCATION'];method=p['SURVEY_MET'];cust=p['DATA_CUSTO'];month=str(p['MONTH']).lower().strip()
                    y=int(p['YEAR']);rawv=[str(p[k]).lower().strip() for k in GBR]
                    if month not in MONTHS:qc['month_unknown']+=1;continue
                    present=str(p['PRESENCE_A']).lower().strip()
                    if not all(x in ('yes','no') for x in rawv) or present not in ('present','absent'):qc['missing_species']+=1;continue
                    v=[x=='yes' for x in rawv]
                    if bool(sum(v))!=(present=='present'):qc['inconsistent']+=1;continue
                    key=(program,st,month,method,cust)
                if not all(k is not None and str(k).strip() not in ('','n/a','unknown') for k in (program,method,cust)):qc['missing_design']+=1;continue
                taxa=frozenset(n for n,x in zip(NAMES,v) if x)
                rows[key][y].append(taxa);qc['eligible_rows']+=1
            byprogram=C.defaultdict(list)
            for key,ys in sorted(rows.items(),key=lambda a:str(a[0])):
                program,coord,month,method,cust=key
                good={}
                for y,vs in ys.items():
                    if len(set(vs))!=1:qc['discordant_station_years']+=1;continue
                    good[y]=vs[0];qc['duplicate_identical']+=len(vs)-1
                lag=2 if reg=='torres' and program=='Torres Strait sea cucumber surveys' else 1
                for y in sorted(good):
                    # Do not bridge a conflicting/missing endpoint; require exact target interval.
                    if y+lag not in good:continue
                    if lag==2 and y+1 in ys:continue
                    byprogram[program].append((coord,program,y,y+lag,good[y],good[y+lag]))
            for program,pairs in sorted(byprogram.items()):
                npos=sum(bool(x[4]) for x in pairs);nst=len({x[0] for x in pairs if x[4]})
                groups[program]={'pairs':len(pairs),'initial_positive':npos,'positive_stations':nst}
                # No response-dependent program selection. 30 prior-positive pairs and 10 coordinates minimum.
                if npos>=30 and nst>=10:panels[reg+'|'+program]=pairs
            audit[reg]={'source_records':len(fs),'qc':dict(qc),'programs_with_repeats':dict(groups)}
    return panels,audit

def read_tampa():
    # Use existing source-pinned parser, unchanged raw source and exact eligible visit definition.
    p=Path(__file__).with_name('33_community_buffering.py')
    spec=importlib.util.spec_from_file_location('tampa33',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    parents,points,children,_=m.parse_event(m.fetch(m.FILES['event']))
    assert len(parents)==1497 and len({v['node_id'] for v in parents.values()})==71
    occ=m.parse_occurrence(m.fetch(m.FILES['occurrence']),set(points))
    rows=C.defaultdict(lambda:C.defaultdict(list));alltaxa=C.Counter()
    for eid,pt in points.items():
        par=parents[pt['parent_id']]
        s=frozenset(occ.get(eid,{}).get('seagrass_names',set()))
        alltaxa.update(s)
        rows[(par['node_id'],pt['point_id'])][par['year']].append(s)
    pairs=[];qc=C.Counter()
    for (node,mark),ys in sorted(rows.items()):
        good={}
        for y,vs in ys.items():
            if len(set(vs))!=1:qc['discordant_full_composition']+=1;continue
            good[y]=vs[0]
        for y,s in sorted(good.items()):
            if y+1 in good:pairs.append((node,mark,y,y+1,s,good[y+1]))
    mapping={s:GENUS[s.split()[0]] for s in alltaxa if s.split()[0] in GENUS}
    # Full-record taxa must be classified for a pair; unknowns never silently removed.
    keep=[x for x in pairs if (x[4]|x[5])<=mapping.keys()]
    return keep,mapping,{'original_point_years':sum(map(len,rows.values())),'all_taxa':dict(alltaxa),'qc':dict(qc),'pairs':len(pairs),'kept':len(keep)}

def boot_cluster(values,seed=20261128,n=3000):
    # Equal clusters; cluster means of already-paired outcomes, not independent taxa.
    if not values:return None
    a=[ST.mean(v) for v in values.values()];r=random.Random(seed)
    sim=sorted(ST.mean(r.choices(a,k=len(a))) for _ in range(n))
    return {'clusters':len(a),'mean':ST.mean(a),'ci95':[sim[int(.025*(n-1))],sim[int(.975*(n-1))]]}
def summarize(pairs,trait):
    result={};loss=C.Counter();classes=C.defaultdict(C.Counter);taxa=C.defaultdict(C.Counter)
    # Group retention and selective disappearance on the same source-positive pair.
    for cluster,mark,y,z,s,t in pairs:
        if not (s|t)<=trait.keys():continue
        tc={trait[x] for x in t}
        for x in s:
            g=trait[x];k=taxa[x];k['prior']+=1;k['same']+=x in t
            k['loss_while_any']+=x not in t and bool(t)
            k['loss_same_class']+=x not in t and g in tc
            if x not in t:
                loss['total']+=1
                loss['bare']+=not t
                loss['same_class']+=g in tc
                loss['other_class_only']+=bool(t) and g not in tc
        for g in {trait[x] for x in s}:
            classes[g]['prior_pairs']+=1;classes[g]['same_class']+=g in tc
            classes[g]['any_grass']+=bool(t)
    assert loss['total']==loss['bare']+loss['same_class']+loss['other_class_only']
    result['loss']=dict(loss);result['classes']={k:dict(v) for k,v in sorted(classes.items())};result['taxa']={k:dict(v) for k,v in sorted(taxa.items())}
    # Within exactly the same initial cooccurrence, compare retained fractions of P vs non-P.
    # Distinguish all initial cooccurrences from both grass-positive endpoint sensitivity.
    for condition in ['all','both_positive']:
        d=C.defaultdict(list);n=0;ds=[]
        for cluster,mark,y,z,s,t in pairs:
            if not (s|t)<=trait.keys() or (condition=='both_positive' and not t):continue
            p={x for x in s if trait[x]=='P'};q=s-p
            if not p or not q:continue
            a=len(p&t)/len(p);b=len(q&t)/len(q)
            d[cluster].append(a-b);ds.append((a,b));n+=1
        result[condition]={'pairs':n,'clusters':len(d),'pair_mean_P':ST.mean(x[0] for x in ds) if n else None,'pair_mean_nonP':ST.mean(x[1] for x in ds) if n else None,'equal_cluster_difference':boot_cluster(d) if len(d)>=10 and n>=30 else None}
    return result

def reference(pairs,trait,seed=20261128,n=1999):
    # Random class labels retain number of observed taxa per class and all pair-specific taxon outcomes.
    # Non-exchangeable evolutionary traits; reference, not a p-value.
    # Only incidents where habitat remains but a prior taxon is missing.
    # Aggregate identical focal/target-composition events for fast repeated evaluation.
    events=C.Counter((x,t) for _,_,_,_,s,t in pairs if t and (s|t)<=trait.keys() for x in s-t)
    if not events:return None
    names=sorted({v for x,t in events for v in ({x}|t)});labels=[trait[x] for x in names]
    if len(set(labels))<2:return None
    total=sum(events.values())
    def score(m):return sum(n for (x,t),n in events.items() if any(m[y]==m[x] for y in t))/total
    observed=score(trait);rng=random.Random(seed)
    vals=[]
    for _ in range(n):
        rng.shuffle(labels);vals.append(score(dict(zip(names,labels))))
    vals.sort()
    return {'eligible_lost_taxon_incidences':total,'species':names,'observed_same_class_fraction':observed,'reference_mean':ST.mean(vals),'reference_95':[vals[int(.025*(n-1))],vals[int(.975*(n-1))]],'difference':observed-ST.mean(vals)}

def selftest():
    trait={'A':'P','B':'C','D':'C'}
    p=[('st','mark',1,2,frozenset(['A','B']),frozenset(['A','D'])),('st','mark',2,3,frozenset(['A','D']),frozenset())]
    r=summarize(p,trait);assert r['loss']=={'total':3,'bare':2,'same_class':1,'other_class_only':0}
    assert r['all']['pair_mean_P']==.5 and r['all']['pair_mean_nonP']==0
    assert reference(p,trait,n=99)['observed_same_class_fraction']==1

def main():
    selftest()
    panels,audit=read_australia(sys.argv[1]);tampa,mapping,taudit=read_tampa()
    panels['tampa|pinned_exact_meter_marks']=tampa
    out={'archive':A,'raw_hashes':HASH,'audit':audit,'tampa_audit':taudit,'trait_mapping_australia':TRAIT,'trait_mapping_tampa':mapping,'panels':{}}
    for name,pairs in sorted(panels.items()):
        tr=mapping if name.startswith('tampa|') else TRAIT
        alt={x:('C' if x.split()[0] in ('Halodule','Zostera') else v) for x,v in tr.items()}
        strict={x:v for x,v in tr.items() if x!='Halophila capricorni'}
        r=summarize(pairs,tr);r['total_pairs']=len(pairs);r['initial_positive_pairs']=sum(bool(x[4]) for x in pairs);r['clusters']=len({x[0] for x in pairs})
        r['class_label_reference']=reference(pairs,tr)
        r['alternative_Halodule_Zostera_C_reference']=reference(pairs,alt)
        if len(strict)!=len(tr):r['without_H_capricorni']=summarize(pairs,strict)['all']
        out['panels'][name]=r
    out['limits']=['Response-open trait comparison. No biological survival, recruitment or direct functional measurements. Life-history classes are known prior art, not new traits.','Tampa bootstrap clusters are transects, Australia exact coordinates. Nearby stations and years may be correlated. Paired cooccurrence controls common site/time but not species-level detection, abundance or microhabitat; three persistent genera maximum.','Class-label shuffle is a fixed-size descriptive reference, not an evolutionary null or statistical p-value. Group identity is not function equivalence.','GBR historic coordinates can be rounded; same month/method/custodian/location and full species agreement required. Different surveys and time intervals not pooled.']
    Path(sys.argv[2]).write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
    compact={k:{'pairs':v['total_pairs'],'positive':v['initial_positive_pairs'],'clusters':v['clusters'],'loss':v['loss'],'all':v['all'],'both_positive':v['both_positive'],'class_label_reference':{a:b for a,b in (v['class_label_reference'] or {}).items() if a!='species'},'alternative_reference':{a:b for a,b in (v['alternative_Halodule_Zostera_C_reference'] or {}).items() if a!='species'}} for k,v in out['panels'].items()}
    print('RESULT_JSON '+json.dumps({'audit':audit,'tampa_audit':taudit,'panels':compact},allow_nan=False))
if __name__=='__main__':main()
