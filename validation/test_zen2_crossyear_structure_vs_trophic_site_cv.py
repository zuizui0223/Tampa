"""No-network synthetic tests for 2014 prior-state -> 2015 leave-site-out CV."""
from __future__ import annotations
import importlib.util,json,math,unittest
from pathlib import Path

PATH=Path(__file__).resolve().parents[1]/"analysis"/"133_zen2_crossyear_structure_vs_trophic_site_cv.py"
SPEC=importlib.util.spec_from_file_location("zen2_site_cv",PATH)
M=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)

def fake_sites(n=14,constant=False):
    rows=[]
    for i in range(n):
        prev=5.0 if constant else 2+i
        nextyear=math.expm1(1+.8*math.log1p(prev))
        rows.append({
            "site_code":f"S{i:02d}",
            "year2014_shoot_density":prev,
            "year2014_epiphyton":float((i*3)%7)+1,
            "year2015_ambient_shoot_density":nextyear,
            "year2015_edge_minus_interior_risk":(i%3-.5)/8,
            "year2015_eighty_minus_ambient_risk":(i%4-1.5)/20,
            "nearest_distance_km":.5 if i>0 else 6.
        })
    return rows

class SiteCrossValidationTests(unittest.TestCase):
    def test_perfect_linear_on_log_scale_forecasts_structure(self):
        model=M.cv(fake_sites(),"year2014_shoot_density",
            "year2015_ambient_shoot_density","log1p_response")
        self.assertEqual(model["n_site_codes"],14)
        self.assertAlmostEqual(model["site_equal_cv_r2_against_fold_training_mean"],1,places=9)
        self.assertAlmostEqual(model["prior_state_model_rmse"],0,places=9)

    def test_constant_predictor_does_not_fake_skill(self):
        model=M.cv(fake_sites(constant=True),
            "year2014_shoot_density","year2015_edge_minus_interior_risk",
            "risk_difference")
        self.assertAlmostEqual(model["site_equal_cv_r2_against_fold_training_mean"],0,places=10)
        self.assertTrue(all(z["training_slope"]==0 for z in model["held_out_site_predictions"]))

    def test_model_uses_training_n_minus_one_only(self):
        x=[1,2,3,4,5,6]
        y=[2,4,6,8,10,1234]
        fit=M.fit_ols(x[:-1],y[:-1])
        self.assertAlmostEqual(fit["slope"],2)
        self.assertAlmostEqual(fit["intercept"],0)

    def test_missingness_drops_only_that_endpoint_case(self):
        rows=fake_sites()
        rows[0]["year2014_epiphyton"]=None
        model=M.cv(rows,"year2014_epiphyton",
            "year2015_edge_minus_interior_risk","risk_difference")
        self.assertEqual(model["n_site_codes"],13)
        self.assertNotIn("S00",model["site_codes"])

    def test_bad_coordinates_or_duplicated_site_units_do_not_score(self):
        rows=fake_sites()
        rows[0]["site_code"]=rows[1]["site_code"]
        with self.assertRaises(ValueError):M.cv(rows,
            "year2014_shoot_density","year2015_ambient_shoot_density","log1p_response")
        with self.assertRaises(ValueError):M.cv(fake_sites(5),
            "year2014_shoot_density","year2015_ambient_shoot_density","log1p_response")

    def test_original_frozen_14_site_source_contract_and_stricter_13(self):
        source=json.loads(M.SOURCE.read_text())
        result=M.report(source)
        self.assertEqual(result["original_geographic_cohort_site_count"],14)
        self.assertEqual(len(result["original_14_site_models"]),5)
        self.assertEqual(len(result["stricter_5km_sensitivity"]),2)
        self.assertEqual(result["stricter_5km_sensitivity"][0]["n_site_codes"],13)
        self.assertTrue(all(x["n_site_codes"]==14 for x in result["original_14_site_models"]))

    def test_wrong_frozen_source_fails_closed(self):
        source=json.loads(M.SOURCE.read_text())
        source["schema"]="invalid"
        with self.assertRaises(ValueError):M.report(source)

if __name__=="__main__":
    unittest.main()
