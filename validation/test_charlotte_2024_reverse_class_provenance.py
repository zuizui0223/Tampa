"""Source-released, deterministic 2024 composition audit; no biological models."""
import importlib.util,copy,json,unittest
from pathlib import Path
root=Path(__file__).resolve().parents[1]
path=root/"analysis/98_charlotte_2024_reverse_class_provenance.py"
spec=importlib.util.spec_from_file_location("rev98",path)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
obj=json.loads((root/"results/charlotte_public_gis_transition_verified_20261119.json").read_text())
class Backwards(unittest.TestCase):
    def test_pinned_real_audit_reproducibility(self):
        r=m.backward(obj)
        self.assertEqual(r["source_verification_run"],44431639618)
        self.assertAlmostEqual(r["2024_attached_algae_of_2022_mapped_seagrass_origin_acres"],280.957,places=3)
        self.assertAlmostEqual(r["2024_attached_algae_outside_2022_mapped_classes_acres"],413.286,places=3)
        self.assertAlmostEqual(r["2024_attached_algae_on_2022_algae_area_acres"],245.158,places=3)
        self.assertAlmostEqual(r["2022_algae_to_2024_seagrass_acres"],83.433,places=3)
        self.assertTrue(r["explicit_no_recovery_effect_inference"])
    def test_changed_archive_identity_rejected(self):
        o=copy.deepcopy(obj);o["verified_workflow"]["artifact_zip_sha256"]="sha256:0"
        with self.assertRaisesRegex(ValueError,"DIGEST_MISMATCH"):
            m.backward(o)
    def test_bad_backward_area_closure_fails(self):
        o=copy.deepcopy(obj);o["result"]["quality_control"]["2024"]["class_area_acres"]["9121"]=100
        with self.assertRaisesRegex(ValueError,"NONCLOSED_TARGET_AREA"):
            m.backward(o)
    def test_causal_claim_rejected(self):
        o=copy.deepcopy(obj);o["result"]["not_a_causal_effect"]=False
        with self.assertRaisesRegex(ValueError,"SCIENTIFIC_BOUNDARY_NOT_ENFORCED"):
            m.backward(o)

if __name__=="__main__":unittest.main()
