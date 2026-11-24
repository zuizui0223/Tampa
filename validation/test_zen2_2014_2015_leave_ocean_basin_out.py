"""No-network, inspectable tests of ZEN2 leave-entire-ocean-basin-out transport."""
from __future__ import annotations
import importlib.util,json,math,statistics,unittest
from pathlib import Path

PATH=Path(__file__).resolve().parents[1]/"analysis"/"134_zen2_2014_2015_leave_ocean_basin_out.py"
SPEC=importlib.util.spec_from_file_location("zen2_lobo",PATH)
M=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)

class OceanOutTests(unittest.TestCase):
    def fixture(self):
        return json.loads(M.FILE2014.read_text()),json.loads(M.FILEGEO.read_text())

    def test_exact_original_cohorts_and_all_endpoints(self):
        r=M.report()
        self.assertEqual(r["schema"],"tampa.zen2_cross_basin_transport_pair_v1")
        self.assertEqual(r["all_25km"]["site_count"],14)
        self.assertEqual(r["strict_5km"]["site_count"],13)
        self.assertEqual(r["all_25km"]["basin_site_counts"],{"Pacific":8,"Atlantic_Mediterranean":6})
        self.assertEqual(r["strict_5km"]["basin_site_counts"],{"Pacific":7,"Atlantic_Mediterranean":6})
        for scenario in ["all_25km","strict_5km"]:
            self.assertEqual(len(r[scenario]["models"]),3)
            for model in r[scenario]["models"]:
                self.assertEqual(model["n_test_sites_combined"],r[scenario]["site_count"])
                self.assertEqual(len(model["two_held_out_basin_evaluations"]),2)
                self.assertTrue(all(t["n_test_site_codes"]+t["n_train_site_codes"]==r[scenario]["site_count"]
                                    for t in model["two_held_out_basin_evaluations"]))

    def test_original_source_14_site_cvbounds(self):
        r=M.report()["all_25km"]
        by={m["subsequent_target"]:m for m in r["models"]}
        self.assertAlmostEqual(by["year2015_ambient_shoot_density"]["leave_one_basin_out_r2_against_training_basin_mean"],.5661401926838103)
        self.assertAlmostEqual(by["year2015_eighty_minus_ambient_risk"]["leave_one_basin_out_r2_against_training_basin_mean"],-.32589689408003597)

    def test_training_mean_does_not_use_heldout_basin(self):
        r=M.report()["all_25km"]["models"][0]
        raw,_=self.fixture()
        pac=[x for x in r["two_held_out_basin_evaluations"] if x["held_out_basin"]=="Pacific"][0]
        original_sites={x["site_code"]:x for x in raw["candidate_sites"]}
        atl_codes=[x["site"] for x in r["two_held_out_basin_evaluations"][1]["site_level_predictions"]]
        baseline=statistics.mean(math.log1p(original_sites[s]["year2015_ambient_shoot_density"]) for s in atl_codes)
        self.assertAlmostEqual(pac["site_level_predictions"][0]["reference_prediction"],baseline)

    def test_original_source_provenance_guard(self):
        data,geo=self.fixture()
        geo["source_shas"]["2015"]="bad"
        with self.assertRaises(ValueError):M.execute(data,geo)

    def test_distance_threshold_hard_stop(self):
        data,geo=self.fixture()
        with self.assertRaises(ValueError):M.execute(data,geo,restrict_km=35)

    def test_not_pseudo_replicating_basin_group(self):
        x=M.report()
        self.assertTrue(x["source_outcomes_already_opened"])
        self.assertTrue(all("posthoc" in x[s]["evidence_class"] for s in ("all_25km","strict_5km")))
        self.assertEqual(len(x["all_25km"]["models"][0]["two_held_out_basin_evaluations"][0]["site_level_predictions"]),8)

if __name__=="__main__":
    unittest.main()
