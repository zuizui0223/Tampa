"""Pure synthetic proof that historical 2016 layer metadata gate has no outcome access."""
import importlib.util,unittest
from pathlib import Path
p=Path(__file__).resolve().parents[1]/"analysis/96_charlotte_2016_historical_gis_metadata_gate.py"
s=importlib.util.spec_from_file_location("legacy96",p)
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)

def example_meta(**updates):
    v={"name":"Synthetic 2016 source","type":"Feature Layer",
       "geometryType":"esriGeometryPolygon","objectIdField":"OBJECTID",
       "fields":[{"name":"OBJECTID","type":"esriFieldTypeOID"},
                 {"name":"FLUCCS_CODE","type":"esriFieldTypeString"}],
       "extent":{"xmin":0,"ymin":0,"xmax":1,"ymax":1,
                 "spatialReference":{"wkid":102658}},
       "maxRecordCount":1000,"capabilities":"Query"}
    v.update(updates)
    return v

class LegacyMetadataGate(unittest.TestCase):
    def test_metadata_only(self):
        def fetcher(params,base=m.SOURCE):
            if base.endswith("/query"):return {"count":500}
            return example_meta()
        q=m.check(fetcher)
        self.assertEqual(q["status"],"PASS_2016_METADATA_AND_COUNT_ONLY")
        self.assertFalse(q["2016_2022_spatial_overlay_computed"])
        self.assertFalse(q["source_polygons_downloaded"])
        self.assertTrue(q["cannot_identify_recovered_historically_vegetated_bottom"])
        self.assertEqual(q["feature_count_whole_legacy_layer"],500)
    def test_wrong_class_stops(self):
        with self.assertRaisesRegex(m.SourceStop,"CLASS_CODE_UNRESOLVED"):
            m.validate_layer(example_meta(fields=[{"name":"OBJECTID","type":"esriFieldTypeOID"}]))
    def test_wrong_geometry_stops(self):
        with self.assertRaisesRegex(m.SourceStop,"NOT_POLYGON"):
            m.validate_layer(example_meta(geometryType="esriGeometryPoint"))
    def test_missing_crs_stops(self):
        with self.assertRaisesRegex(m.SourceStop,"CRS_UNRESOLVED"):
            m.validate_layer(example_meta(extent={"xmin":0,"xmax":1}))
    def test_unavailable_count_stops(self):
        def f(params,base=m.SOURCE):
            if base.endswith("/query"):return {"count":None}
            return example_meta()
        with self.assertRaisesRegex(m.SourceStop,"FEATURE_COUNT_UNRESOLVED"):
            m.check(f)

if __name__=="__main__":unittest.main()
