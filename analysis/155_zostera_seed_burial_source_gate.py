#!/usr/bin/env python3
"""Public-source schema gate for Jorgensen et al. 2019 seed burial experiment.
Four published supplementary workbooks; no inferred plant or seed-level joins.
"""
import hashlib,io,json,urllib.request,urllib.error,zipfile
from pathlib import Path
import openpyxl
ROOT=Path("seed_burial_source")
DOI="10.1371/journal.pone.0215157"
SOURCES={"s001":"seed_size_metrics","s002":"seedling_emergence","s003":"unemerged_seed_fates","s004":"seedling_biomass"}
LIMIT=12_000_000
def get(s):
    url=f"https://journals.plos.org/plosone/article/file?id=10.1371%2Fjournal.pone.0215157.{s}&type=supplementary"
    record={"supplement_doi":DOI+"."+s,"description":SOURCES[s],"url":url}
    try:
        req=urllib.request.Request(url,headers={"User-Agent":"Tampa-seed-burial-source-audit/1.0","Accept-Encoding":"identity"})
        with urllib.request.urlopen(req,timeout=45) as r:b=r.read(LIMIT+1)
        if len(b)>LIMIT or not zipfile.is_zipfile(io.BytesIO(b)):raise ValueError("invalid workbook or size cap")
        with zipfile.ZipFile(io.BytesIO(b)) as z:
            if sum(i.file_size for i in z.infolist())>60_000_000:raise ValueError("expansion cap")
        w=openpyxl.load_workbook(io.BytesIO(b),read_only=True,data_only=True)
        sheets=[]
        for sheet in w:
            # Preview only for column and experimental-unit mapping.
            sheets.append(dict(name=sheet.title,declared_rows=sheet.max_row,declared_cols=sheet.max_column,
                first_rows=list(sheet.iter_rows(min_row=1,max_row=8,values_only=True))))
        w.close()
        (ROOT/(s+".xlsx")).write_bytes(b)
        record.update(status="ACQUIRED_SCHEMA_ONLY",sha256=hashlib.sha256(b).hexdigest(),bytes=len(b),sheets=sheets)
    except (OSError,ValueError,KeyError,zipfile.BadZipFile,openpyxl.utils.exceptions.InvalidFileException) as e:
        record.update(status="ACCESS_OR_SCHEMA_STOP",reason=str(e)[:250])
    return record
if __name__=="__main__":
    ROOT.mkdir(exist_ok=True)
    report={"status":"source_inventory_only","paper_doi":DOI,"sources":[get(s) for s in SOURCES],
      "boundaries":["Five outdoor tanks, fifteen seeds per pot. Sorted large/small seed treatments at 2,4,6 cm (30 pots). Unsorted two separate destructive harvest cohorts at seven depths (70 pots).",
      "Size metrics may come from different seed samples than emergence observations; no individual seed-mass-to-fate pairing assumed.",
      "Before joining any tables verify tank, pot, size class, depth, observation date and harvest-cohort identifiers. Never join only by treatment means.",
      "Distinguish emerged seedlings, failed emergence, dead seeds, viable unemerged seeds and unresolved/missing fates. No imputation as dead or alive.",
      "Biomass is conditional on recovered seedlings; no whole-seed establishment effect without a valid denominator. No transfer to 2025 father-genotype seed masses without calibration.",
      "Inventory success is not successful acquisition of every file and not an empirical reanalysis."]}
    (ROOT/"source_manifest.json").write_text(json.dumps(report,indent=2,sort_keys=True,default=str)+"\n")
    print(json.dumps(report,indent=2,sort_keys=True,default=str))
