"""Synthetic authorized ZIP shapefile intake; no user registration or real field inference."""
import importlib.util,io,os,tempfile,unittest,zipfile,json
from pathlib import Path
import shapefile
SRC=Path(__file__).resolve().parents[1]/"analysis/119_swfmd_original_seagrass_zip_intake_gate.py"
SPEC=importlib.util.spec_from_file_location("ch119",SRC)
M=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(M)

def make_zip(where,codes=(9113,9116,9121),archive_name="swfwmd_2024.zip",complete=True):
    target=Path(where)/archive_name
    shp,shx,dbf=io.BytesIO(),io.BytesIO(),io.BytesIO()
    w=shapefile.Writer(shp=shp,shx=shx,dbf=dbf,shapeType=shapefile.POLYGON)
    w.field("FLUCCSCODE","N",size=8,decimal=0)
    w.field("ACRES","F",size=12,decimal=3)
    for i,code in enumerate(codes):
        a=i*10
        w.poly([[[a,a],[a,a+2],[a+2,a+2],[a+2,a],[a,a]]])
        w.record(int(code),1.)
    w.close()
    with zipfile.ZipFile(target,"w",compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr("SWFWMD_2024/data.shp",shp.getvalue())
        z.writestr("SWFWMD_2024/data.shx",shx.getvalue())
        z.writestr("SWFWMD_2024/data.dbf",dbf.getvalue())
        if complete:z.writestr("SWFWMD_2024/data.prj","PROJCS[\"WGS 84 / UTM zone 17N\"]")
    return target

class SourceZIPGate(unittest.TestCase):
    def test_three_class_zip_does_not_claim_complete_habitat_source(self):
        with tempfile.TemporaryDirectory() as t:
            p=make_zip(t)
            report=M.inspect_zip(p)
            self.assertEqual(report["status"],"PASS_LOCAL_ARCHIVE_CLASS_DICTIONARY_INTAKE_ONLY")
            self.assertEqual(report["all_observed_class_codes"],["9113","9116","9121"])
            self.assertTrue(report["only_restricted_three_categories_seen_in_classified_files"])
            self.assertFalse(report["all_benthic_classes_and_photo_footprint_confirmed_complete"])
            self.assertFalse(report["other_benthic_classes_observed"])
            self.assertEqual(report["shapefile_group_registry"][0]["n_records"],3)
            self.assertEqual(report["shapefile_group_registry"][0]["original_area_field_candidates"],["ACRES"])

    def test_extra_background_code_detected_but_coverage_still_unproven(self):
        with tempfile.TemporaryDirectory() as t:
            p=make_zip(t,codes=(9113,9116,9121,5400))
            r=M.inspect_zip(p)
            self.assertIn("5400",r["all_observed_class_codes"])
            self.assertEqual(r["shapefile_group_registry"][0]["non_three_class_records"],1)
            self.assertFalse(r["all_benthic_classes_and_photo_footprint_confirmed_complete"])

    def test_missing_shapefile_component_fails_closed(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/"incomplete.zip"
            with zipfile.ZipFile(p,"w") as z:
                z.writestr("sample.shp",b"not a complete vector")
                z.writestr("sample.dbf",b"not a complete table")
            with self.assertRaisesRegex(M.Stop,"MISSING_SHAPEFILE_TRIPLET"):
                M.inspect_zip(p)

    def test_zip_parent_path_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/"path_traversal.zip"
            with zipfile.ZipFile(p,"w") as z:z.writestr("../source.shp",b"some fake bytes")
            with self.assertRaisesRegex(M.Stop,"UNSAFE_ZIP_MEMBER_PATH"):
                M.inspect_zip(p)

    def test_zipped_geodatabase_without_shapefile_explicit_stop(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/"original.zip"
            with zipfile.ZipFile(p,"w") as z:z.writestr("source.gdb/a00000001.gdbtable",b"not a shapefile")
            r=M.inspect_zip(p)
            self.assertEqual(r["status"],"STOP_NO_SHAPEFILE_GROUPS_OR_GDB_ONLY")
            self.assertTrue(r["contains_gdb_paths"])

if __name__=="__main__":unittest.main()
