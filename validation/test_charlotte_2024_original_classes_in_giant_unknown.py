"""Synthetic source-locked 2024 original district GIS all-class overlap tests."""
from __future__ import annotations
import importlib.util,unittest
from pathlib import Path
from shapely.geometry import box,GeometryCollection,mapping
from shapely.ops import transform

ROOT=Path(__file__).resolve().parents[1]
SP=importlib.util.spec_from_file_location("ch126",ROOT/"analysis/126_charlotte_2024_original_classes_in_giant_unknown.py")
M=importlib.util.module_from_spec(SP);SP.loader.exec_module(M)

def empty_codes():
    return {c:GeometryCollection() for c in M.CODES}

class OriginalClassUnknown(unittest.TestCase):
    def test_full_reclassification_of_2024_threeclass_unknown_as_other_code(self):
        giant=box(0,0,200,100)
        hosted_2024=box(0,0,100,100)
        other=empty_codes()
        other[5400]=box(100,0,200,100)
        r=M.independent_source_overlap(giant,hosted_2024,other)
        self.assertAlmostEqual(r["unknown_2024_3class_area_acres"],10000/M.AREA,places=6)
        self.assertAlmostEqual(r["source_2024_original_non_three_code_coverage_acres"],10000/M.AREA,places=6)
        self.assertAlmostEqual(r["no_2024_original_class_map_polygon_overlapping_acres"],0,places=6)
        self.assertTrue(r["not_bare_substrate_or_biological_absence"])
    def test_unmapped_not_automatically_covered_when_orig_district_category_missing(self):
        giant=box(0,0,200,100)
        hosted=box(0,0,100,100)
        r=M.independent_source_overlap(giant,hosted,empty_codes())
        self.assertAlmostEqual(r["no_2024_original_class_map_polygon_overlapping_acres"],10000/M.AREA,places=6)
    def test_original_threecode_category_can_expose_hosted_omission(self):
        giant=box(0,0,200,100)
        hosted=box(0,0,100,100)
        orig=empty_codes()
        orig[9113]=box(100,0,200,100)
        r=M.independent_source_overlap(giant,hosted,orig)
        self.assertGreater(r["source_2024_original_three_code_coverage_acres"],0)
        self.assertEqual(r["source_2024_original_non_three_code_coverage_acres"],0)
    def test_source_id_query_rejects_duplicate_and_count_drift(self):
        def bad(url,params):
            if params.get("returnIdsOnly")=="true":return {"objectIdFieldName":"OBJECTID","objectIds":[1,2,2]}
            return {"count":3}
        with self.assertRaisesRegex(M.Stop,"GIANT_BBOX_ID_ROSTER_INVALID"):
            M.source_ids_by_bbox(box(-7918209,3301405,-7918000,3301600),bad)
    def test_original_source_geometries_fetched_by_exact_oid_only(self):
        def fixture(url,params):
            if params.get("f")!="geojson":raise AssertionError("Must request actual geojson")
            ids=[int(v) for v in params["objectIds"].split(",")]
            fs=[]
            for oid in ids:
                a=-82.3 + oid*.001
                fs.append({"type":"Feature","properties":{"OBJECTID":oid,"FLUCCSCODE":5400},
                            "geometry":mapping(box(a,26.7,a+.0005,26.7005))})
            return {"type":"FeatureCollection","features":fs}
        features=M.fetch_original_features([1,2,3],fixture)
        self.assertEqual(len(features),3)
        geoms,repaired=M.mapped_shapes(features)
        self.assertGreater(geoms[5400].area,0)
        self.assertTrue(geoms[5400].is_valid)
        self.assertEqual(repaired,0)
    def test_pinned_code_registry_includes_extra_9122(self):
        self.assertEqual(M.CODES,(0,5400,6510,6540,7210,9113,9116,9121,9122))
        self.assertEqual(M.BACKGROUND,(0,5400,6510,6540,7210,9122))
        self.assertEqual(M.MAX_OIDS,4000)
if __name__=="__main__":unittest.main()
