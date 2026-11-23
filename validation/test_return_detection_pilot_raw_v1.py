"""No-real-data synthetic QC for optional non-invasive detection pilot."""
from __future__ import annotations
import importlib.util
import unittest
from pathlib import Path

PATH=Path(__file__).resolve().parents[1]/"validation"/"validate_return_detection_pilot_raw_v1.py"
SPEC=importlib.util.spec_from_file_location("optional_detection_raw_qc",PATH)
M=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)

def row(visit="r1",mode="registered_revisit",observer="obs1",photo="img1",
        sampled="1",recorded="1",bb="2",offset="",footprint="frameA",verified="1"):
    return {
        "campaign_id":"synthetic_only","node_id":"syntheticN","water_body":"Old Tampa Bay",
        "mark_id":"m1","visit_id":visit,"visit_local_iso":"2026-11-24T10:00:00-05:00",
        "observer_id":observer,"mode":mode,"footprint_id":footprint,
        "offset_id":offset,"photo_id":photo,"was_sampled":sampled,
        "thalassia_recorded":recorded,"bb_ordinal":bb,
        "mark_identity_verified":verified,"notes":"synthetic test no field observation",
    }

class TestOptionalDetectionPilotQC(unittest.TestCase):
    def test_empty_template_cannot_be_ready(self):
        r=M.validate_rows([])
        self.assertEqual(r["status"],"EMPTY_TEMPLATE_NOT_READY")
        self.assertFalse(r["independence_certified"])

    def test_modes_and_revisits_are_not_conflated(self):
        a=row()
        b=row(visit="r2",observer="obs2",photo="img2",recorded="0",bb="0")
        c=row(visit="r1",mode="blind_photo_recheck",observer="obs3",photo="img1")
        d=row(visit="r1",mode="offset_subquadrat",observer="obs4",photo="img3",
              recorded="0",bb="0",offset="offset_25cm",footprint="frameB")
        e=row(visit="r3",observer="obs5",photo="",sampled="0",
              recorded="",bb="",verified="0")
        x=M.validate_rows([a,b,c,d,e])
        self.assertEqual(x["counts"]["mode_registered_revisit"],2)
        self.assertEqual(x["counts"]["mode_blind_photo_recheck"],1)
        self.assertEqual(x["counts"]["mode_offset_subquadrat"],1)
        self.assertEqual(x["counts"]["unvisited_or_unread"],1)
        self.assertEqual(x["counts"]["verified_registered_footprints_with_two_or_more_distinct_visit_ids"],1)
        self.assertFalse(x["independence_certified"])
        self.assertFalse(x["closure_certified"])

    def test_unvisited_is_not_zero(self):
        x=row(photo="",sampled="0",recorded="0",bb="")
        with self.assertRaises(ValueError):
            M.validate_rows([x])

    def test_duplicate_registered_record_disallowed(self):
        a=row()
        with self.assertRaises(ValueError):
            M.validate_rows([a,a.copy()])

    def test_reusing_a_photo_is_not_an_independent_revisit(self):
        a=row()
        b=row(visit="r2",observer="obs2",photo="img1")
        with self.assertRaises(ValueError):
            M.validate_rows([a,b])

    def test_blind_read_without_photo_disallowed(self):
        x=row(mode="blind_photo_recheck",photo="")
        with self.assertRaises(ValueError):
            M.validate_rows([x])

    def test_offset_without_offset_id_disallowed(self):
        x=row(mode="offset_subquadrat",footprint="frameB",photo="img3")
        with self.assertRaises(ValueError):
            M.validate_rows([x])

    def test_naive_timestamp_disallowed(self):
        x=row()
        x["visit_local_iso"]="2026-11-24T10:00:00"
        with self.assertRaises(ValueError):
            M.validate_rows([x])

    def test_bb_zero_conflicts_with_recorded_presence(self):
        x=row(bb="0",recorded="1")
        with self.assertRaises(ValueError):
            M.validate_rows([x])

if __name__=="__main__":
    unittest.main()
