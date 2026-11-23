"""Synthetic source-metadata-only audit, no biological observation values."""
from __future__ import annotations
import csv
import importlib.util
import io
import unittest
from pathlib import Path

PATH=Path(__file__).resolve().parents[1]/"analysis"/"113_pinned_event_within_year_repeat_eligibility.py"
SPEC=importlib.util.spec_from_file_location("tampa_repeat_eligibility",PATH)
M=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)

def make_event_csv(visits):
    handle=io.StringIO()
    writer=csv.DictWriter(handle,fieldnames=M.HEADER)
    writer.writeheader()
    for visit in visits:
        pid,node,year,date,marks=visit
        writer.writerow({"eventID":pid,"eventType":"Transect","locationID":node,
                         "eventDate":date,"year":str(year),"waterBody":"Old Tampa Bay",
                         "samplingProtocol":"synthetic protocol","institutionCode":"SYNTHETIC"})
        for i,mark in enumerate(marks):
            writer.writerow({"eventID":f"{pid}-point-{i}","eventType":"Point",
                             "parentEventID":pid,"locationID":mark})
    return handle.getvalue().encode()

class PinnedSourceRepeatTests(unittest.TestCase):
    def test_eligible_same_year_distinct_dates_and_roster_overlap(self):
        data=make_event_csv([
            ("v1","N1",2024,"2024-06-10",["a","b","c"]),
            ("v2","N1",2024,"2024-06-14",["b","c","d"]),
            ("v3","N2",2025,"2025-07-14",["x","y","z"]),
        ])
        eligible,marks,r=M.source_index(data)
        self.assertEqual(r["eligible_transect_visits"],3)
        self.assertEqual(r["eligible_node_years"],2)
        a=M.audit(eligible,marks)
        self.assertEqual(a["summary"]["extra_visits_beyond_first_node_year"],1)
        self.assertEqual(a["summary"]["node_year_groups_with_multiple_parent_dates"],1)
        self.assertEqual(a["summary"]["total_marks_repeated_across_distinct_dates_sum_across_node_years"],2)
        self.assertEqual(a["summary"]["distinct_date_pairs_sharing_mark_ids"],1)
        self.assertEqual(a["summary"]["within_7_days_pairs"],1)
        self.assertFalse(a["repeated_node_year_details"][0]["valid_independent_detection_replicates_verified"])

    def test_same_day_does_not_become_independent_temporal_revisit(self):
        data=make_event_csv([
            ("v1","N1",2024,"2024-06-10",["a","b","c"]),
            ("v2","N1",2024,"2024-06-10",["a","b","c"])
        ])
        e,m,r=M.source_index(data)
        a=M.audit(e,m)
        self.assertEqual(a["summary"]["extra_visits_beyond_first_node_year"],1)
        self.assertEqual(a["summary"]["node_year_groups_with_multiple_parent_dates"],0)
        self.assertEqual(a["summary"]["distinct_date_pairs_sharing_mark_ids"],0)

    def test_distinct_dates_disjoint_marks_are_not_repeat_detections(self):
        data=make_event_csv([
            ("v1","N1",2024,"2024-06-10",["a","b","c"]),
            ("v2","N1",2024,"2024-06-11",["d","e","f"])
        ])
        e,m,r=M.source_index(data)
        a=M.audit(e,m)
        self.assertEqual(a["summary"]["node_year_groups_with_multiple_parent_dates"],1)
        self.assertEqual(a["summary"]["node_year_groups_with_repeated_marks_across_distinct_dates"],0)
        self.assertEqual(a["summary"]["within_7_days_pairs"],0)

    def test_parent_with_less_than_three_point_rows_excluded(self):
        data=make_event_csv([
            ("v1","N1",2024,"2024-06-10",["a","b"]),
            ("v2","N1",2024,"2024-06-11",["a","b","c"])
        ])
        e,m,r=M.source_index(data)
        self.assertEqual(r["eligible_transect_visits"],1)
        self.assertEqual(M.audit(e,m)["summary"]["extra_visits_beyond_first_node_year"],0)

    def test_invalid_year_or_orphan_fails_closed(self):
        data=make_event_csv([("v1","N1",2023,"2024-06-10",["a","b","c"])])
        with self.assertRaises(RuntimeError):
            M.source_index(data)
        h=io.StringIO()
        w=csv.DictWriter(h,fieldnames=M.HEADER);w.writeheader()
        w.writerow({"eventID":"x","eventType":"Point","parentEventID":"missing",
                    "locationID":"markA"})
        with self.assertRaises(RuntimeError):
            M.source_index(h.getvalue().encode())

    def test_no_biological_response_fields_needed(self):
        data=make_event_csv([("v1","N1",2024,"2024-06-10",["a","b","c"])])
        eligible,marks,meta=M.source_index(data)
        self.assertEqual(len(eligible),1)
        self.assertFalse(any("thalassia" in k.lower() for k in M.HEADER))
        self.assertEqual(M.audit(eligible,marks)["summary"]["node_year_groups_with_multiple_eligible_visits"],0)

if __name__=="__main__":
    unittest.main()
