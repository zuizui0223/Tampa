"""No-network synthetic diagnostics for global paired seagrass allocation."""
from __future__ import annotations
import importlib.util
import math
import unittest
from pathlib import Path

PATH=Path(__file__).resolve().parents[1]/"analysis"/"115_global_seagrass_allocation_conditional_spread.py"
SPEC=importlib.util.spec_from_file_location("global_allocation",PATH)
M=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)

KEYS={"ref":"Reference","genus":"Genus","region":"Region","habitat":"Habitat",
      "ag":"Above","bg":"Below"}


def make_rows():
    # Two distinct original reference strings; within-study rows are not
    # independent publications. Observed zero and blank are not positive biomass.
    a=[
        {"Reference":"S1 2005","Genus":"Zostera","Region":"Temperate",
         "Habitat":"Estuarine","Above":str(x),"Below":str(y)}
        for x,y in [(10,20),(20,40),(30,120),(40,20),(50,25)]
    ]
    b=[
        {"Reference":"S2 2007","Genus":"Zostera","Region":"Temperate",
         "Habitat":"Estuarine","Above":str(x),"Below":str(y)}
        for x,y in [(15,3),(25,15),(35,70),(45,30),(55,110)]
    ]
    x=a+b
    x.append(dict(Reference="S2 2007",Genus="Zostera",Region="Temperate",
                  Habitat="Estuarine",Above="0",Below="30"))
    x.append(dict(Reference="S2 2007",Genus="Zostera",Region="Temperate",
                  Habitat="Estuarine",Above="10",Below=""))
    return x


class TestGlobalAllocation(unittest.TestCase):
    def test_strict_same_row_pair_and_missingness(self):
        records,exclusions=M.records_from_source(make_rows(),KEYS)
        self.assertEqual(len(records),10)
        self.assertEqual(len({x["ref"] for x in records}),2)
        self.assertEqual(exclusions["missing_or_nonpositive_above"],1)
        self.assertEqual(exclusions["missing_or_nonpositive_below"],1)
        self.assertAlmostEqual(records[0]["ratio"],2.0)

    def test_same_row_allocation_does_not_join_blank_measure(self):
        rows=make_rows()
        rows[0]["Below"]=""
        records,_=M.records_from_source(rows,KEYS)
        self.assertEqual(len(records),9)

    def test_group_requires_independent_raw_ref_strings_for_descriptive_report(self):
        rs,ex=M.records_from_source(make_rows(),KEYS)
        grouped=M.grouped_summary(rs,"genus",min_rows=10,min_refs=3)
        self.assertEqual(grouped[0]["paired_observation_rows"],10)
        self.assertEqual(grouped[0]["raw_reference_string_clusters_not_verified_unique_papers"],2)
        self.assertFalse(grouped[0]["supported_descriptive_coverage_gate"])
        self.assertIsNone(grouped[0]["median_reference_equal_below_above_ratio"])

    def test_reference_equal_calculation_is_not_row_weighted_median(self):
        rs,_=M.records_from_source(make_rows(),KEYS)
        out=M.grouped_summary(rs,"genus",min_rows=10,min_refs=2)[0]
        expected=math.exp(M.statistics.median([
            M.statistics.median([r["log_ratio"] for r in rs if r["ref"]=="S1 2005"]),
            M.statistics.median([r["log_ratio"] for r in rs if r["ref"]=="S2 2007"])
        ]))
        self.assertAlmostEqual(out["median_reference_equal_below_above_ratio"],expected)

    def test_historical_central_bin_does_not_claim_mechanism_with_two_refs(self):
        rs,_=M.records_from_source(make_rows(),KEYS)
        out=M.reference_central_aboveground_spread(rs)[0]
        self.assertFalse(out["coverage_gate"])
        self.assertIsNone(out["central_band_bg_q75_to_q25"])
        self.assertEqual(out["central_band_raw_reference_strings"],2)

    def test_nonpositive_below_does_not_turn_into_biomass(self):
        d=make_rows()
        d[0]["Below"]="-1"
        rs,ex=M.records_from_source(d,KEYS)
        self.assertEqual(len(rs),9)
        self.assertEqual(ex["missing_or_nonpositive_below"],2)


if __name__=="__main__":
    unittest.main()
