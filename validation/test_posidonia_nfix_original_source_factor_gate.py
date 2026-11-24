"""Synthetic ZIP/XLSX source-lock tests for Posidonia N2 symbiosis workbooks."""
from __future__ import annotations
import importlib.util
import io
import unittest
import zipfile
import hashlib
from pathlib import Path
PATH=Path(__file__).resolve().parents[1]/"analysis"/"123_posidonia_nfix_original_source_factor_gate.py"
SPEC=importlib.util.spec_from_file_location("posidonia_n2",PATH)
M=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)

def make_xlsx():
    b=io.BytesIO()
    with zipfile.ZipFile(b,"w") as z:
        z.writestr("xl/workbook.xml",'<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheets><sheet name="Figure 1"/></sheets></workbook>')
        z.writestr("xl/sharedStrings.xml",'<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><si><t>month</t></si></sst>')
        z.writestr("xl/worksheets/sheet1.xml",'<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData><row r="1"><c r="A1" t="s"><v>0</v></c></row><row r="2"><c r="A2" t="inlineStr"><is><t>Apr</t></is></c><c r="B2"><v>0.31</v></c></row></sheetData></worksheet>')
    return b.getvalue()

class SourceNfixTests(unittest.TestCase):
    def test_xlsx_row_mapping(self):
        names,sheets=M.unpack(make_xlsx())
        self.assertEqual(names,["Figure 1"])
        self.assertEqual(len(sheets["xl/worksheets/sheet1.xml"]),2)
        self.assertEqual(sheets["xl/worksheets/sheet1.xml"][0]["cells"]["A1"],"month")
        self.assertEqual(sheets["xl/worksheets/sheet1.xml"][1]["cells"]["B2"],"0.31")

    def test_wrong_source_hash_rejected(self):
        with self.assertRaises(ValueError):
            M.inspect_one("figure1",make_xlsx())

    def test_mock_source_full_gate_only_maps_and_never_fits(self):
        data=make_xlsx()
        old=M.FILES["figure1"].copy()
        try:
            M.FILES["figure1"]["sha256"]=hashlib.sha256(data).hexdigest()
            x=M.inspect_one("figure1",data)
            self.assertEqual(x["unmapped_status"],"ORIGINAL_VALUES_INSPECTED_NO_INFERENTIAL_COMPARISON")
            self.assertEqual(len(x["first25_nonempty_source_rows_for_factor_mapping"]),2)
        finally:
            M.FILES["figure1"].update(old)

    def test_no_source_records_zero_effect(self):
        x=M.report(fetcher=lambda url:(_ for _ in ()).throw(ValueError("synthetic unavailable")))
        self.assertEqual(x["files"]["figure1"]["status"],"RETRIEVAL_OR_SCHEMA_STOP")
        self.assertEqual(x["files"]["figure2"]["status"],"RETRIEVAL_OR_SCHEMA_STOP")

    def test_no_cross_species_inference(self):
        x=M.report(fetcher=lambda url:(_ for _ in ()).throw(ValueError("unavailable")))
        self.assertTrue(any("Thalassia" in y for y in x["claim_limits"]))

if __name__=="__main__":unittest.main()
