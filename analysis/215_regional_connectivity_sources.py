#!/usr/bin/env python3
"""Bounded public habitat and published Torres Strait SLIM archive discovery."""
import hashlib,io,json,re,urllib.request,urllib.parse,zipfile,concurrent.futures
from html.parser import HTMLParser
from pathlib import Path
O=Path("regional_connectivity_sources");O.mkdir(exist_ok=True)
def get(url,cap=12_000_000):
 with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Tampa-seagrass-connectivity-research/1.0','Accept-Encoding':'identity'}),timeout=30) as r:
  b=r.read(cap+1);assert len(b)<=cap
  return b,dict(url=url,host=urllib.parse.urlsplit(r.geturl()).netloc,bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),type=r.headers.get('Content-Type'))
def save(name,b,m):
 (O/name).write_bytes(b);return dict(m,file=name,state='ACQUIRED')
def gbr():
 url='https://maps.eatlas.org.au/maps/wfs?'+urllib.parse.urlencode(dict(service='WFS',version='1.0.0',request='GetFeature',typeName='nesp1:GBR_NESP-TWQ-3-1_JCU_Seagrass_1984-2014_Meadow-boundaries',outputFormat='application/json',srsName='EPSG:4326',bbox='148.5,-24,152,-20.5,EPSG:4326'))
 try:
  b,m=get(url);j=json.loads(b);assert j['type']=='FeatureCollection' and len(j['features'])>0
  return save('shoalwater_meadows.geojson',b,dict(m,n_features=len(j['features']),keys=list(j['features'][0]['properties'])))
 except Exception as e:return dict(url=url,state='STOP',reason=type(e).__name__+': '+str(e)[:300])
class Links(HTMLParser):
 def __init__(self):super().__init__();self.urls=[]
 def handle_starttag(self,tag,attrs):
  if tag=='a':self.urls.extend(v for k,v in attrs if k=='href' and v)
def slim():
 doi='10.25903/3pe4-9n65';url='https://doi.org/'+doi
 try:
  b,m=get(url,2_000_000);p=Links();p.feed(b.decode('utf-8',errors='replace'))
  # Resolve relative links using the real landing URL, keeping only explicit public links.
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Tampa-seagrass-connectivity-research/1.0'}),timeout=15) as r:landing=r.geturl()
  links=list(dict.fromkeys(urllib.parse.urljoin(landing,x) for x in p.urls))
  links=[x for x in links if urllib.parse.urlsplit(x).scheme=='https' and (re.search(r'\.(csv|xlsx|xls|zip|shp)(?:$|\?)',x,re.I) or '/download/' in x.lower() or '/download?' in x.lower())]
  return dict(m,doi=doi,landing=landing,explicit_file_links=links[:50],state='METADATA_ONLY')
 except Exception as e:return dict(doi=doi,url=url,state='STOP',reason=type(e).__name__+': '+str(e)[:300])
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as e:a=e.submit(gbr);b=e.submit(slim);out=[a.result(),b.result()]
 (O/'manifest.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
