#!/usr/bin/env python3
"""Inspect an authorized SWFWMD / SEACAR seagrass ZIP BEFORE spatial claims.

Never registers for restricted downloads, invents an email, or fetches data.
Reads local ZIP contents safely in memory without extracting file paths.
For each shapefile group reports record counts and full FLUCCS_CODE dictionary,
shape type, source CRS text hash, source area fields and evidence limits.
This may show that the so-called original ZIP still contains only 9113/9116/
9121, in which case it CANNOT resolve the 222-acres target-unmapped fate.

This is a SOURCE INTAKE GATE, NOT a seagrass mortality or restoration test.
"""
from __future__ import annotations
import argparse,hashlib,io,json,os,sys,zipfile
from collections import Counter
from pathlib import Path

try:
    import shapefile
except ImportError:
    raise SystemExit("STOP: install pyshp for original SWFWMD ZIP validation")
FIELD_CANDIDATES=("FLUCCSCODE","FLUCCS_CODE","FLUCCS")
MAPPED_ONLY={"9113","9116","9121"}
MAX_FILES=20000
MAX_ZIP_BYTES=2_000_000_000
MAX_TABLE_FIELDS=1000
LAYER_SHAPE_TYPES={5,15,25,31}
SCHEMA="tampa.original_swfwmd_seagrass_zip_classification_source_gate_v1"

class Stop(ValueError):pass

def inspect_zip(path):
    p=Path(path)
    if not p.is_file():
        raise Stop("LOCAL_SOURCE_ZIP_NOT_FOUND")
    if p.stat().st_size>MAX_ZIP_BYTES:
        raise Stop("SOURCE_ZIP_TOO_LARGE_FOR_SAFE_INTAKE")
    blob_sha=hashlib.sha256(p.read_bytes()).hexdigest()
    with zipfile.ZipFile(p) as z:
        infos=z.infolist()
        if len(infos)>MAX_FILES or not infos: raise Stop("SOURCE_ARCHIVE_MEMBERS_INVALID")
        names=[x.filename for x in infos if not x.is_dir()]
        if len(names)!=len(set(names)):raise Stop("DUPLICATED_ZIP_MEMBER_PATH")
        if any(x.startswith("/") or ".." in Path(x).parts or "\\" in x for x in names):
            raise Stop("UNSAFE_ZIP_MEMBER_PATH")
        parts={}
        for x in names:
            y=Path(x)
            if y.suffix.lower() not in (".shp",".shx",".dbf",".prj"):
                continue
            k=str(y.with_suffix(""))
            parts.setdefault(k,{})[y.suffix.lower()]=x
        layers=[]
        for stem,files in sorted(parts.items()):
            if ".dbf" not in files or ".shp" not in files or ".shx" not in files:
                raise Stop("MISSING_SHAPEFILE_TRIPLET:"+stem)
            data={suffix:io.BytesIO(z.read(files[suffix])) for suffix in (".shp",".shx",".dbf")}
            try:
                sh=shapefile.Reader(shp=data[".shp"],shx=data[".shx"],dbf=data[".dbf"])
            except Exception as e:
                raise Stop("UNREADABLE_SHAPEFILE:"+stem+":"+type(e).__name__) from e
            if sh.shapeType not in LAYER_SHAPE_TYPES:
                raise Stop("SOURCE_LAYER_NOT_POLYGON:"+stem)
            fields=[x[0] for x in sh.fields[1:]]
            if len(fields)>MAX_TABLE_FIELDS:raise Stop("TOO_MANY_DB_FIELDS")
            upper={f.upper():f for f in fields}
            cls=next((upper[x] for x in FIELD_CANDIDATES if x in upper),None)
            counts=Counter()
            if cls:
                pos=fields.index(cls)
                for row in sh.iterRecords():
                    value=row[pos]
                    if value is None:label="NULL"
                    elif isinstance(value,(float,int)) and float(value).is_integer():
                        label=str(int(value))
                    else:label=str(value).strip()
                    counts[label]+=1
                if sum(counts.values())!=len(sh):
                    raise Stop("CLASS_RECORDS_NOT_CLOSED:"+stem)
            prj_hash=None
            if ".prj" in files:
                prj=z.read(files[".prj"])
                prj_hash=hashlib.sha256(prj).hexdigest()
            matched=sum(counts[x] for x in MAPPED_ONLY)
            non3=sum(v for k,v in counts.items() if k not in MAPPED_ONLY)
            layers.append({
                "stem":stem,
                "n_records":len(sh),
                "shapefile_type":sh.shapeType,
                "all_dbf_fields":fields,
                "class_code_field":cls,
                "full_class_code_counts":dict(sorted(counts.items())),
                "mapped_9113_9116_9121_records":matched,
                "non_three_class_records":non3,
                "original_area_field_candidates":[f for f in fields if
                       "ACRE" in f.upper() or "AREA" in f.upper() or "GEODESIC" in f.upper()],
                "projection_wkt_sha256":prj_hash,
                "has_prj":".prj" in files,
                "all_2024_benthic_classes_proved_complete":False,
                "surveyed_photo_footprint_identified":False
            })
    if not layers:
        return {
           "schema":SCHEMA,"status":"STOP_NO_SHAPEFILE_GROUPS_OR_GDB_ONLY",
           "source_zip_path":p.name,"source_sha256":blob_sha,
           "n_zip_files":len(names),
           "contains_gdb_paths":any(".gdb/" in n.lower() for n in names),
           "no_2024_benthic_fate_estimated":True
        }
    codes=set(k for s in layers for k in s["full_class_code_counts"])
    return {
      "schema":SCHEMA,"status":"PASS_LOCAL_ARCHIVE_CLASS_DICTIONARY_INTAKE_ONLY",
      "source_zip_path":p.name,"source_sha256":blob_sha,
      "n_zip_files":len(names),
      "n_polygon_shapefile_groups":len(layers),
      "shapefile_group_registry":layers,
      "all_observed_class_codes":sorted(codes),
      "only_restricted_three_categories_seen_in_classified_files":bool(codes) and codes.issubset(MAPPED_ONLY),
      "other_benthic_classes_observed":bool(codes-MAPPED_ONLY),
      "all_benthic_classes_and_photo_footprint_confirmed_complete":False,
      "not_source_map_fate_or_biological_response":True,
      "interpretation":"A ZIP with only 9113/9116/9121 cannot classify the 2024 source area not represented in the published three-class map. Even a ZIP with other codes does not prove it has full imagery/field observation coverage. Verify data vintage, class dictionary, region, source polygons and map footprint before spatial overlay."
    }

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source-zip",required=True)
    ap.add_argument("--out",required=True)
    a=ap.parse_args()
    try:
        report=inspect_zip(a.source_zip)
        rc=0 if report["status"].startswith("PASS_") else 2
    except (Stop,zipfile.BadZipFile,OSError,TypeError,ValueError) as e:
        report={"schema":SCHEMA,"status":"STOP_ORIGINAL_SOURCE_ZIP_INVALID",
                "reason":str(e),"no_benthic_fate_inferred":True}
        rc=2
    target=Path(a.out);target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(report,indent=2,ensure_ascii=False,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2,ensure_ascii=False,sort_keys=True))
    return rc

if __name__=="__main__":sys.exit(main())
