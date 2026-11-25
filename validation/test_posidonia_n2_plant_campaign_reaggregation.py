"""Synthetic Excel factor-identity tests for Nature 2021 root-piece vs plant data."""
from __future__ import annotations
import hashlib
import importlib.util
import io
import unittest
import zipfile
from pathlib import Path

PATH=Path(__file__).resolve().parents[1]/"analysis"/"124_posidonia_n2_plant_campaign_reaggregation.py"
SPEC=importlib.util.spec_from_file_location("posidonia_campaign",PATH)
M=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)

def colnum(n):
    out=""
    while n:
        n,v=divmod(n-1,26)
        out=chr(65+v)+out
    return out

def mock_xlsx(change=""):
    names=[]
    for camp,n in M.CAMPAIGN_EXPECTED.items():
        for j in range(n):
            names.append(camp+"_Plant"+str(j+1))
    if change=="missing_plant":
        names.pop()
    row3='<row r="3"><c r="A3" t="inlineStr"><is><t>Sample name</t></is></c>'
    row4='<row r="4"><c r="A4" t="inlineStr"><is><t>Accession number</t></is></c>'
    row5='<row r="5">'
    row6='<row r="6">'
    for i,name in enumerate(names,2):
        col=colnum(i)
        amount=2 if name.startswith("August2016") else 0 if name.startswith("April2016") else 1
        row3+=f'<c r="{col}3" t="inlineStr"><is><t>{name}</t></is></c>'
        row4+=f'<c r="{col}4" t="inlineStr"><is><t>ERS-SYNTHETIC-{i}</t></is></c>'
        row5+=f'<c r="{col}5"><v>{amount}</v></c>'
        row6+=f'<c r="{col}6"><v>{amount}</v></c>'
    second_panel='<row r="30"><c r="B30" t="inlineStr"><is><t>April2016_Plant1</t></is></c></row>'
    sheet='<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>'+row3+'</row>'+row4+'</row>'+row5+'</row>'+row6+'</row>'+second_panel+'</sheetData></worksheet>'
    book='<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheets><sheet name="Figure 2"/></sheets></workbook>'
    out=io.BytesIO()
    with zipfile.ZipFile(out,"w") as z:
        z.writestr("xl/workbook.xml",book)
        z.writestr("xl/worksheets/sheet1.xml",sheet)
    return out.getvalue()

class PlantLevelTests(unittest.TestCase):
    def with_sha(self,data,callback):
        prev=M.SHA
        try:
            M.SHA=hashlib.sha256(data).hexdigest()
            return callback()
        finally:
            M.SHA=prev

    def test_complete_31_plants_are_not_62_independent_root_pieces(self):
        raw=mock_xlsx()
        j=self.with_sha(raw,lambda:M.calculate_from_raw(raw))
        self.assertEqual(j["plant_count"],31)
        self.assertEqual(j["root_piece_measurement_count"],62)
        self.assertEqual({x["campaign"]:x["plants_distinct"] for x in j["campaigns"]},
                         M.CAMPAIGN_EXPECTED)
        self.assertEqual(j["same_year_2016_nonmatched_plants_apr_vs_aug"]["difference_aug_minus_apr_of_plant_mean_fixation"],2)

    def test_missing_plant_blocks_inference(self):
        raw=mock_xlsx(change="missing_plant")
        with self.assertRaises(ValueError):
            self.with_sha(raw,lambda:M.calculate_from_raw(raw))

    def test_fixed_original_source_digest_enforced(self):
        with self.assertRaises(ValueError):
            M.calculate_from_raw(mock_xlsx())

    def test_technical_zero_not_excluded(self):
        raw=mock_xlsx()
        j=self.with_sha(raw,lambda:M.calculate_from_raw(raw))
        apr=next(x for x in j["campaigns"] if x["campaign"]=="April2016")
        self.assertEqual(apr["all_root_piece_zero_counts"],10)
        self.assertEqual(apr["plant_means_positive_count"],0)

    def test_negative_assay_invalid(self):
        raw=mock_xlsx()
        # replace only the numeric root fragment for first plant
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            book=z.read("xl/workbook.xml")
            sheet=z.read("xl/worksheets/sheet1.xml").replace(b'<c r="B5"><v>0</v></c>',b'<c r="B5"><v>-1</v></c>')
        out=io.BytesIO()
        with zipfile.ZipFile(out,"w") as z:
            z.writestr("xl/workbook.xml",book)
            z.writestr("xl/worksheets/sheet1.xml",sheet)
        modified=out.getvalue()
        with self.assertRaises(ValueError):
            self.with_sha(modified,lambda:M.calculate_from_raw(modified))

if __name__=="__main__":unittest.main()
