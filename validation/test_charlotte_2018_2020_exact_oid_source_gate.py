"""Source-only 2018/2020 unique official OID inventory gate synthetic checks."""
from pathlib import Path
import importlib.util,unittest
S=importlib.util.spec_from_file_location("ch123",Path(__file__).resolve().parents[1]/"analysis/123_charlotte_2018_2020_exact_oid_source_gate.py")
M=importlib.util.module_from_spec(S);S.loader.exec_module(M)
BBOX={"xmin":-9000,"ymin":3000,"xmax":-7000,"ymax":5000}
def source():
    return {"status":"PASS_OFFICIAL_LEGACY_MAP_METADATA_AND_CLASS_COUNTS_ONLY",
      "years":{y:{
        "metadata_sha256":M.sha(meta(y)),
        "map_extent_2016_2024_reference_envelope_3857":BBOX,
        "n_legacy_source_features_intersecting_envelope":5,
        "n_by_focal_legacy_flucss_code":{"9113":3,"9116":2,"9121":0}}
        for y in ("2018","2020")}}
def meta(year):
    return {"name":"Seagrass in "+year,
      "fields":[{"name":"OBJECTID","type":"esriFieldTypeOID"},
                {"name":"FLUCCSCODE","type":"esriFieldTypeInteger"},
                {"name":"FLUCCSDESC","type":"esriFieldTypeString"},
                {"name":"Shape__Area","type":"esriFieldTypeDouble"}]}
class APITest:
    def __init__(self,bad=False):self.bad=bad;self.calls=[]
    def __call__(self,url,params):
        self.calls.append((url,params))
        year="2018" if url.split(M.M.SOURCE_BASE+"/")[1].split("/")[0]=="0" else "2020"
        if url.endswith("/query"):
            w=params["where"]
            ids=[1,2,3,4,5] if w=="1=1" else [1,2,3] if w=="FLUCCSCODE=9113" else [4,5] if w=="FLUCCSCODE=9116" else []
            if self.bad and w=="FLUCCSCODE=9113":ids=[1,2,2]
            return {"objectIdFieldName":"OBJECTID","objectIds":ids}
        return meta(year)
class Tests(unittest.TestCase):
    def test_exact_source_roster_without_geometry(self):
        q=APITest();r=M.audit(q,source)
        self.assertEqual(r["status"],"PASS_HISTORICAL_GIS_EXACT_SOURCE_ID_INVENTORIES_ONLY")
        self.assertEqual(r["years"]["2018"]["bbox_all_oid_count"],5)
        self.assertEqual(r["years"]["2020"]["focal_class_id_audits"]["9121"]["count"],0)
        self.assertTrue(r["years"]["2018"]["strict_original_source_acreage_crosscheck_possible"])
        self.assertTrue(all(p.get("returnGeometry")!="true" for _,p in q.calls))
        self.assertFalse(r["2018_and_2020_polygon_areas_computed"])
    def test_arcgis_null_id_list_accepted_only_for_frozen_zero_algae_code(self):
        class SourceNull(APITest):
            def __call__(self,url,params):
                v=super().__call__(url,params)
                if url.endswith("/query") and params.get("where")=="FLUCCSCODE=9121":
                    v["objectIds"]=None
                return v
        r=M.audit(SourceNull(),source)
        self.assertEqual(r["years"]["2018"]["focal_class_id_audits"]["9121"]["count"],0)
        self.assertEqual(r["years"]["2020"]["focal_class_id_audits"]["9121"]["count"],0)
    def test_arcgis_null_positive_class_ids_is_hard_stop(self):
        class SourceNullPositive(APITest):
            def __call__(self,url,params):
                v=super().__call__(url,params)
                if url.endswith("/query") and params.get("where")=="FLUCCSCODE=9113":
                    v["objectIds"]=None
                return v
        with self.assertRaisesRegex(M.Stop,"LEGACY_CLASS_EXACT_SOURCE_ID_COUNT_DRIFT"):
            M.audit(SourceNullPositive(),source)
    def test_duplicate_focal_code_ids_refused(self):
        with self.assertRaisesRegex(M.Stop,"EXACT_SOURCE_ID_COUNT_DRIFT"):
            M.audit(APITest(bad=True),source)
    def test_no_source_backfilled_year(self):
        self.assertEqual(M.M.LAYERS,{"2018":0,"2020":1})
        self.assertEqual(set(M.AREA_FIELDS),set(("ACRES","Geodesic","Area_Acres","AREA_ACRES","SHAPE_Area","Shape__Area")))
if __name__=="__main__":unittest.main()
