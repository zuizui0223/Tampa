#!/usr/bin/env python3
"""Response-free tests: current meter-mark rosters, not old anchors, determine candidate triplets."""
from __future__ import annotations

import importlib.util
import unittest
import subprocess
import sys
import csv
import json
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"analysis/84_tnc_current_anchor_candidate.py"
spec=importlib.util.spec_from_file_location("current_tnc_anchor_candidate",SOURCE)
assert spec is not None and spec.loader is not None
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

BAYS=("Old Tampa Bay","Middle Tampa Bay","Lower Tampa Bay","Boca Ciega Bay")
COUNTS=(8,11,14,8)
SPARSE={(1,0):1,(2,0):2,(2,1):1}

def sample():
    node_rows=[]; point_rows=[]
    for bi,(bay,count) in enumerate(zip(BAYS,COUNTS)):
        for i in range(count):
            nid=f"synthetic-bay{bi}-node{i}"
            node_rows.append({
              "node_id":nid,"water_body":bay,"thalassia_positive":"true",
              "tnc_date":"2027-08-03","baseline_survey_date":"2027-08-01"
            })
            npositive=SPARSE.get((bi,i),5)
            for k,site in enumerate((10,20,30,40,50,60)):
                focal=k<npositive
                point_rows.append({
                    "node_id":nid,"water_body":bay,
                    "baseline_survey_date":"2027-08-01",
                    "point_location_id":f"{nid}:mark:{site}",
                    "site_m":str(site),
                    "thalassia_present":"true" if focal else "false",
                    "baseline_bb_anchor":str((1.0,1.5,2.0,2.5,3.0)[k]) if focal else "0",
                })
    return node_rows,point_rows

class ProspectiveAnchorTests(unittest.TestCase):
    def test_census_and_frozen_triplet_gate(self):
        nodes,marks=sample()
        r=mod.build(nodes,marks)
        self.assertEqual(r["status"],"PASS_ANCHOR_CANDIDATE_GEOMETRY_ONLY")
        self.assertEqual(r["historical_frame_reference"],"NOT_USED_FOR_SELECTION")
        self.assertEqual(r["positive_nodes"],41)
        self.assertEqual(r["complete_triplet_nodes"],38)
        self.assertEqual(r["bay_complete_triplet_counts"],dict(zip(BAYS,(8,10,12,8))))
        self.assertEqual(len(r["anchor_candidates"]),114)
        self.assertEqual(len(r["excluded_nodes"]),3)
        example=[a for a in r["anchor_candidates"] if a["node_id"]=="synthetic-bay0-node0"]
        self.assertEqual([(a["anchor_id"],a["site_m"]) for a in example],
                         [("q25",20.0),("q50",30.0),("q75",40.0)])
        self.assertEqual({a["sampling_authority_status"] for a in example},{"NOT_AUTHORIZED"})
        self.assertEqual({a["current_eligibility_evidence"] for a in example},{"CURRENT_BASELINE_INPUT_ONLY"})
        self.assertEqual({a["baseline_bb_anchor"] for a in example},{1.5,2.0,2.5})

    def test_missing_selected_bb_does_not_choose_another_mark(self):
        nodes,marks=sample()
        targets={f"synthetic-bay0-node{i}:mark:30" for i in range(3)}
        for m in marks:
            if m["point_location_id"] in targets:
                m["baseline_bb_anchor"]="Reported"
        r=mod.build(nodes,marks)
        self.assertEqual(r["status"],"STOP_COMPLETE_TRIPLET_GATE")
        self.assertEqual(r["complete_triplet_nodes"],35)
        self.assertEqual(len(r["anchor_candidates"]),105)
        self.assertEqual(len(r["excluded_nodes"]),6)
        for nid in [f"synthetic-bay0-node{i}" for i in range(3)]:
            self.assertTrue(any(z["node_id"]==nid and "numeric" in z["reason"].lower()
                                for z in r["excluded_nodes"]))

    def test_duplicate_mark_or_unknown_node_fails_closed(self):
        nodes,marks=sample()
        with self.assertRaises(ValueError):
            mod.build(nodes,marks+[marks[0].copy()])
        with self.assertRaises(ValueError):
            mod.build(nodes,marks+[dict(marks[0],node_id="unknown")])

    def test_future_data_and_false_positivity_do_not_pass(self):
        nodes,marks=sample()
        with self.assertRaises(ValueError):
            mod.build(nodes,[dict(marks[0],future_bb_anchor="4")]+marks[1:])
        with self.assertRaises(ValueError):
            mod.build([dict(nodes[0],thalassia_positive="false")]+nodes[1:],marks)

    def test_source_year_and_date_mismatch_rejected(self):
        nodes,marks=sample()
        with self.assertRaises(ValueError):
            mod.build(nodes,[dict(marks[0],baseline_survey_date="2027-08-07")]+marks[1:])
        with self.assertRaises(ValueError):
            mod.build([dict(nodes[0],tnc_date="2027-08-30")]+nodes[1:],marks)

    def test_cli_reports_candidate_not_field_authorization(self):
        nodes,points=sample()
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            node_file=root/"node_date.csv"
            point_file=root/"complete_current_point_roster.csv"
            for path,rows in ((node_file,nodes),(point_file,points)):
                with path.open("w",newline="",encoding="utf-8") as h:
                    w=csv.DictWriter(h,fieldnames=list(rows[0]))
                    w.writeheader()
                    w.writerows(rows)
            report=root/"candidate_status.json"
            roster=root/"candidate_triplets.csv"
            cmd=[sys.executable,str(SOURCE),"--nodes",str(node_file),
                 "--points",str(point_file),"--out",str(report),
                 "--candidate-csv",str(roster)]
            cp=subprocess.run(cmd,text=True,capture_output=True,timeout=30)
            self.assertEqual(cp.returncode,0,(cp.stdout,cp.stderr))
            j=json.loads(report.read_text())
            self.assertEqual(j["status"],"PASS_ANCHOR_CANDIDATE_GEOMETRY_ONLY")
            with roster.open(newline="") as h:
                exported=list(csv.DictReader(h))
            self.assertEqual(len(exported),114)
            self.assertTrue(all(x["sampling_authority_status"]=="NOT_AUTHORIZED"
                                for x in exported))
            for r in points:
                if r["node_id"] in {f"synthetic-bay0-node{i}" for i in range(3)} and r["site_m"]=="30":
                    r["baseline_bb_anchor"]="Reported"
            with point_file.open("w",newline="",encoding="utf-8") as h:
                w=csv.DictWriter(h,fieldnames=list(points[0]))
                w.writeheader();w.writerows(points)
            cp=subprocess.run(cmd,text=True,capture_output=True,timeout=30)
            self.assertEqual(cp.returncode,2,(cp.stdout,cp.stderr))
            self.assertEqual(json.loads(report.read_text())["status"],
                             "STOP_COMPLETE_TRIPLET_GATE")

    def test_tie_break_is_nearest_then_lower_site(self):
        self.assertEqual(mod.quartile_sites([10,20,30,40]),[20.,30.,40.])
        self.assertEqual(mod.quartile_sites([10,20,40,50]),[20.,40.,50.])

if __name__=="__main__":
    unittest.main()
