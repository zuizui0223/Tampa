#!/usr/bin/env python3
"""Transcribe Fig. 6 categories, verify with rendered colors; descriptive cell summaries."""
import argparse, csv, hashlib, json, subprocess, zipfile
from pathlib import Path
from collections import Counter
import xml.etree.ElementTree as ET
from PIL import Image
ARCHIVE='fbc015db8390a554621eba991dace725083ddea5baab9c86be20c916e83f445f'
PDF='009f7f76fa6ee20e2f6974446bdce06de38d656c2d26c4bfc1d651c5d35ae645'
# Visual reading of Figure 6, printed p.4, PDF page 5; rows trial 1..5.
# -1 = no record, not absence of pollen tubes.
C=[[0,0,0,0,1,0],[0,0,0,0,1,0],[0,1,0,0,0,1],[0,0,1,0,0,0],[-1,0,-1,-1,0,0]]
F=[[3,2,3,2,3,3],[2,3,3,1,2,3],[1,2,2,2,2,2],[2,2,1,0,2,0],[-1,2,-1,-1,2,3]]
D=[15,30,45,60,90,150]
COLORS={(255,255,255):-1,(255,255,203):0,(215,215,0):1,(234,101,19):2,(255,102,0):2,(165,0,0):3}
def run(path,out):
    out.mkdir(parents=True,exist_ok=True)
    assert hashlib.sha256(path.read_bytes()).hexdigest()==ARCHIVE
    with zipfile.ZipFile(path) as z:
        m=json.loads(z.read('manifest.json'));p=z.read(m[2]['document']['file']);x=z.read(m[0]['xml']['file'])
        assert hashlib.sha256(p).hexdigest()==PDF==m[2]['document']['sha256']
        assert hashlib.sha256(x).hexdigest()==m[0]['xml']['sha256']
        assert '10.1038/ncomms12980' in [a.text for a in ET.fromstring(x).findall('.//article-meta/article-id')]
    dest=out/'ncomms12980.pdf';dest.write_bytes(p)
    subprocess.run(['pdftoppm','-f','5','-l','5','-r','220','-png',str(dest),str(out/'page')],check=True,capture_output=True)
    im=Image.open(out/'page-5.png').convert('RGB');w,h=im.size
    rows=[]
    for i,y in enumerate([285,248,211,174,137]):
        for j,x in enumerate([590,609,628,647,666,685,704,723,742,761,780,799]):
            counts=Counter(im.crop((int((x-4)*w/1071),int((y-6)*h/1408),int((x+4)*w/1071),int((y+6)*h/1408))).getdata())
            color,n=counts.most_common(1)[0];category=COLORS[color];t='control' if j<6 else 'fauna';manual=(C if j<6 else F)[i][j%6]
            assert category==manual,(i,j,color,category,manual)
            rows.append(dict(treatment=t,trial=i+1,distance_cm=D[j%6],category=category,modal_rgb=' '.join(map(str,color)),modal_fraction=n/sum(counts.values())))
    def counts(v):
        a=[r['category'] for r in v];n=sum(k>=0 for k in a)
        return dict(n_cells=len(a),n_recorded=n,n_no_record=a.count(-1),category_counts=[a.count(k) for k in range(4)],positive=sum(k>0 for k in a),positive_fraction=sum(k>0 for k in a)/n,at_least10=sum(k>=2 for k in a),at_least100=sum(k==3 for k in a))
    def compare(v):
        c,f=[counts([r for r in v if r['treatment']==t]) for t in ['control','fauna']]
        return dict(control=c,fauna=f,positive_RD=f['positive_fraction']-c['positive_fraction'],at_least10_RD=f['at_least10']/f['n_recorded']-c['at_least10']/c['n_recorded'])
    allr=compare(rows);c,f=allr['control'],allr['fauna'];assert c['n_recorded']==f['n_recorded']==27
    def chisq(tab):
        rr=list(map(sum,tab));cc=list(map(sum,zip(*tab)));tot=sum(rr)
        return sum((v-rr[i]*cc[j]/tot)**2/(rr[i]*cc[j]/tot) for i,r in enumerate(tab) for j,v in enumerate(r) if cc[j])
    bydist=[dict(distance_cm=d,**compare([r for r in rows if r['distance_cm']==d])) for d in D]
    report=dict(status='published figure transcription, visual and pixel cross-check; not raw records',archive_sha256=ARCHIVE,pdf_sha256=PDF,figure='Figure 6, printed p.4, PDF page 5',legend={'-1':'no record','0':'zero tubes','1':'positive <10','2':'10–99','3':'>=100'},all=allr,by_distance=bydist,far_90_150=compare([r for r in rows if r['distance_cm']>=90]),hypothetical_binary_completion_RD_bounds=[(f['positive']-(c['positive']+c['n_no_record']))/30,((f['positive']+f['n_no_record'])-c['positive'])/30],pearson_diagnostic={'displayed_categories_control_fauna':chisq([c['category_counts'],f['category_counts']]),'displayed_distance_fauna':chisq([r['fauna']['category_counts'] for r in bydist]),'published_treatment_chi_square':38.75,'published_distance_chi_square':10.465,'note':'Not exactly reproduced by visible cell counts; no inferred p-values or relabeling.'},limitations=['Four physical mesocosms, treatment assigned at mesocosm/night level, two female flowers per tank; displayed trial rows do not identify tank-night membership. No independent-flower inference.','No water-flow in both arms; no animal x flow factorial or direct relative contribution in nature.','Categories do not provide exact tube counts, fruit or seed set. No record may reflect unopened buds. Hypothetical binary completion not measured outcomes.','Supplement downloads timed out; source PDF and XML verified.'])
    with (out/'figure6_cells.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    (out/'results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    return report
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('artifact',type=Path);p.add_argument('--out',type=Path,required=True);a=p.parse_args();r=run(a.artifact,a.out);print(json.dumps(r,ensure_ascii=False,indent=2))
