"""Synthetic legacy ArcGIS grouped class code diagnostic tests."""
import importlib.util,unittest
from pathlib import Path
p=Path(__file__).resolve().parents[1]/"analysis/99_charlotte_2016_legacy_class_dictionary.py"
s=importlib.util.spec_from_file_location("old99",p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
C={"6510":10,"6540":7,"7210":3,"9113":20,"9116":15,"9121":5,"9230":2}

class Mock:
    def __init__(self,wrong=False):self.calls=[];self.wrong=wrong
    def __call__(self,url,params):
        self.calls.append((url,params))
        if url in m.M.CURRENT.values():
            return {"extent":{"xmin":-9150000,"ymin":3090000,"xmax":-9130000,"ymax":3120000}}
        if params.get("groupByFieldsForStatistics"):
            counts=dict(C)
            if self.wrong:counts["9230"]=3
            return {"features":[{"attributes":{"FLUCCS_CODE":k,"n":v}} for k,v in counts.items()]}
        if params.get("returnCountOnly"):
            if params["where"]=="1=1":return {"count":sum(C.values())}
            return {"count":C[params["where"].split("'")[1]]}
        raise AssertionError("Unexpected query")

class CodeAuditTests(unittest.TestCase):
    def test_unknown_class_is_exposed_not_called_absence(self):
        stub=Mock();r=m.audit(stub)
        self.assertEqual(r["status"],"PASS_CATEGORY_SOURCE_DIAGNOSTIC_ONLY")
        self.assertEqual(r["unrecognized_count"],2)
        self.assertEqual(r["unmapped_to_known_six_classes"],{"9230":2})
        self.assertTrue(r["unrecognized_classes_are_not_absence"])
        self.assertFalse(r["polygon_geometries_downloaded"])
        self.assertFalse(r["2016_2022_2024_transitions_computed"])
        self.assertFalse(any(q.get("returnGeometry")=="true" for _,q in stub.calls))
    def test_unclosed_counts_are_rejected(self):
        with self.assertRaisesRegex(m.M.GateStop,"COUNTS_DO_NOT_SUM"):
            m.audit(Mock(wrong=True))

if __name__=="__main__":unittest.main()
