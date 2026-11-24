#!/usr/bin/env python3
"""Acquire public RWS mapping and restoration data, not a fitted model.

Do not convert absence of mapped polygons into absence of plants.
Preserve zero attributes, catalog metadata, and feature identity. Refuse partial layers.
"""
import json,hashlib,urllib.request,urllib.parse,re,io,xml.etree.ElementTree as ET
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
OUT=Path('wadden_seagrass_sources');OUT.mkdir(exist_ok=True)
BBOX=(4.7,52.8,7.35,53.65)
YEARS={2008,2009,2010,2011,2014,2017,2020,2023}
CAP=35_000_000
def get(url,params=None,cap=CAP):
    if params:url+=('?' if '?' not in url else '&')+urllib.parse.urlencode(params)
    assert urllib.parse.urlparse(url).scheme=='https'
    req=urllib.request.Request(url,headers={'User-Agent':'Tampa ecological research source audit/1.0','Accept-Encoding':'identity'})
    with urllib.request.urlopen(req,timeout=45) as r:b=r.read(cap+1)
    if len(b)>cap:raise ValueError('byte cap exceeded')
    return b
def save(name,b):
    name=re.sub(r'[^a-zA-Z0-9_.-]','_',name)
    (OUT/name).write_bytes(b)
    return dict(file=name,bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def loadjson(url,params=None,cap=CAP):
    b=get(url,params,cap);j=json.loads(b)
    if 'error' in j:raise ValueError(str(j['error'])[:300])
    return b,j
def is_relevant(name):
    return bool(re.search(r'(?i)zostera|zeegras|survey|karter|onderzoek|begrenz|dekking',name))
def arcgis():
    result={'type':'Rijkswaterstaat ArcGIS public catalog','attempts':[],'layers':[]}
    for base in ['https://geo.rijkswaterstaat.nl/arcgis/rest/services/GDR/zeegras/FeatureServer','https://geo.rijkswaterstaat.nl/arcgis/rest/services/GDR/zeegras/MapServer']:
        try:
            b,j=loadjson(base,{'f':'json'},4_000_000);result['catalog']=save('rws_catalog_'+base.rsplit('/',1)[1]+'.json',b);result['base']=base
            selected=[]
            for l in j.get('layers',[]):
                name=l['name'];yrs={int(x) for x in re.findall(r'(?<!\d)(?:19|20)\d{2}(?!\d)',name)}
                if not is_relevant(name) or (yrs and not yrs&YEARS):continue
                selected.append(l)
            result['selected_count']=len(selected)
            # limit public requests, retain exact catalog for unselected layers
            for l in selected[:36]:
                lid=l['id'];name=l['name'];r={'id':lid,'name':name,'chunks':[]};prefix='rws_layer_'+str(lid)
                try:
                    bb,meta=loadjson(base+'/'+str(lid),{'f':'json'},3_000_000)
                    r['metadata']=save(prefix+'_metadata.json',bb)
                    r['fields']=meta.get('fields',[]);r['geometryType']=meta.get('geometryType')
                    if not r['geometryType']:raise ValueError('group or nongeometric layer')
                    # query exact envelope with defined spatial reference; return all attributes.
                    q=base+'/'+str(lid)+'/query'
                    geom=','.join(map(str,BBOX))
                    params={'f':'json','where':'1=1','geometry':geom,'geometryType':'esriGeometryEnvelope','inSR':4326,'spatialRel':'esriSpatialRelIntersects','returnIdsOnly':'true'}
                    bi,ji=loadjson(q,params,4_000_000);ids=ji.get('objectIds') or []
                    r['ids']=save(prefix+'_ids.json',bi);r['n_ids']=len(ids)
                    if len(ids)>30000:raise ValueError('selected spatial subset >30,000 features; need explicit paging strategy')
                    if not ids:r['status']='EMPTY_QUERY_NOT_ABSENCE';result['layers'].append(r);continue
                    oid=ji.get('objectIdFieldName') or meta.get('objectIdField')
                    assert oid and len(set(ids))==len(ids)
                    chunk_size=min(500,int(meta.get('maxRecordCount') or 500));features=[];sr=None;total_bytes=0
                    for off in range(0,len(ids),chunk_size):
                        chunk=ids[off:off+chunk_size];bz,zz=loadjson(q,{'f':'json','objectIds':','.join(map(str,chunk)),'outFields':'*','outSR':4326,'returnGeometry':'true'},CAP)
                        total_bytes+=len(bz)
                        if total_bytes>CAP:raise ValueError('layer exceeds 35 MB total cap')
                        assert not zz.get('exceededTransferLimit',False)
                        fs=zz.get('features',[]);assert len(fs)==len(chunk)
                        assert {f['attributes'][oid] for f in fs}==set(chunk)
                        assert all(f.get('geometry') for f in fs)
                        if sr is None:sr=zz.get('spatialReference')
                        else:assert sr==zz.get('spatialReference')
                        features.extend(fs)
                    assert len(features)==len(ids) and sr and (sr.get('wkid')==4326 or sr.get('latestWkid')==4326)
                    payload=json.dumps({'source':q,'spatialReference':sr,'geometryType':r['geometryType'],'fields':r['fields'],'features':features},ensure_ascii=False).encode()
                    r['data']=save(prefix+'_features.json',payload);r['status']='ACQUIRED_COMPLETE_SPATIAL_QUERY'
                except Exception as e:r.update(status='STOP_OR_METADATA_ONLY',reason=str(e)[:300])
                result['layers'].append(r)
            result['status']='ACQUIRED_LAYERS' if any('data' in x for x in result['layers']) else 'METADATA_ONLY'
            return result
        except Exception as e:result['attempts'].append({'base':base,'error':str(e)[:300]})
    result['status']='STOP';return result
def wfs():
    r={'type':'Rijkswaterstaat WFS catalog fallback','attempts':[],'layers':[]}
    for base in ['https://geoservices.rijkswaterstaat.nl/apps/geoserver/zeegras/ows','https://geo.rijkswaterstaat.nl/services/ogc/gdr/zeegras/ows']:
        try:
            b=get(base,{'service':'WFS','version':'2.0.0','request':'GetCapabilities'},4_000_000);root=ET.fromstring(b)
            names=[x.text for x in root.findall('.//{*}FeatureType/{*}Name') if x.text];assert names
            r['catalog']=save('rws_wfs_capabilities.xml',b);r['base']=base;r['type_names']=names
            for name in names:
                yrs={int(x) for x in re.findall(r'(?<!\d)(?:19|20)\d{2}(?!\d)',name)}
                if not is_relevant(name) or not yrs&YEARS:continue
                q={'service':'WFS','version':'2.0.0','request':'GetFeature','typeNames':name,'srsName':'urn:ogc:def:crs:OGC:1.3:CRS84','bbox':','.join(map(str,BBOX))+',urn:ogc:def:crs:OGC:1.3:CRS84'}
                a={'name':name}
                try:
                    schema=get(base,{'service':'WFS','version':'2.0.0','request':'DescribeFeatureType','typeNames':name},1_000_000);a['schema']=save(name+'_schema.xml',schema)
                    hits=get(base,q|{'resultType':'hits'},1_000_000);root=ET.fromstring(hits);count=int(root.attrib['numberMatched']);a['count']=count
                    if count==0:a['status']='EMPTY_QUERY_NOT_ABSENCE'
                    elif count>30000:raise ValueError('layer exceeds 30,000 features')
                    else:
                        bb=get(base,q|{'outputFormat':'application/json','count':count},CAP);j=json.loads(bb);assert j['type']=='FeatureCollection' and len(j['features'])==count and all(f.get('geometry') for f in j['features'])
                        ids=[f.get('id') for f in j['features']]
                        if all(x is not None for x in ids):assert len(set(ids))==count
                        a['data']=save(name+'_features.geojson',bb);a['status']='ACQUIRED_COMPLETE_SPATIAL_QUERY'
                except Exception as e:a.update(status='STOP_OR_METADATA_ONLY',reason=str(e)[:300])
                r['layers'].append(a)
                if len(r['layers'])>=36:break
            r['status']='ACQUIRED_LAYERS' if any('data' in x for x in r['layers']) else 'METADATA_ONLY';return r
        except Exception as e:r['attempts'].append({'base':base,'error':str(e)[:300]})
    r['status']='STOP';return r
def dataverse(doi,base):
    r={'doi':doi,'base':base,'files':[]}
    try:
        b,j=loadjson(base+'/api/datasets/:persistentId/',{'persistentId':'doi:'+doi},5_000_000);d=j['data']
        assert str(d['persistentUrl']).lower().endswith(doi.lower())
        r['metadata']=save('dv_'+doi.rsplit('/',1)[-1]+'_metadata.json',b)
        for f in d['latestVersion']['files']:
            v=f['dataFile'];name=v['filename'];a={'name':name,'id':v['id'],'restricted':bool(f.get('restricted'))}
            try:
                if a['restricted']:raise ValueError('restricted')
                if v.get('filesize',0)>CAP:raise ValueError('file exceeds cap')
                if not name.lower().endswith(('.csv','.tab','.tsv','.txt','.xlsx','.xls','.ods','.r','.rmd','.pdf','.docx','.zip')):raise ValueError('non-table/document/code extension')
                bb=get(base+'/api/access/datafile/'+str(v['id']),cap=CAP)
                chk=v.get('checksum',{})
                if chk.get('type','').upper()=='MD5':assert hashlib.md5(bb).hexdigest()==chk['value'].lower().zfill(32)
                elif chk.get('type','').upper()=='SHA-1':assert hashlib.sha1(bb).hexdigest()==chk['value'].lower()
                a.update(save('dv_'+str(v['id'])+'_'+name,bb),status='ACQUIRED')
            except Exception as e:a.update(status='STOP_OR_SKIPPED',reason=str(e)[:300])
            r['files'].append(a)
        r['status']='ACQUIRED_FILES' if any(x['status']=='ACQUIRED' for x in r['files']) else 'METADATA_ONLY'
    except Exception as e:r.update(status='STOP',reason=str(e)[:300])
    return r
with ThreadPoolExecutor(max_workers=4) as ex:
    fa=ex.submit(arcgis)
    fs=[ex.submit(dataverse,doi,base) for doi,base in [
        ('10.34894/FHEZIR','https://dataverse.nl'),
        ('10.34894/FKSY2M','https://dataverse.nl'),
        ('10.34894/ZY6U9J','https://dataverse.nl'),
        ('10.17026/LS/TZYAGQ','https://lifesciences.datastations.nl')]]
    ar=fa.result();results=[ar]
    # Only use public WFS fallback when primary ArcGIS retrieval lacks complete layers.
    if ar['status']!='ACQUIRED_LAYERS':results.append(wfs())
    results.extend(f.result() for f in fs)
(OUT/'manifest.json').write_text(json.dumps(results,indent=2,ensure_ascii=False)+'\n')
print(json.dumps([{k:v for k,v in a.items() if k not in ['type_names','layers']}|({'layers':[{'name':x['name'],'status':x['status'],'count':x.get('count',x.get('n_ids')),'reason':x.get('reason')} for x in a['layers']]} if 'layers' in a else {}) for a in results],indent=2))
