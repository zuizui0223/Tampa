"""No-network tests of posthoc broad-ocean label shuffling and latitude rank."""
from __future__ import annotations
import importlib.util,json,unittest
from pathlib import Path

FILE=Path(__file__).resolve().parents[1]/"analysis"/"132_zen2_crossyear_basin_latitude_rank_sensitivity.py"
SP=importlib.util.spec_from_file_location("zen2_basin",FILE)
M=importlib.util.module_from_spec(SP)
SP.loader.exec_module(M)

class BasinTests(unittest.TestCase):
    def source(self):
        return json.loads(M.DATA.read_text()),json.loads(M.GEO.read_text())

    def test_latitude_and_ocean_classification(self):
        self.assertEqual(M.ocean(-120),"Pacific")
        self.assertEqual(M.ocean(145),"Pacific")
        self.assertEqual(M.ocean(-70),"Atlantic_Mediterranean")
        self.assertEqual(M.ocean(20),"Atlantic_Mediterranean")

    def test_rank_ties(self):
        self.assertEqual(M.rank([3,3,1,8]),[2.5,2.5,1,4])
        self.assertAlmostEqual(M.pearson([1,2,3,4],[2,4,6,8]),1.)

    def test_actual_pinned_site_geography_not_duplicated(self):
        source,geo=self.source()
        x=M.analyze(source,geo,perm=1000,seed=42)
        self.assertEqual(x["ocean_category_counts"],{"Pacific":8,"Atlantic_Mediterranean":6})
        self.assertAlmostEqual(x["same_14_sites_original_spearman_r"],.8285714285714286)
        self.assertAlmostEqual(x["partial_spearman_rank_correlation_given_latitude"],.8235278265905026)
        self.assertGreater(x["basin_stratified_2015_label_permutation_two_sided_p"],0)
        self.assertLessEqual(x["basin_stratified_2015_label_permutation_two_sided_p"],1)

    def test_source_identity_hard_stop(self):
        source,geo=self.source()
        geo["source_shas"]["2014"]="false-source"
        with self.assertRaises(ValueError):M.analyze(source,geo,perm=50)

    def test_site_to_geo_not_linked_by_independent_arrays(self):
        source,geo=self.source()
        source["candidate_sites"][0]["site_code"]="UNMATCHED"
        with self.assertRaises(ValueError):M.analyze(source,geo,perm=50)

    def test_same_random_state_reproducible(self):
        source,geo=self.source()
        a=M.analyze(source,geo,perm=350,seed=123)
        b=M.analyze(source,geo,perm=350,seed=123)
        self.assertEqual(a,b)

if __name__=="__main__":
    unittest.main()
