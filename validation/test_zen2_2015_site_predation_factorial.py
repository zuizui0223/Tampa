"""Zero-network tests for 2015 ZEN2 six-cell site-level predation analysis."""
from __future__ import annotations
import importlib.util,unittest,io,csv
from pathlib import Path
FILE=Path(__file__).resolve().parents[1]/"analysis"/"127_zen2_2015_site_predation_factorial.py"
SPEC=importlib.util.spec_from_file_location("zen2experiment",FILE)
M=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(M)

def fake_rows():
    records=[]
    for i,site in enumerate(("AA","BB","CC","DD","EE")):
        for loc in M.LOCATIONS:
            for treatment in M.TREATMENTS:
                for j in range(6):
                    eaten=int(j<(1+(loc=="Interior")+(treatment=="Eighty")))
                    records.append({
                        "site":site,"location":loc,"treatment":treatment,
                        "recorded_eaten":eaten,"taxon":"Amphipod",
                        "density_initial":100.,"density_actual":100 if treatment=="Amb" else 50,
                        "epibiont":2.,"crust_biomass":1.,"tether":f"{site}|{loc}|{treatment}|{j}"
                    })
    return records

class TestZEN2Experimental(unittest.TestCase):
    def test_exact_factorial_risk_contrasts(self):
        x=M.analyze(fake_rows())
        self.assertEqual(x["site_count"],5)
        self.assertEqual(x["tethered_prey_count"],180)
        self.assertAlmostEqual(x["site_equal_contrasts"]["edge_minus_interior_risk"]["mean_site_equal"],-1/6)
        self.assertAlmostEqual(x["site_equal_contrasts"]["eighty_minus_ambient_risk"]["mean_site_equal"],1/6)
        self.assertAlmostEqual(x["site_equal_contrasts"]["edge_by_eighty_thinning_difference_in_differences"]["mean_site_equal"],0)
        self.assertEqual(x["site_equal_contrasts"]["edge_minus_interior_risk"]["sites"],5)

    def test_missing_site_cell_fails_closed(self):
        x=[z for z in fake_rows() if not (z["site"]=="AA" and z["location"]=="Edge" and z["treatment"]=="Amb")]
        with self.assertRaises(ValueError):M.analyze(x)

    def test_fewer_than_five_per_cell_fails_closed(self):
        x=[z for z in fake_rows() if not (z["site"]=="AA" and z["location"]=="Edge" and z["treatment"]=="Amb" and z["tether"].endswith("|5"))]
        # Removing only one of 6 leaves 5; remove another.
        x=[z for z in x if not (z["site"]=="AA" and z["location"]=="Edge" and z["treatment"]=="Amb" and z["tether"].endswith("|4"))]
        with self.assertRaises(ValueError):M.analyze(x)

    def test_original_source_digest_rejects_synthetic(self):
        b=io.StringIO();w=csv.DictWriter(b,fieldnames=M.TARGET_COLUMNS);w.writeheader()
        for z in fake_rows():
            w.writerow({"Site":z["site"],"Taxon":"Amphipod","Basin":"P","Latitude":"38",
                        "Longitude":"-123","Patch_location":z["location"],
                        "Shoot_reduction":z["treatment"],"Tether_no":z["tether"],
                        "Size_mm":"10","Crust_biomass":"1","Other_biomass":"1",
                        "Total_biomass":"2","Epiphyte_biomass":"1",
                        "Starting_shoot_dens":"100","Calc_shoot_dens":"100",
                        "Status":str(z["recorded_eaten"])})
        with self.assertRaises(ValueError):M.parse_rows(b.getvalue().encode(),verify_digest=True)
        parsed=M.parse_rows(b.getvalue().encode(),verify_digest=False)
        self.assertEqual(len(parsed),180)

    def test_invalid_event_is_not_implicitly_mortality(self):
        b=io.StringIO();w=csv.DictWriter(b,fieldnames=M.TARGET_COLUMNS);w.writeheader()
        w.writerow({"Site":"A","Taxon":"Amphipod","Patch_location":"Edge","Shoot_reduction":"Amb","Status":"missing"})
        with self.assertRaises(ValueError):M.parse_rows(b.getvalue().encode(),verify_digest=False)

if __name__=="__main__":unittest.main()
