"""No-network checks for ZEN2 source preflight and missing-as-zero stops."""
from __future__ import annotations
import importlib.util,io,csv,unittest
from pathlib import Path
PATH=Path(__file__).resolve().parents[1]/"analysis"/"126_zen2_structure_consumer_source_preflight.py"
SPEC=importlib.util.spec_from_file_location("zen2preflight",PATH)
M=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(M)

def fake_source(kind="ZEN2_thinning_2015"):
    head=["Site","Patch_location","Shoot_reduction","Status","Tether_no",
          "Calc_shoot_dens","Crust_biomass"] if kind=="ZEN2_thinning_2015" else ["site_code","aboveground_biomass","epifauna"]
    b=io.StringIO();w=csv.DictWriter(b,fieldnames=head);w.writeheader()
    for i in range(36):
        if kind=="ZEN2_thinning_2015":
            row={"Site":"A" if i<18 else "B","Patch_location":"edge" if i%2 else "interior",
                 "Shoot_reduction":("ambient","fifty","eighty")[i%3],"Status":str(i%2),
                 "Tether_no":str(i),"Calc_shoot_dens":str(20+i),
                 "Crust_biomass":str(1+i)}
        else:row={"site_code":"A" if i<18 else "B","aboveground_biomass":str(i),
                 "epifauna":str(i*2)}
        w.writerow(row)
    return b.getvalue().encode()

class TestSourcePreflight(unittest.TestCase):
    def test_2015_treatments_and_status(self):
        j=M.inspect_csv(fake_source(),"ZEN2_thinning_2015")
        self.assertEqual(j["row_count"],36)
        self.assertEqual(j["factor_levels_and_counts"]["Site"]["distinct"],2)
        self.assertEqual(j["factor_levels_and_counts"]["Shoot_reduction"]["distinct"],3)
        self.assertFalse(j["raw_outcome_effect_estimable_in_this_gate"])
    def test_2014_is_separate(self):
        j=M.inspect_csv(fake_source("ZEN2_survey_2014"),"ZEN2_survey_2014")
        self.assertEqual(j["row_count"],36)
        self.assertNotIn("Status",j["schema"])
    def test_missing_treatment_field_fails(self):
        with self.assertRaises(ValueError):
            M.inspect_csv(fake_source("ZEN2_survey_2014"),"ZEN2_thinning_2015")
    def test_short_file_fails(self):
        with self.assertRaises(ValueError):
            M.inspect_csv(b"a,b\n1,2\n","ZEN2_thinning_2015")
if __name__=="__main__":unittest.main()
