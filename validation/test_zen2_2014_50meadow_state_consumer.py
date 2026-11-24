"""Synthetic pair-grain safeguards for ZEN2 2014 source.
No-source network required.
"""
from __future__ import annotations
import importlib.util,io,csv,math,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/"analysis"/"128_zen2_2014_50meadow_state_consumer.py"
S=importlib.util.spec_from_file_location("zen2pair",P);M=importlib.util.module_from_spec(S);S.loader.exec_module(M)

def fake_sites():
    rows=[]
    for i in range(25):
        for letter,offset in (("A",0),("B",1)):
            rows.append({"region_code":f"S{i:02d}","subsite_id":f"S{i:02d}.{letter}","subsite":letter,
                         "above":10+i+offset*2,"below":30+i*2+offset,
                         "shoots":100+i*5+offset*10,
                         "mesograzer_abundance":2+i+.1*offset,
                         "mesograzer_count_unstandardized":20+i+3*offset,
                         "mesograzer_richness":3+i%5,
                         "epiphyton":1+i/10+offset*.5,
                         "temperature":10+i*.3,
                         "salinity":27+i/10})
    return rows

class Tests(unittest.TestCase):
    def test_site_code_pairs_no_subsite_double_count(self):
        x=M.summarize(fake_sites())
        self.assertEqual(x["sample_subsites"],50)
        self.assertEqual(x["paired_region_codes"],25)
        for v in x["within_region_association_tests_descriptive"].values():
            self.assertEqual(v["pairs"],25)
    def test_single_subsite_is_not_two_independent_sites(self):
        rows=fake_sites()
        rows.pop()
        with self.assertRaises(ValueError):M.summarize(rows)
    def test_missing_biological_measure_is_not_zero(self):
        rows=fake_sites()
        rows[0]["epiphyton"]=None
        x=M.summarize(rows)
        self.assertEqual(x["measured_missing_subsite_counts"]["epiphyton"],1)
        self.assertEqual(x["within_region_association_tests_descriptive"]["above__epiphyton"]["pairs"],24)
    def test_wrong_digest_rejects_synthetic(self):
        with self.assertRaises(ValueError):
            M.parse(b"Site_Code,Site\nS1,S1.A\n")
    def test_negative_measured_biomass_is_invalid(self):
        self.assertTrue(math.isclose(M.corr([0,1,2,3,4,5],[0,1,2,3,4,5]),1.))
if __name__=="__main__":unittest.main()
