"""Synthetic pre-exposure source-concordance tests. No new ecological field data."""
from pathlib import Path
import importlib.util, unittest, json, hashlib
from shapely.geometry import box,mapping,GeometryCollection
from shapely.ops import transform
ROOT=Path(__file__).resolve().parents[1]
sp=importlib.util.spec_from_file_location("ch114",ROOT/"analysis/114_charlotte_official_gain_loss_map_concordance.py")
M=importlib.util.module_from_spec(sp);sp.loader.exec_module(M)

def fake_layer():
    return {"geometryType":"esriGeometryPolygon","objectIdField":"FID",
       "fields":[{"name":"FID","type":"esriFieldTypeOID"},
                 {"name":"FLUCCSCODE","type":"esriFieldTypeDouble"},
                 {"name":"FLUCCSDESC","type":"esriFieldTypeString"},
                 {"name":"ACRES","type":"esriFieldTypeDouble"},
                 {"name":"Geodesic","type":"esriFieldTypeDouble"}]}
def pinned(meta,role,official=1,classes=None):
    h=hashlib.sha256(json.dumps(meta,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
    if classes is None:classes={"9113":1,"9116":0,"9121":0}
    return {"records":{role:{"layer_url":"https://example.org/test/"+role,
           "layer_metadata_sha256":h,"oid_field":"FID","official_polygon_count":official,
           "mapped_class_counts_9113_9116_9121":classes}}}
def mock(url,query):
    if not url.endswith("/query"):return fake_layer()
    if query.get("returnCountOnly"):return {"count":1}
    if query.get("returnIdsOnly"):return {"objectIds":[17]}
    source=box(-82.3,26.7,-82.29,26.71)
    area=M.G.transform(M.G.TRANSFORM,source).area/M.AREA
    props={"FID":17,"FLUCCSCODE":9113,"FLUCCSDESC":"Patchy Seagrass",
           "ACRES":area,"Geodesic":area}
    return {"type":"FeatureCollection","features":[{"type":"Feature",
             "properties":props,"geometry":mapping(source)}]}
class TestChangeGeometry(unittest.TestCase):
    def test_source_lock_and_verified_area(self):
        meta=fake_layer()
        a=M.get_change("mapped_seagrass_gain",pinned(meta,"mapped_seagrass_gain"),fetch=mock)
        self.assertEqual(a["count"],1)
        self.assertEqual(a["flucss_class_counts"]["9113"],1)
        self.assertGreater(a["mapped_all_three_class_acres"],0)
        self.assertLess(a["max_source_area_error_acres"],.005)
    def test_unknown_code_stops_not_assumed_seagrass(self):
        def bad(url,query):
            r=mock(url,query)
            if url.endswith("/query") and query.get("f")=="geojson":
                r["features"][0]["properties"]["FLUCCSCODE"]=9230
            return r
        with self.assertRaisesRegex(M.Stop,"UNRECOGNIZED_BENTHIC_CODE"):
            M.get_change("mapped_seagrass_gain",pinned(fake_layer(),"mapped_seagrass_gain"),fetch=bad)
    def test_9121_record_kept_as_algae_not_added_to_seagrass(self):
        def algae(url,query):
            r=mock(url,query)
            if url.endswith("/query") and query.get("f")=="geojson":
                r["features"][0]["properties"]["FLUCCSCODE"]=9121
            return r
        v=M.get_change("mapped_seagrass_gain",pinned(fake_layer(),"mapped_seagrass_gain",classes={"9113":0,"9116":0,"9121":1}),fetch=algae)
        self.assertEqual(v["flucss_class_counts"]["9121"],1)
        self.assertEqual(v["flucss_class_counts"]["9113"],0)
        self.assertTrue(v["class_9121_attached_algae_present"])
        self.assertEqual(v["mapped_class_areas_acres"]["9113"],0)
    def test_frozen_mixed_source_code_counts_cannot_change(self):
        def algae(url,query):
            r=mock(url,query)
            if url.endswith("/query") and query.get("f")=="geojson":
                r["features"][0]["properties"]["FLUCCSCODE"]=9121
            return r
        with self.assertRaisesRegex(M.Stop,"MIXED_CHANGE_CODE_COUNTS_NOT_REPRODUCED"):
            M.get_change("mapped_seagrass_gain",pinned(fake_layer(),"mapped_seagrass_gain"),fetch=algae)
    def test_oid_count_mismatch_stops(self):
        def wrong(url,query):
            r=mock(url,query)
            if query.get("returnCountOnly"):return {"count":2}
            return r
        with self.assertRaisesRegex(M.Stop,"COUNT_DRIFT"):
            M.get_change("mapped_seagrass_gain",pinned(fake_layer(),"mapped_seagrass_gain"),fetch=wrong)
    def test_official_gain_vs_source_fid_comparison_is_not_ecology(self):
        g=box(0,0,100,100)
        sample={"report":{"two_largest_source_algae_patches":[
            {"source_2022_FID":37,"source_algae_acres":2,
             "2024_mapped_seagrass_acres":1},
            {"source_2022_FID":2166,"source_algae_acres":2,
             "2024_mapped_seagrass_acres":1}]}}
        gain={"geometries_by_class":{9113:box(0,0,50,100),9116:GeometryCollection(),9121:box(50,0,75,100)}}
        loss={"geometries_by_class":{9113:GeometryCollection(),9116:box(90,0,100,100),9121:box(80,0,90,100)}}
        r=M.compare({"37":g,"2166":g},gain,loss,sample)
        self.assertEqual(len(r),2)
        self.assertTrue(r["37"]["same_original_imagery_not_independent_ecology"])
        self.assertGreater(r["37"]["agency_gain_9113_9116_overlap_acres"],0)
        self.assertGreater(r["37"]["agency_loss_9121_overlap_acres"],0)
        self.assertGreater(r["37"]["official_change_layer_code_specific_overlap_acres"]["gain_code_9121_overlap_acres"],0)
        self.assertTrue(r["37"]["agency_gain_code_9121_overlaps_are_not_seagrass"])
if __name__=="__main__": unittest.main()
