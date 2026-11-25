#!/usr/bin/env python3
"""Public document source gate. No acquisition success inferred until output audited."""
from pathlib import Path
import urllib.request as u, urllib.parse as p, hashlib,json,re,html
from concurrent.futures import ThreadPoolExecutor
O=Path('marine_access_sources');O.mkdir(exist_ok=True)
def get(url,cap=20000000):
    assert p.urlparse(url).scheme=='https'
    with u.urlopen(u.Request(url,headers={'User-Agent':'Tampa-research-audit/1.0','Accept-Encoding':'identity'}),timeout=45) as f:
        b=f.read(cap+1)
    if len(b)>cap:raise ValueError('size cap')
    return b
def save(n,b):
    (O/n).write_bytes(b);return dict(file=n,bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def pdf(item):
    n,url=item;r=dict(url=url)
    try:
        b=get(url);assert b.startswith(b'%PDF-');r.update(save(n,b),status='ACQUIRED_IDENTITY_TO_AUDIT')
    except Exception as e:r.update(status='STOP',reason=str(e)[:250])
    return r
def frontiers():
    url='https://www.frontiersin.org/journals/conservation-science/articles/10.3389/fcosc.2025.1646399/full'
    r=dict(url=url,files=[])
    try:
        b=get(url,8000000);s=b.decode('utf-8');assert '10.3389/fcosc.2025.1646399' in s
        r['html']=save('zakaria_article.html',b)
        urls=sorted({p.urljoin(url,html.unescape(x)) for x in re.findall(r'(?:href|src)=["\x27]([^"\x27]+)["\x27]',s) if re.search(r'1646399.*(?:supplement|table)|(?:supplement|table).*1646399',x,re.I)})
        r['public_links']=urls[:100]
        for i,x in enumerate(urls[:20]):
            if p.urlparse(x).scheme!='https' or not re.search(r'\.(?:pdf|docx|xlsx|csv|zip)(?:\?|$)',x,re.I):continue
            a=dict(url=x)
            try:
                bb=get(x);assert bb.startswith((b'%PDF-',b'PK')) or x.split('?')[0].endswith('.csv')
                ext=p.urlparse(x).path.rsplit('.',1)[-1];a.update(save('zakaria_supp_'+str(i)+'.'+ext,bb),status='ACQUIRED_SCHEMA_TO_AUDIT')
            except Exception as e:a.update(status='STOP',reason=str(e)[:250])
            r['files'].append(a)
        r['status']='ACQUIRED_FILES' if any(a['status'].startswith('ACQUIRED') for a in r['files']) else 'HTML_ONLY'
    except Exception as e:r.update(status='STOP',reason=str(e)[:250])
    return r
with ThreadPoolExecutor(max_workers=4) as ex:
    jobs=[ex.submit(pdf,x) for x in [('mizutani2019.pdf','https://www.jstage.jst.go.jp/article/hozen/24/2/24_1803/_pdf'),('rollon2003.pdf','https://www.vliz.be/imisdocs/publications/57415.pdf'),('vantussenbroek2008.pdf','https://www.int-res.com/articles/meps2008/354/m354p119.pdf')]]
    jobs.append(ex.submit(frontiers));r=[j.result() for j in jobs]
(O/'manifest.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
