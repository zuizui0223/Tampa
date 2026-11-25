#!/usr/bin/env python3
"""Acquire openly published marine pollination figures and supplement documents.
No figure transcriptions or individual records manufactured here."""
import hashlib,io,json,urllib.request,urllib.parse,zipfile,xml.etree.ElementTree as ET
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
OUT=Path('marine_pollen_sources');OUT.mkdir(exist_ok=True)
CAP=35_000_000
def get(url,cap=CAP):
    assert urllib.parse.urlparse(url).scheme=='https'
    req=urllib.request.Request(url,headers={'User-Agent':'Tampa-ecology-source-audit/1.0','Accept-Encoding':'identity'})
    with urllib.request.urlopen(req,timeout=50) as f:b=f.read(cap+1)
    if len(b)>cap:raise ValueError('byte cap exceeded')
    return b
def save(name,b):
    assert Path(name).name==name
    (OUT/name).write_bytes(b)
    return dict(file=name,bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def pmc(pmcid,doi,files):
    r=dict(pmcid=pmcid,doi=doi,files=[],attempts=[])
    base='https://www.ebi.ac.uk/europepmc/webservices/rest/'+pmcid
    try:
        raw=get(base+'/fullTextXML',8_000_000)
        root=ET.fromstring(raw)
        ids={x.attrib.get('pub-id-type'):x.text for x in root.findall('.//article-meta/article-id')}
        assert ids.get('doi','').lower()==doi.lower()
        r['xml']=save(pmcid+'_article.xml',raw)
        r['figure_ids']=[{'id':x.attrib.get('id'),'label':x.findtext('label'),'graphics':[g.attrib for g in x.findall('.//graphic')]} for x in root.findall('.//fig')]
        r['supplements']=[x.attrib for x in root.findall('.//supplementary-material')]
    except Exception as e:r['attempts'].append({'step':'xml','reason':str(e)[:250]})
    try:
        raw=get(base+'/supplementaryFiles')
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            r['members']=[dict(name=x.filename,bytes=x.file_size) for x in z.infolist()]
            total=0
            for i in z.infolist():
                name=Path(i.filename).name
                if name not in files:continue
                if i.file_size>10_000_000 or total+i.file_size>20_000_000:continue
                b=z.read(i);total+=len(b)
                r['files'].append(save(pmcid+'_'+name,b))
        r['status']='ACQUIRED_FILES' if r['files'] else 'METADATA_OR_EMPTY_SELECTION'
    except Exception as e:r.update(status='STOP_OR_XML_ONLY',reason=str(e)[:250])
    return r
def pdf():
    r=dict(doi='10.1038/ncomms12980',attempts=[])
    for u in ['https://www.pure.ed.ac.uk/ws/files/28992590/ncomms12980.pdf','https://www.vliz.be/imisdocs/publications/295682.pdf','https://www.nature.com/articles/ncomms12980.pdf']:
        try:
            b=get(u,15_000_000);assert b.startswith(b'%PDF-')
            r.update(source=u,document=save('ncomms12980.pdf',b),status='ACQUIRED_PDF_IDENTITY_TO_AUDIT');return r
        except Exception as e:r['attempts'].append({'url':u,'reason':str(e)[:250]})
    r['status']='STOP';return r
with ThreadPoolExecutor(max_workers=3) as ex:
    f=[ex.submit(pmc,'PMC5056424','10.1038/ncomms12980',{'ncomms12980-s1.pdf','ncomms12980-f6.jpg','ncomms12980-f6.gif','ncomms12980-f6.png','ncomms12980-f006.jpg','ncomms12980-f006.gif','ncomms12980-f006.png'}),ex.submit(pmc,'PMC5127610','10.1002/ece3.2309',{'ece32309-sup-0001-Supinfo.docx'}),ex.submit(pdf)]
    result=[x.result() for x in f]
(OUT/'manifest.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
