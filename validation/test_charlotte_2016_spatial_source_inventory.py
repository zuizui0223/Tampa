"""Synthetic source-inventory gate tests: no 2016 polygon/biological response opens."""
from pathlib import Path
import importlib.util
import unittest
mod=Path(__file__).resolve().parents[1]/"analysis/97_charlotte_2016_spatial_source_inventory.py"
spec=importlib.util.spec_from_file_location("ch97",mod)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

CODES={"9113":20,"9116":35,"9121":5,"6510":10,"6540":7,"7210":3,"0":0,"5400":0}
class Stub:
    def __init__(self,bad=False):self.calls=[];self.bad=bad
    def __call__(self,url,params):
        self.calls.append((url,params))
        if url==m.HIST:
            return {"geometryType":"esriGeometryPolygon",
                "fields":[{"name":"OBJECTID","type":"esriFieldTypeOID"},
                          {"name":"FLUCCS_CODE","type":"esriFieldTypeString"},
                          {"name":"ACRES","type":"esriFieldTypeDouble"}],
                "extent":{"spatialReference":{"wkid":2882}}}
        if url in m.CURRENT.values():
            y="2022" if "2022" in url else "2024"
            b=0 if y=="2022" else 100
            return {"geometryType":"esriGeometryPolygon","objectIdField":"FID",
                    "extent":{"xmin":-9000+b,"ymin":3000+b,"xmax":-7000+b,
                              "ymax":5000+b,"spatialReference":{"latestWkid":3857}}}
        if params.get("returnDistinctValues"):
            vals=list(CODES)+(["9999"] if self.bad else [])
            return {"features":[{"attributes":{"FLUCCS_CODE":code}} for code in vals]}
        if params.get("returnCountOnly"):
            where=params["where"]
            if where=="1=1":
                return {"count":21026 if "geometry" not in params else 80+(1 if self.bad else 0)}
            return {"count":CODES[where.split("'")[1]]}
        raise AssertionError("Unexpected query "+str(params))

class SourceInventoryTests(unittest.TestCase):
    def test_metadata_and_spatial_counts_only(self):
        stub=Stub()
        r=m.spatial_counts(stub)
        self.assertEqual(r["status"],"PASS_METADATA_SPATIAL_COUNTS_ONLY")
        self.assertEqual(r["whole_district_2016_polygon_count"],21026)
        self.assertEqual(r["2016_envelope_intersecting_polygon_count"],80)
        self.assertEqual(r["2016_envelope_counts_by_code"],CODES)
        self.assertFalse(r["source_feature_geometries_downloaded"])
        self.assertFalse(r["2016_to_2022_2024_overlap_computed"])
        self.assertTrue(all(p.get("returnGeometry")!="true" for _,p in stub.calls))
    def test_unexpected_class_count_is_stopped_not_ignored(self):
        with self.assertRaisesRegex(m.GateStop,"UNKNOWN_CLASS_COUNT_IN_2016_ENVELOPE"):
            m.spatial_counts(Stub(bad=True))
    def test_wrong_legacy_crs_stops(self):
        base=Stub()
        def f(url,params):
            x=base(url,params)
            if url==m.HIST:x["extent"]["spatialReference"]["wkid"]=3857
            return x
        with self.assertRaisesRegex(m.GateStop,"LEGACY_CRS_UNEXPECTED"):
            m.spatial_counts(f)
    def test_unavailable_distinct_endpoint_is_not_needed(self):
        stub=Stub()
        r=m.spatial_counts(stub)
        self.assertEqual(r["2016_envelope_unmatched_code_count"],0)
        self.assertIn("9116",r["2016_envelope_documented_codes_with_positive_counts"])
        self.assertFalse(any(p.get("returnDistinctValues") for _,p in stub.calls))

if __name__=="__main__":unittest.main()
