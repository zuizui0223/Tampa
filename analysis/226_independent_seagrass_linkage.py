#!/usr/bin/env python3
"""Audit independently acquired MarineGEO actual tables and retry explicit Moreton data export."""
import collections as C, csv, hashlib, io, json, sys, urllib.request as U, zipfile
from pathlib import Path
def sha(b):return hashlib.sha256(b).hexdigest()
def archive(path):
    raw=Path(path).read_bytes();assert sha(raw)=='f08742a7d7b26ff55e1e21fa98bcfc545b92f3cd1cd9e5beebcebf96a3f1771c'
    with zipfile.ZipFile(io.BytesIO(raw)) as z:b=z.read(next(x for x in z.namelist() if x.endswith('marinegeo.zip')))
    assert sha(b)=='d54938eed357e27ebd456dfd7d50c0506e60e8345b524809711b91f8c0cee29e'
    z=zipfile.ZipFile(io.BytesIO(b))
    hashes={'event.txt':'3bef0b191f395141bb926f2c3d277e2bbe42d1f7f12861c9a5f28e06663cf048','occurrence.txt':'6656a636f74e5658dac1c9393e41f424cf31e95cc691ceaab901fb0d35b03a55','extendedmeasurementorfact.txt':'264070846a202902cd5aa5799a82f8c94295119d790de130b78b5df5cab5824d'}
    def read(n):raw=z.read(n);assert sha(raw)==hashes[n];return list(csv.DictReader(io.StringIO(raw.decode('utf-8-sig')),delimiter='\t'))
    e,o,m=map(read,hashes);assert (len(e),len(o),len(m))==(492,2534,2976)
    core={x['id']:x for x in e};assert len(core)==len(e)
    occ={x['occurrenceID']:x for x in o};assert len(occ)==len(o)
    gen=set('Amphibolis Cymodocea Enhalus Halodule Halophila Heterozostera Phyllospadix Posidonia Syringodium Thalassia Thalassodendron Zostera Ruppia'.split())
    audit=C.Counter();types=C.Counter();evtypes=C.defaultdict(set);species=C.Counter();animals=C.Counter();sample=C.defaultdict(set)
    for x in m:
        a=occ.get(x['occurrenceID']);v=core.get(x['id']);typ=x['measurementType'];unit=x['measurementUnit']
        audit['measurement_rows']+=1
        if v is None:audit['unlinked_core']+=1;continue
        if a is None:audit['no_exact_occurrence']+=1;group='unlinked_occurrence'
        elif a['genus'] in gen:group='seagrass_or_Ruppia';species[a['scientificName']]+=1
        elif a['kingdom']=='Animalia':group='Animalia';animals[a['scientificName']]+=1
        else:group=a['kingdom'] or 'other'
        if a is not None and a['id']!=x['id']:audit['occurrence_core_mismatch']+=1;continue
        types[(group,typ,unit)]+=1;evtypes[x['id']].add((group,typ,unit))
        sample[(group,typ,unit)].add(x['id'])
    groups=C.defaultdict(set);eventfamilies=C.Counter()
    for eid,ts in evtypes.items():
        v=core[eid];eventfamilies[tuple(sorted({(g,t) for g,t,u in ts}))]+=1
        for g,t,u in ts:groups[g].add(eid)
    ea=groups['Animalia'];es=groups['seagrass_or_Ruppia']
    cn=C.Counter(x['countryCode'] for x in e);years=C.Counter(x['eventDate'][:4] for x in e)
    roots=C.Counter(x['id'].count(':') for x in e)
    return {'event_n':len(e),'occurrence_n':len(o),'measurement_n':len(m),'audit':dict(audit),'countries':dict(cn),'years':dict(years),'core_id_depth':dict(roots),'core_examples':[{k:x[k] for k in ('id','eventID','parentEventID','eventDate','countryCode','samplingProtocol','sampleSizeValue','sampleSizeUnit','footprintWKT')} for x in e[:8]],'taxon_measurement_types':[{'group':g,'type':t,'unit':u,'rows':n,'events':len(sample[(g,t,u)])} for (g,t,u),n in sorted(types.items())],'seagrass_names':dict(species),'animal_names_top25':dict(animals.most_common(25)),'seagrass_events':len(es),'animal_events':len(ea),'exact_core_both':len(es&ea),'exact_core_both_examples':sorted(es&ea)[:12],'families':[{'types':x,'events':n} for x,n in eventfamilies.items()],'limits':['Exact core co-occurrence is a linkage audit, not proof of comparable sampling effort, actual interaction, or same individual. Ruppia included only in candidate group. Animalia may include sessile cover rather than epifaunal counts. No zero imputation, no model or ecological effect estimate.']}
def moreton(outdir):
    out={}
    for year,num in [(2011,'846143'),(2012,'846146')]:
        url='https://doi.pangaea.de/10.1594/PANGAEA.'+num+'?format=textfile'
        res={'url':url}
        try:
            with U.urlopen(U.Request(url,headers={'User-Agent':'Tampa-scientific-data-acquisition/1.0','Accept':'text/plain','Accept-Encoding':'identity'}),timeout=45) as r:b=r.read(30_000_001);res['final_url']=r.url
            if len(b)>30_000_000:raise ValueError('byte limit')
            s=b.decode('utf-8-sig');lines=s.splitlines()
            candidates=[i for i,x in enumerate(lines) if '\t' in x and ('Latitude' in x or 'LATITUDE' in x) and ('Longitude' in x or 'LONGITUDE' in x)]
            res['preview']=[x[:350] for x in lines[:4]]
            if len(candidates)!=1:raise ValueError('ambiguous/missing tabular geospatial header: '+str(candidates[:8]))
            idx=candidates[0];header=lines[idx].split('\t');rows=[x for x in csv.reader(lines[idx+1:],delimiter='\t') if x]
            if len(header)<25 or not rows or any(len(x)!=len(header) for x in rows):raise ValueError('table shape')
            res.update(state='ACQUIRED',sha256=sha(b),bytes=len(b),header=header,rows=len(rows),first=rows[0])
            (outdir/('moreton_'+str(year)+'.tsv')).write_bytes(b)
        except Exception as e:res.update(state='STOP',reason=type(e).__name__+': '+str(e))
        out[str(year)]=res
    return out
if __name__=='__main__':
    out=Path('independent_audit');out.mkdir(exist_ok=True);result={'marinegeo':archive(sys.argv[1]),'moreton_retry':moreton(out)}
    (out/'audit.json').write_text(json.dumps(result,indent=2)+'\n');print('AUDIT_JSON '+json.dumps(result))
