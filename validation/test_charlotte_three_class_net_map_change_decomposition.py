"""Source-verified map-class area conservation; no biological or causal effect."""
import copy,importlib.util,unittest
from pathlib import Path
SRC=Path(__file__).resolve().parents[1]/"analysis/117_charlotte_three_class_net_map_change_decomposition.py"
spec=importlib.util.spec_from_file_location("ch117",SRC)
M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)

class ClassAreaConservation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.o,cls.change=M.inputs()
    def test_frozen_source_reproduces_map_net_area_exactly(self):
        r=M.compute(self.o,self.change)
        self.assertEqual(r["status"],"SUCCESS_VERIFIED_TWO_SOURCE_GIS_AREA_MASS_BALANCE_NOT_CAUSAL")
        a=r["mapped_area_acres"]
        self.assertAlmostEqual(a["seagrass_net_change"],-816.474,places=3)
        self.assertAlmostEqual(a["attached_algae_net_change"],265.213,places=3)
        self.assertAlmostEqual(a["three_class_net_change"],-551.261,places=3)
        self.assertAlmostEqual(r["cross_class_mapped_area_acres"]["net_seagrass_from_class_reclassification"],-197.524,places=3)
        self.assertAlmostEqual(r["source_map_coverage_change_acres"]["mapped_seagrass_net_coverage_component"],-618.95,places=3)
        self.assertTrue(r["not_true_establishment_mortality_or_algae_inhibition"])
        self.assertTrue(r["code_9121_in_nominal_seagrass_change_layers_is_attached_macroalgae"])
        self.assertTrue(all(abs(x)<.025 for x in r["mass_balance_residual_acres"].values()))
    def test_modified_agency_algae_gain_area_is_detected(self):
        changed=copy.deepcopy(self.change)
        changed["report"]["official_gain_loss_sources"]["gain"]["mapped_class_areas_acres"]["9121"]+=1
        with self.assertRaisesRegex(M.Stop,"AGENCY_GAIN_LOSS_AREA_INCONSISTENT"):
            M.compute(self.o,changed)
    def test_nominal_gain_layer_cannot_be_relabelled_all_seagrass(self):
        changed=copy.deepcopy(self.change)
        changed["report"]["official_gain_loss_sources"]["gain"]["flucss_class_counts"]["9121"]=0
        with self.assertRaisesRegex(M.Stop,"OFFICIAL_CHANGE_CLASS_COUNT_LEDGER_DRIFT"):
            M.compute(self.o,changed)
    def test_two_year_transition_matrix_missing_2024_class_fails(self):
        changed=copy.deepcopy(self.o)
        del changed["result"]["source_area_to_target_class"]["9113"]["target_area_acres"]["9121"]
        with self.assertRaises(KeyError):
            M.compute(changed,self.change)
    def test_source_identities_pinned_to_actual_successful_runs(self):
        self.assertEqual(self.o["verified_workflow"]["run_id"],44431639618)
        self.assertEqual(self.change["verified_ci"]["run_id"],44478539061)
    def test_2022_source_class_differences_keep_seagrass_patchy_and_continuous_merged(self):
        r=M.compute(self.o,self.change)
        c=r["cross_class_mapped_area_acres"]
        self.assertAlmostEqual(c["2022_seagrass_to_2024_attached_algae"],280.957,places=3)
        self.assertAlmostEqual(c["2022_attached_algae_to_2024_seagrass"],83.433,places=3)
        self.assertAlmostEqual(c["net_attached_algae_from_class_reclassification"],197.524,places=3)
if __name__=="__main__":unittest.main()
