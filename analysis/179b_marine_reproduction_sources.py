import urllib.request as u,urllib.parse as q,json,hashlib,re
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
O=Path('marine_reproduction_sources');O.mkdir(exist_ok=True)
def get(url):
    assert q.urlparse(url).scheme=='https'
    with u.urlopen(u.Request(url,headers={'User-Agent':'Tampa-source-audit/1.0','Accept-Encoding':'identity'}),timeout=45) as f:b=f.read(12000001)
    if len(b)>12000000:raise ValueError('size cap')
    return b
def save(n,b):
    n=re.sub(r'[^A-Za-z0-9_.-]','_',n);(O/n).write_bytes(b)
    return dict(file=n,sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def dryad(item):
    d,t=item;base='https://datadryad.org';key=d.split('.')[-1];r={'doi':d,'files':[]}
    try:
        b=get(base+'/api/v2/datasets/'+q.quote('doi:'+d,safe=''));j=json.loads(b);assert t.lower() in j['title'].lower()
        r['metadata']=save(key+'_metadata.json',b)
        b=get(q.urljoin(base,j['_links']['stash:version']['href']));v=json.loads(b);r['version']=save(key+'_version.json',b)
        b=get(q.urljoin(base,v['_links']['stash:files']['href']));r['listing']=save(key+'_files.json',b)
        for f in json.loads(b)['_embedded']['stash:files']:
            a={'name':f['path']}
            try:
                if f.get('restricted') or not f['path'].lower().endswith(('.csv','.tsv','.txt','.md','.xlsx','.r')):raise ValueError('restricted or unselected')
                if (f.get('size') or 0)>12000000:raise ValueError('size cap')
                raw=get(q.urljoin(base,f['_links']['stash:download']['href']))
                if f.get('size') is not None:assert len(raw)==f['size']
                dt=(f.get('digestType') or '').lower().replace('-','')
                if dt in ('md5','sha1','sha256') and f.get('digest'):assert hashlib.new(dt,raw).hexdigest()==f['digest'].lower()
                a.update(save(key+'_'+f['path'],raw),status='ACQUIRED')
            except Exception as e:a.update(status='STOP_OR_SKIP',reason=str(e)[:200])
            r['files'].append(a)
        r['status']='ACQUIRED' if any(x['status']=='ACQUIRED' for x in r['files']) else 'METADATA_ONLY'
    except Exception as e:r.update(status='STOP',reason=str(e)[:200])
    return r
def pangaea():
    d='10.1594/PANGAEA.937393';r={'doi':d}
    try:
        b=get('https://doi.pangaea.de/'+d+'?format=textfile');s=b.decode('utf-8-sig');assert d in s and 'Zostera marina' in s and '*/' in s
        r.update(save('pangaea_937393.tsv',b),status='ACQUIRED_SCHEMA_TO_AUDIT')
    except Exception as e:r.update(status='STOP',reason=str(e)[:200])
    return r
with ThreadPoolExecutor(max_workers=4) as ex:
    f=ex.submit(pangaea);r=list(ex.map(dryad,[('10.5061/dryad.vhhmgqnwz','Flowering, seed production'),('10.5061/dryad.dfn2z358x','Mating system variation'),('10.5061/dryad.sj6dv','Should we sync')]))+[f.result()]
(O/'manifest.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
