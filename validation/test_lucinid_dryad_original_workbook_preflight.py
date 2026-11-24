"""Synthetic XLSX/API tests for Dryad 2012 lucinid original experiment preflight."""
from __future__ import annotations
import importlib.util
import io
import json
import unittest
import zipfile
from pathlib import Path
PATH=Path(__file__).resolve().parents[1]/"analysis"/"119_lucinid_dryad_original_workbook_preflight.py"
SPEC=importlib.util.spec_from_file_location("lucinid2012",PATH)
M=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)

def workbook():
    b=io.BytesIO()
    with zipfile.ZipFile(b,"w") as z:
        z.writestr("xl/workbook.xml",'''<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheets><sheet name="Experiment" sheetId="1"/></sheets></workbook>''')
        z.writestr("xl/sharedStrings.xml",'''<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><si><t>treatment</t></si><si><t>no bivalve</t></si></sst>''')
        z.writestr("xl/worksheets/sheet1.xml",'''<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData><row r="1"><c r="A1" t="s"><v>0</v></c></row><row r="2"><c r="A2" t="s"><v>1</v></c><c r="B2"><v>22.4</v></c></row></sheetData></worksheet>''')
    return b.getvalue()

class DryadOriginalExperimentTests(unittest.TestCase):
    def test_official_file_listing_selects_unique_file(self):
        j={"_embedded":{"stash:files":[{"id":42,"path":"Experimental_data.xlsx",
            "_links":{"stash:download":{"href":"/api/v2/files/42/download"}}}]}}
        d=M.file_manifest(j)
        self.assertEqual(d["file_id"],42)
        self.assertEqual(d["download_url"],"https://datadryad.org/api/v2/files/42/download")

    def test_original_zip_metadata_and_small_header_preview(self):
        x=M.workbook_outline(workbook())
        self.assertEqual(x["sheet_names"],["Experiment"])
        p=x["worksheet_previews"]["xl/worksheets/sheet1.xml"]
        self.assertEqual(p["worksheet_xml_rows"],2)
        self.assertEqual(p["nonempty_preview_rows_max10"][0]["cells"]["A1"],"treatment")
        self.assertEqual(p["nonempty_preview_rows_max10"][1]["cells"]["B2"],"22.4")
        self.assertIn("NO_EFFECT_FIT",x["status"])

    def test_full_response_workbook_first_stage_never_fits(self):
        manifest=json.dumps({"_embedded":{"stash:files":[{"id":42,"path":"Experimental_data.xlsx"}]}}).encode()
        def fake(url):
            return manifest if url==M.VERSION_FILES else workbook()
        x=M.report(fetcher=fake)
        self.assertEqual(x["status"],"ORIGINAL_WORKBOOK_RETRIEVED_TREATMENT_MAPPING_REQUIRED")
        self.assertEqual(x["workbook"]["sheet_names"],["Experiment"])

    def test_no_workbook_download_counted_as_no_effect(self):
        def blocked(url):raise ValueError("synthetic HTTP 403")
        x=M.report(fetcher=blocked)
        self.assertEqual(x["status"],"OFFICIAL_SOURCE_OR_SCHEMA_BLOCKED")
        self.assertIsNone(x["new_experimental_effects"])

    def test_ambiguous_source_list_fails_closed(self):
        with self.assertRaises(ValueError):
            M.file_manifest({"files":[{"id":1,"path":"Experimental_data.xlsx"},{"id":2,"path":"Experimental_data.xlsx"}]})

if __name__=="__main__":unittest.main()
