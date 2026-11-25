"""Synthetic tests for ZEN 15-site experimental site-equal contrasts."""
from __future__ import annotations
import importlib.util
import io
import csv
import math
import unittest
from pathlib import Path
PATH=Path(__file__).resolve().parents[1]/"analysis"/"118_zen_15site_mesograzer_factorial.py"
SPEC=importlib.util.spec_from_file_location("zen15",PATH)
M=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)

def fake_csv(sites=("A","B"),n=5,missing=None):
    head=["site_code","plot","unique_plot_id","treatment","chla_per_Zostera",
          "grazer_bmass_per_g","grazer_richness_site","temp_avg","sal"]
    buf=io.StringIO();w=csv.DictWriter(buf,fieldnames=head)
    w.writeheader()
    for site in sites:
        for t in M.TREATMENTS:
            d=int("D+" in t);nut=int("N+" in t)
            for j in range(n):
                value=(2+2*d+nut)
                v="" if missing==(site,t) else str(value)
                w.writerow(dict(site_code=site,plot=str(j),unique_plot_id=f"{site}|{t}|{j}",
                                treatment=t,chla_per_Zostera=v,
                                grazer_bmass_per_g=str(3-2*d),
                                grazer_richness_site="5",
                                temp_avg="-1",sal="31"))
    return buf.getvalue().encode()

class ZENAnalysisTests(unittest.TestCase):
    def test_factorial_contrasts_exact(self):
        r=M.analysis(M.parse_core(fake_csv()))
        a=r["per_site_exploratory_contrasts"][0]["endpoints"]["chla_per_Zostera"]["contrasts"]
        self.assertAlmostEqual(a["grazer_deterrent_main_difference"],2)
        self.assertAlmostEqual(a["nutrient_addition_main_difference"],1)
        self.assertAlmostEqual(a["grazer_deterrent_x_nutrient_difference_in_differences"],0)

    def test_posthoc_scale_invariant_same_site_ratio(self):
        r=M.analysis(M.parse_core(fake_csv()))
        x=r["per_site_exploratory_contrasts"][0]["endpoints"]["chla_per_Zostera"]["posthoc_log_arm_mean_contrasts"]
        self.assertAlmostEqual(
            x["grazer_deterrent_main_difference"],
            (math.log(5/3)+math.log(4/2))/2
        )
        self.assertAlmostEqual(
            x["grazer_deterrent_x_nutrient_difference_in_differences"],
            math.log(5/3)-math.log(4/2)
        )

    def test_grazer_reduction_manipulation_sign(self):
        r=M.analysis(M.parse_core(fake_csv()))
        a=r["per_site_exploratory_contrasts"][0]["endpoints"]["grazer_bmass_per_g"]["contrasts"]
        self.assertAlmostEqual(a["grazer_deterrent_main_difference"],-2)

    def test_missing_is_not_zero_and_cannot_create_fully_estimable_cell(self):
        r=M.analysis(M.parse_core(fake_csv(missing=("A","D+N+"))))
        a=r["per_site_exploratory_contrasts"][0]["endpoints"]["chla_per_Zostera"]
        self.assertFalse(a["eligible_for_four_arm_contrast"])
        self.assertEqual(a["n_valid_per_arm"]["D+N+"],0)
        self.assertEqual(r["endpoints"]["chla_per_Zostera"]["sites_eligible"],1)

    def test_reject_duplicate_experimental_plot(self):
        x=M.parse_core(fake_csv())
        # duplicate UID across two sites must reject
        b=fake_csv().decode().splitlines()
        second=b[1].split(",")[2]
        last=b[-1].split(",");last[2]=second;b[-1]=",".join(last)
        with self.assertRaises(ValueError):
            M.parse_core(("\n".join(b)+"\n").encode())

    def test_temp_can_be_below_zero_but_biomass_cannot(self):
        x=M.parse_core(fake_csv())
        self.assertEqual(x["A"][0]["temp_avg"],-1.0)
        with self.assertRaises(ValueError):
            M.numeric("-0.1")

    def test_bootstrap_site_mean_not_rows(self):
        x=M.cluster_bootstrapped_mean([1,2,3,4,5])
        self.assertTrue(x["estimable"])
        self.assertEqual(x["sites"],5)
        self.assertAlmostEqual(x["mean_site_equal"],3)
        self.assertEqual(x["site_bootstrap_95pct_percentile_ci"],
                         M.cluster_bootstrapped_mean([1,2,3,4,5])["site_bootstrap_95pct_percentile_ci"])

    def test_requires_complete_treatment_assignment(self):
        b=fake_csv().decode().splitlines()
        b=[line for line in b if not (line.startswith("A,") and ",D+N+," in line)]
        with self.assertRaises(ValueError):
            M.by_site(M.parse_core(("\n".join(b)+"\n").encode()))

    def test_no_fake_original_sha(self):
        with self.assertRaises(ValueError):
            M.parse(fake_csv())

if __name__=="__main__":unittest.main()
