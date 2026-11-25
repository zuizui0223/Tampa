"""No-network field experiment source and failure-state checks."""
from __future__ import annotations
import importlib.util
import json
import unittest
from pathlib import Path
PATH=Path(__file__).resolve().parents[1]/"analysis"/"121_lucinid_2020_field_experiment_source_gate.py"
SPEC=importlib.util.spec_from_file_location("lucinid_field",PATH)
M=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)

class FieldOriginalSource(unittest.TestCase):
    def test_official_file_manifest(self):
        files=[{"id":i,"path":path} for i,path in enumerate(M.KEY_FILES,1)]
        got=M.resolve_files({"_embedded":{"stash:files":files}})
        self.assertEqual(set(got),set(M.KEY_FILES))
        self.assertEqual(got[M.KEY_FILES[0]]["url"],"https://datadryad.org/api/v2/files/1/download")

    def test_source_first_rows_without_effect(self):
        b=b"block\tclams\tsulfide\tplant_biomass\n1\t0\t3\t4\n2\t1\t1\t8\n"
        x=M.summarize_text(b)
        self.assertEqual(x["lines"],3)
        self.assertEqual(len(x["first_row_fields"]),4)
        self.assertIn("NO_FACTORIAL_EFFECT",x["text_parse_status"])

    def test_mock_three_files_open_without_effect(self):
        meta=json.dumps({"_links":{"stash:version":{"href":"/api/v2/versions/321"}}}).encode()
        files=json.dumps({"_embedded":{"stash:files":[
            {"id":i,"path":p} for i,p in enumerate(M.KEY_FILES,1)]}}).encode()
        def mocked(url):
            if url==M.DATASET_ENDPOINT:return meta
            if url=="https://datadryad.org/api/v2/versions/321/files":return files
            return b"header1\theader2\n1\t2\n"
        x=M.report(fetcher=mocked)
        self.assertEqual(x["source_status"],"ORIGINAL_FIELD_FILES_RETRIEVED_TREATMENT_MAPPING_NOT_FROZEN")
        self.assertEqual(len(x["files_from_authoritative_version"]),3)
        self.assertTrue(x["no_effect_estimators_fitted"])

    def test_missing_original_source_not_treated_as_zero_effect(self):
        x=M.report(fetcher=lambda url:(_ for _ in ()).throw(ValueError("Synthetic no file")))
        self.assertEqual(x["source_status"],"OFFICIAL_SOURCE_OR_SCHEMA_STOP")
        self.assertTrue(x["no_effect_estimators_fitted"])

    def test_bad_file_path_rejected(self):
        with self.assertRaises(ValueError):
            M.href({"_links":{"stash:version":{"href":"https://other.com"}}},"stash:version")

if __name__=="__main__":unittest.main()
