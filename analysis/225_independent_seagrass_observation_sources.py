#!/usr/bin/env python3
"""New independent observation resources; actual source bytes, no inferred zeros."""
import concurrent.futures as F, csv, hashlib, io, json, sys, urllib.request as U, zipfile
from pathlib import Path
OUT=Path('new_seagrass_sources');OUT.mkdir(exist_ok=True)
SPECS={
'moreton_2011_06':('https://doi.pangaea.de/10.1594/PANGAEA.846143','tsv'),
'moreton_2012_06':('https://doi.pangaea.de/10.1594/PANGAEA.846146','tsv'),
'marinegeo':('https://ipt-obis.gbif.us/archive.do?r=marinegeo-seagrass-monitoring&v=1.2','zip')}
def get(key,spec):
    url,typ=spec;res={'url':url}
    try:
        req=U.Request(url,headers={'User-Agent':'Tampa-scientific-data-acquisition/1.0','Accept':'text/tab-separated-values' if typ=='tsv' else 'application/zip','Accept-Encoding':'identity'})
        with U.urlopen(req,timeout=70) as r:b=r.read(60_000_001);res['final_url']=r.url
        if len(b)>60_000_000:raise ValueError('cap')
        if typ=='zip':
            z=zipfile.ZipFile(io.BytesIO(b));members={}
            for n in z.namelist():
                if n.lower().endswith(('.txt','.csv','.tsv')):
                    raw=z.read(n);s=raw.decode('utf-8-sig');lines=s.splitlines()
                    members[n]={'rows_ex_header':max(0,len(lines)-1),'header':lines[0][:4000] if lines else '', 'first':lines[1][:4000] if len(lines)>1 else '', 'sha256':hashlib.sha256(raw).hexdigest()}
            res['members']=members;res['all_members']=z.namelist()
        else:
            text=b.decode('utf-8-sig');lines=text.splitlines()
            idx=next(i for i,s in enumerate(lines) if s.startswith('ID\t') or (s.startswith('Identification') and '\t' in s))
            header=lines[idx].split('\t');data=list(csv.reader(lines[idx+1:],delimiter='\t'))
            data=[x for x in data if x]
            if len(header)<25 or any(len(x)!=len(header) for x in data):raise ValueError('shape')
            res.update(header=header,rows=len(data),first=data[0],nonempty_by_col=[sum(bool(x[i]) for x in data) for i in range(len(header))])
        filename=key+'.'+typ;(OUT/filename).write_bytes(b)
        res.update(state='ACQUIRED',file=filename,sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
    except Exception as e:res.update(state='STOP',reason=type(e).__name__+': '+str(e)[:300])
    return key,res
def main():
    with F.ThreadPoolExecutor(max_workers=3) as e:result=dict(e.map(lambda x:get(*x),SPECS.items()))
    (OUT/'manifest.json').write_text(json.dumps(result,indent=2)+'\n');print('ACQUIRE_JSON '+json.dumps(result))
if __name__=='__main__':main()
