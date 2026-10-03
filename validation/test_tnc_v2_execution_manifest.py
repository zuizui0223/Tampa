#!/usr/bin/env python3
from __future__ import annotations
import csv,json,subprocess,sys,tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"analysis/70_freeze_tnc_v2_execution_manifest.py"
BAYS=("Old Tampa Bay","Middle Tampa Bay","Lower Tampa Bay","Boca Ciega Bay")

def write_manifest(path, counts, start="2027-08-20", bad_offset=False, add_future=False):
    import datetime as dt
    d0=dt.date.fromisoformat(start)
    fields=["node_id","water_body","thalassia_positive","tnc_date","baseline_survey_date"]
    if add_future: fields.append("future_frequency")
    rows=[]
    for bi,b in enumerate(BAYS):
        for i in range(counts.get(b,0)):
            td=d0+dt.timedelta(days=(bi*2+i)%20)
            bd=td+(dt.timedelta(days=20) if bad_offset and b==BAYS[0] and i==0 else dt.timedelta(days=2))
            row={
              "node_id":f"{bi}-{i}","water_body":b,"thalassia_positive":"true",
              "tnc_date":td.isoformat(),"baseline_survey_date":bd.isoformat()
            }
            if add_future: row["future_frequency"]="0.9"
            rows.append(row)
    with path.open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)

def run(path):
    out=path.with_suffix(".json")
    cp=subprocess.run([sys.executable,str(SCRIPT),"--manifest",str(path),"--out",str(out)],cwd=ROOT,text=True,capture_output=True)
    obj=json.loads(out.read_text()) if out.exists() else None
    return cp,obj

def main():
    with tempfile.TemporaryDirectory() as td:
        td=Path(td)

        good=td/"good.csv"
        write_manifest(good,{b:9 for b in BAYS})
        cp,x=run(good)
        assert cp.returncode==0,(cp.stdout,cp.stderr)
        assert x["status"]=="PASS_EXECUTION_MANIFEST"
        assert x["total_eligible_nodes"]==36
        assert all(x["counts_by_bay"][b]==9 for b in BAYS)
        assert x["resource_freeze_payload"] is not None

        low=td/"low.csv"
        write_manifest(low,{"Old Tampa Bay":9,"Middle Tampa Bay":9,"Lower Tampa Bay":9,"Boca Ciega Bay":5})
        cp,x=run(low)
        assert cp.returncode!=0
        assert x["status"]=="STOP_EXECUTION_MANIFEST"
        assert any("Boca Ciega Bay" in e for e in x["errors"])

        off=td/"off.csv"
        write_manifest(off,{b:9 for b in BAYS},bad_offset=True)
        cp,x=run(off)
        assert cp.returncode!=0
        assert any(">14 d" in e for e in x["errors"])

        future=td/"future.csv"
        write_manifest(future,{b:9 for b in BAYS},add_future=True)
        cp,x=run(future)
        assert cp.returncode!=0
        assert x is None
        assert "forbidden future/outcome columns" in (cp.stdout+cp.stderr)

    print("TNC-v2 execution-manifest freeze tests: OK")

if __name__=="__main__":
    main()
