#!/usr/bin/env python3
"""RED-before-fix: recorded next-year zero needs a real sampled point-event.

Synthetic only. Future sampled-event records must be independent of the
model-ready seven-column BB/TNC input and carry true point event provenance.
"""
import copy
import importlib.util
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path)
    assert spec and spec.loader
    m=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

source=load("lineage",Path("analysis/85_tnc_anchor_lineage.py"))
fixtures=load("prior_lineage_tests",Path("validation/test_tnc_anchor_lineage.py")).fixtures

def sampled_ledger(future):
    rows=[]
    for i,r in enumerate(future):
        bb=str(r["future_bb_anchor"])
        present=bb!="0"
        rows.append({
            "node_id":r["node_id"],
            "water_body":r["water_body"],
            "point_location_id":r["point_location_id"],
            "future_survey_date":r["future_survey_date"],
            "point_event_id":f"TBEP:synthetic:future:point-event:{i}",
            "thalassia_present":"true" if present else "false",
            "raw_thalassia_bb":bb if present else ""
        })
    return rows

class SampledPointEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.c,self.a,self.t,self.f,self.ledger=copy.deepcopy(fixtures())

    def test_frozen_future_zero_is_real_sampled_non_detection(self):
        result=source.build(self.c,self.a,self.t,self.f,self.ledger)
        self.assertEqual(result["status"],"PASS_LINEAGE_FOR_FROZEN_PRIMARY_INPUT")
        self.assertEqual(result["complete_nodes"],36)
        self.assertEqual(result["primary_input_rows"][0]["future_bb_anchor"],0.0)

    def test_recorded_zero_without_sampled_point_event_is_not_loss(self):
        ledger=[x for x in self.ledger if x["point_location_id"]!=self.f[0]["point_location_id"]]
        result=source.build(self.c,self.a,self.t,self.f,ledger)
        self.assertEqual(result["status"],"STOP_COMPLETE_TRIPLET_GATE")
        self.assertEqual(result["complete_nodes"],35)
        self.assertTrue(any(self.f[0]["node_id"]==x["node_id"] for x in result["excluded_nodes"]))

    def test_declared_zero_but_raw_occurrence_positive_must_fail(self):
        self.ledger[0]["thalassia_present"]="true"
        self.ledger[0]["raw_thalassia_bb"]="2"
        with self.assertRaises(ValueError):
            source.build(self.c,self.a,self.t,self.f,self.ledger)

    def test_nonnumeric_present_does_not_become_absence(self):
        self.ledger[0]["thalassia_present"]="true"
        self.ledger[0]["raw_thalassia_bb"]="Reported"
        self.f[0]["future_bb_anchor"]="Reported"
        result=source.build(self.c,self.a,self.t,self.f,self.ledger)
        self.assertEqual(result["status"],"STOP_COMPLETE_TRIPLET_GATE")
        self.assertEqual(result["complete_nodes"],35)

    def test_duplicate_point_event_id_must_fail(self):
        self.ledger[1]["point_event_id"]=self.ledger[0]["point_event_id"]
        with self.assertRaises(ValueError):
            source.build(self.c,self.a,self.t,self.f,self.ledger)

    def test_positive_raw_bb_and_entered_future_bb_disagreement_must_fail(self):
        self.f[1]["future_bb_anchor"]="4"
        with self.assertRaises(ValueError):
            source.build(self.c,self.a,self.t,self.f,self.ledger)

    def test_source_future_point_id_date_wrong_cannot_pass(self):
        self.ledger[0]["future_survey_date"]="2029-09-01"
        with self.assertRaises(ValueError):
            source.build(self.c,self.a,self.t,self.f,self.ledger)

if __name__=="__main__":
    unittest.main()
