"""No-network original-data schema and access stop tests; all fixtures synthetic."""
from __future__ import annotations
import importlib.util
import io
import json
import unittest
import urllib.error
import zipfile
from pathlib import Path

PATH=Path(__file__).resolve().parents[1]/"analysis"/"117_seagrass_interaction_original_data_preflight.py"
SPEC=importlib.util.spec_from_file_location("interaction_preflight",PATH)
M=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)

def fake_xlsx():
    buffer=io.BytesIO()
    with zipfile.ZipFile(buffer,"w") as z:
        z.writestr("xl/workbook.xml",'''<?xml version="1.0"?>
         <workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
           <sheets><sheet name="Experimental_Data" sheetId="1"/></sheets></workbook>''')
        z.writestr("xl/worksheets/sheet1.xml",'''<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
        <sheetData><row r="1"/><row r="2"/><row r="3"/></sheetData></worksheet>''')
    return buffer.getvalue()

class SourcePreflightTests(unittest.TestCase):
    def test_factorial_csv_detects_but_does_not_fit(self):
        b=b"site,fertilizer,deterrent,algal_biomass\nA,yes,no,2\nA,no,no,3\nB,yes,yes,4\n"
        x=M.csv_metadata(b)
        self.assertEqual(x["row_count"],3)
        self.assertEqual(x["site_label_uniques"]["site"],2)
        self.assertEqual(x["candidate_factor_level_counts"]["fertilizer"]["yes"],2)
        self.assertEqual(x["row_level_design_status"],"OUTCOME_SCHEMA_NOT_PREDECLARED_NO_EFFECT_FIT")

    def test_dryad_api_is_only_metadata(self):
        j={"title":"Synthetic lucinid experiment","versionNumber":1,
           "_links":{"stash:files":{"href":"/api/v2/versions/42/files"}}}
        x=M.dryad_metadata(json.dumps(j).encode())
        self.assertEqual(x["related_links"]["stash:files"],"/api/v2/versions/42/files")
        self.assertIn("NOT_YET_READ",x["status"])

    def test_xlsx_workbook_structure_without_outcomes(self):
        x=M.xlsx_metadata(fake_xlsx())
        self.assertEqual(x["sheet_count"],1)
        self.assertEqual(x["worksheet_xml_row_counts_including_headers"]["xl/worksheets/sheet1.xml"],3)
        self.assertIn("NOT_MAPPED",x["parse_status"])

    def test_fail_closed_no_download_failure_as_zero_effect(self):
        def blocker(url):
            raise urllib.error.HTTPError(url,403,"Synthetic restricted",hdrs=None,fp=None)
        x=M.report(fetcher=blocker)
        self.assertEqual(len(x["source_probe_results"]),4)
        self.assertTrue(all(y["status"]=="SOURCE_ACCESS_OR_SCHEMA_STOP" for y in x["source_probe_results"]))
        self.assertTrue(all(y["new_biological_effect_estimated"] is False for y in x["source_probe_results"]))

    def test_probe_source_with_synthetic_workbook(self):
        r=M.probe_source("Posidonia_N2_2021_figure1","https://fake.example/source.xlsx",fetcher=lambda _:fake_xlsx())
        self.assertEqual(r["status"],"SOURCE_RETRIEVED_METADATA_PROFILED")
        self.assertGreater(r["bytes"],0)

    def test_bad_workbook_fails(self):
        with self.assertRaises(ValueError):
            M.xlsx_metadata(b"not a zip")

if __name__=="__main__":unittest.main()
