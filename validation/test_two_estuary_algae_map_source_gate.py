"""Synthetic no-geometry tests for preselected Lemon and Dona/Roberts public map pairs."""
import importlib.util, unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/"analysis/104_two_estuary_algae_map_source_gate.py"
SPEC=importlib.util.spec_from_file_location("cross104",P)
M=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(M)

def fake_get(url,params):
    year="2022" if "2022" in url else "2024"
    n=6 if year=="2022" else 8
    if url.endswith("/FeatureServer"):return {"layers":[{"id":1}]}
    if url.endswith("/query"):
        if params["where"]=="1=1":return {"count":n}
        k=int(params["where"].split("=")[1])
        return {"count":({9113:3,9116:2,9121:1} if year=="2022" else
                         {9113:4,9116:3,9121:1})[k]}
    area="Geodesic" if year=="2022" else "ACRES"
    return {"type":"Feature Layer","geometryType":"esriGeometryPolygon",
      "objectIdField":"FID","extent":{
        "xmin":-9150000,"xmax":-9130000,"ymin":3080000,"ymax":3120000,
        "spatialReference":{"latestWkid":3857,"wkid":102100}},
      "fields":[{"name":"FID","type":"esriFieldTypeOID"},
                {"name":"FLUCCSCODE","type":"esriFieldTypeInteger"},
                {"name":"FLUCCSDESC","type":"esriFieldTypeString"},
                {"name":area,"type":"esriFieldTypeDouble"}]}

class FrozenSourceGate(unittest.TestCase):
    def test_fixed_two_site_scope_and_no_polygons(self):
        r=M.run(fake_get)
        self.assertEqual(r["status"],"PASS_SOURCE_METADATA_AND_CATEGORY_COUNTS_ONLY")
        self.assertFalse(r["polygon_geometry_downloaded"])
        self.assertFalse(r["areal_overlap_computed"])
        self.assertTrue(r["not_untouched_external_confirmatory_validation"])
        self.assertEqual(list(r["locations"]),["Lemon Bay","Dona and Roberts Bays"])
        self.assertEqual(r["locations"]["Lemon Bay"]["2022"]["class_counts"]["9121"],1)
    def test_zero_algae_in_one_year_is_observable_non_estimability_not_omission(self):
        def no_algae(url,params):
            v=fake_get(url,params)
            if "2024" in url and url.endswith("/query"):
                if params["where"]=="FLUCCSCODE=9121":return {"count":0}
                if params["where"]=="1=1":return {"count":7}
            return v
        r=M.run(no_algae)
        self.assertEqual(r["locations"]["Dona and Roberts Bays"]["2024"]["class_counts"]["9121"],0)
        self.assertFalse(r["locations"]["Lemon Bay"]["2024"]["focal_algae_present_in_map"])
    def test_unaccounted_code_hard_stop(self):
        def bad(url,params):
            v=fake_get(url,params)
            if url.endswith("/query") and params["where"]=="1=1":
                return {"count":v["count"]+1}
            return v
        with self.assertRaisesRegex(M.SourceStop,"MAPPED_CLASS_SUM_NOT_CLOSED"):
            M.run(bad)
    def test_unverified_area_field_hard_stop(self):
        def bad(url,params):
            v=fake_get(url,params)
            if url.endswith("/1") and "2022" in url:
                v["fields"]=[f for f in v["fields"] if f["name"]!="Geodesic"]
            return v
        with self.assertRaisesRegex(M.SourceStop,"AREA_MISSING"):
            M.run(bad)
    def test_no_unregistered_replacement_regions(self):
        self.assertEqual(set(M.CASES),{"Lemon Bay","Dona and Roberts Bays"})
        self.assertEqual(tuple(M.CODES),(9113,9116,9121))
if __name__=="__main__":unittest.main()
