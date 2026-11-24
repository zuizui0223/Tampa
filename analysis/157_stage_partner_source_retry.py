"""Retry field and seed-ball sources; preserve bytes before schema decisions."""
import csv,hashlib,io,json,urllib.request
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
OUT=Path('stage_partner_retry');OUT.mkdir(exist_ok=True)
def get(url):
 assert url.startswith('https://')
 with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Tampa-public-data-audit/1.0','Accept-Encoding':'identity'}),timeout=60) as f:b=f.read(20_000_001)
 assert len(b)<=20_000_000
 return b
def save(name,b):
 (OUT/name).write_bytes(b)
 return {'file':name,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def field():
 r={'doi':'10.1594/PANGAEA.984656'}
 try:
  b=get('https://doi.pangaea.de/10.1594/PANGAEA.984656?format=textfile');r.update(save('pangaea_984656.tsv',b));r['status']='RAW_RETRIEVED_NOT_VALIDATED'
  t=b.decode('utf-8-sig');assert r['doi'].lower() in t.lower() and '*/' in t
  body=t.split('*/',1)[1].lstrip('\r\n')
  rows=list(csv.reader(io.StringIO(body),delimiter='\t'));rows=[x for x in rows if x]
  assert rows and len(rows[0])>2
  bad=[{'line':i+2,'fields':len(x)} for i,x in enumerate(rows[1:]) if len(x)!=len(rows[0])]
  r.update(columns=rows[0],rows=len(rows)-1,irregular_rows=bad[:50],irregular_count=len(bad),status='SCHEMA_PROFILED' if not bad else 'RAW_SCHEMA_STOP')
 except Exception as e:r['reason']=str(e)[:300];r.setdefault('status','STOP')
 return r
def fig():
 r={'doi':'10.6084/m9.figshare.32328606','files':[]}
 try:
  b=get('https://api.figshare.com/v2/articles/32328606');j=json.loads(b);assert j['doi'].lower().startswith(r['doi']);r['metadata']=save('figshare_metadata.json',b)
  for f in j['files']:
   x={'name':f['name']}
   try:
    bb=get(f['download_url']);assert len(bb)==f['size'] and hashlib.md5(bb).hexdigest()==f['computed_md5']
    x.update(save('figshare_'+str(f['id'])+'_'+Path(f['name']).name,bb));x['status']='ACQUIRED'
   except Exception as e:x.update(status='STOP',reason=str(e)[:300])
   r['files'].append(x)
  r['status']='ACQUIRED' if r['files'] and all(x['status']=='ACQUIRED' for x in r['files']) else 'PARTIAL_OR_STOP'
 except Exception as e:r.update(status='STOP',reason=str(e)[:300])
 return r
with ThreadPoolExecutor(max_workers=2) as ex:
 futures=[ex.submit(field),ex.submit(fig)];m=[f.result() for f in futures]
(OUT/'manifest.json').write_text(json.dumps(m,indent=2)+'\n');print(json.dumps(m,indent=2))
