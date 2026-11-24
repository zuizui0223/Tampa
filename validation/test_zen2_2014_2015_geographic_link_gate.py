"""Synthetic geographic-only cohort linkage and permanent-plot limitation checks."""
from __future__ import annotations
import importlib.util
import unittest
from pathlib import Path

MOD=Path(__file__).resolve().parents[1]/"analysis"/"130_zen2_2014_2015_geographic_link_gate.py"
SPEC=importlib.util.spec_from_file_location("link_zen2_geography",MOD)
M=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)

OLD_CODES=["BB","BC","CR","ES","FI","FR","IR","JN","JS","KO","LI","MA","MX",
           "NC","NN","OR","PO","QU","RU","SD","SF","SW","UK","VA","WA"]
NEW_CODES=["BB","CR","FI","FR","GA","JN","JS","KOA","KOB","MX","NC","OR",
           "QU","SD","SF","VA","WA"]
def fixture():
    old=[]
    coordinates={}
    for i,code in enumerate(OLD_CODES):
        lat=30+i/10;lon=-120+i/10
        coordinates[code]=(lat,lon)
        for sub in ("A","B"):
            old.append({"code":code,"id":code+"."+sub,
                        "name":"Synthetic only","lat":lat,
                        "lon":lon+(0.005 if sub=="B" else 0)})
    new=[]
    for code in NEW_CODES:
        lookup=M.AMBIGUOUS_CODE_FAMILIES.get(code,code)
        la,lo=coordinates.get(lookup,(10.,10.))
        new.append({"code":code,"id":code,"name":"","lat":la,"lon":lo})
    return old,new

class GeographicLinkageTests(unittest.TestCase):
    def test_same_code_not_enough_if_2015_coordinate_far(self):
        old,new=fixture()
        for x in new:
            if x["code"]=="VA":x["lat"]=53.
        j=M.audit(old,new)
        self.assertNotIn("VA",j["eligible_site_codes"])
        va=next(x for x in j["candidates"] if x["source_2015_site"]=="VA")
        self.assertGreater(va["closest_distance_km"],25)

    def test_ambiguous_KO_is_excluded_even_with_exact_coordinate(self):
        j=M.audit(*fixture())
        self.assertNotIn("KOA",j["eligible_site_codes"])
        self.assertNotIn("KOB",j["eligible_site_codes"])
        self.assertTrue(all(x["code_mapping_ambiguous"] for x in j["candidates"]
                            if x["source_2015_site"].startswith("KO")))
        self.assertEqual(len(j["candidates"]),17)

    def test_nonoverlap_GA_not_included_and_thirteen_exact(self):
        j=M.audit(*fixture())
        self.assertEqual(len(j["eligible_site_codes"]),14)
        self.assertNotIn("GA",j["eligible_site_codes"])
        self.assertEqual(j["source_2014_subsites"],50)

    def test_position_checks_fail_closed(self):
        self.assertAlmostEqual(M.haversine((0.,0.),(0.,0.)),0)
        with self.assertRaises(ValueError):
            M.haversine((91,0),(0,0))
        old,new=fixture()
        new.append(new[0].copy())
        with self.assertRaises(ValueError):M.audit(old,new)

    def test_one_site_two_positions_need_manual_review(self):
        old,new=fixture()
        new.append({"code":"BB","id":"BB","name":"","lat":19,"lon":40})
        with self.assertRaises(ValueError):M.audit(old,new)

if __name__=="__main__":
    unittest.main()
