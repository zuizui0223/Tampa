#!/usr/bin/env python3
"""Response-free known-truth tests of candidate -> core -> future meter-mark identity."""
from __future__ import annotations

import copy
import importlib.util
import unittest
import csv
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"analysis/85_tnc_anchor_lineage.py"
CANDIDATE=ROOT/"analysis/84_tnc_current_anchor_candidate.py"

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    assert spec is not None and spec.loader is not None
    m=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

def fixtures():
    m=load("candidate",CANDIDATE)
    nodes=[]; marks=[]
    for bi,bay in enumerate(m.BAYS):
        for ni in range(9):
            node=f"synthetic-{bi}-{ni}"
            nodes.append({"node_id":node,"water_body":bay,
              "thalassia_positive":"true","tnc_date":"2027-08-03",
              "baseline_survey_date":"2027-08-01"})
            for idx,site in enumerate((10,20,30,40)):
                marks.append({"node_id":node,"water_body":bay,
                 "baseline_survey_date":"2027-08-01",
                 "point_location_id":f"{node}:mark:{site}",
                 "site_m":str(site),"thalassia_present":"true",
                 "baseline_bb_anchor":str(idx+1)})
    result=m.build(nodes,marks)
    assert result["status"]=="PASS_ANCHOR_CANDIDATE_GEOMETRY_ONLY"
    candidates=result["anchor_candidates"]
    approve=[]; tnc=[]; future=[]
    for ai,row in enumerate(candidates):
        key={k:row[k] for k in ("node_id","water_body","anchor_id","point_location_id")}
        approve.append({**key,"approval_reference_id":"TEST_PERMIT_NOT_REAL",
           "approved_before_collection":"true","anchor_freeze_date":"2027-08-01"})
        tnc.append({**key,"core_id":f"SYNTH-CORE-{ai}",
            "core_collection_date":"2027-08-03",
            "anchor_tnc":str(80+ai%3*10+ai//3*.03),
            "anchor_tnc_qc_pass":"true"})
        future.append({
            "node_id":row["node_id"],"water_body":row["water_body"],
            "point_location_id":row["point_location_id"],
            "future_survey_date":"2028-08-01",
            "future_bb_anchor":str(row["baseline_bb_anchor"])
        })
    future[0]["future_bb_anchor"]="0" # sampled focal absence is a VALID measured score.
    return candidates,approve,tnc,future

class TNCLineageTests(unittest.TestCase):
    def setUp(self):
        self.m=load("lineage",SCRIPT)
        self.data=fixtures()

    def test_complete_current_to_future_linkage(self):
        result=self.m.build(*self.data)
        self.assertEqual(result["status"],"PASS_LINEAGE_FOR_FROZEN_PRIMARY_INPUT")
        self.assertEqual(result["complete_nodes"],36)
        self.assertEqual(len(result["primary_input_rows"]),108)
        self.assertEqual(set(result["complete_nodes_by_bay"].values()),{9})
        self.assertEqual(set(row["anchor_id"] for row in result["primary_input_rows"]),{"q25","q50","q75"})
        self.assertEqual(set(row["anchor_tnc_qc_pass"] for row in result["primary_input_rows"]),{True})
        self.assertEqual(next(r for r in result["primary_input_rows"]
            if r["node_id"]==self.data[0][0]["node_id"] and r["anchor_id"]=="q25")["future_bb_anchor"],0.0)
        self.assertNotIn("point_location_id",result["primary_input_rows"][0])
        self.assertEqual(len(result["lineage_rows"]),108)
        self.assertEqual(result["lineage_rows"][0]["point_location_id"],
                         self.data[0][0]["point_location_id"])
        self.assertEqual(result["lineage_rows"][0]["core_id"],"SYNTH-CORE-0")
        self.assertEqual(result["lineage_rows"][0]["future_survey_date"],"2028-08-01")
        self.assertEqual(result["evidence_class"],"SYNTHETIC_OR_EXTERNALLY_SUPPLIED_UNVERIFIED_SOURCE_ONLY")

    def test_cli_produces_exact_frozen_model_input_and_hashed_mark_lineage(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            paths={}
            for name,rows in zip(("candidate","approval","tnc","future"),self.data):
                path=root/(name+".csv")
                with path.open("w",newline="") as h:
                    w=csv.DictWriter(h,fieldnames=list(rows[0]))
                    w.writeheader()
                    w.writerows(rows)
                paths[name]=path
            result_path=root/"lineage.json"
            output=root/"frozen_primary.csv"
            cmd=[sys.executable,str(SCRIPT),
                 "--candidate",str(paths["candidate"]),
                 "--approval",str(paths["approval"]),
                 "--tnc",str(paths["tnc"]),
                 "--future",str(paths["future"]),
                 "--report",str(result_path),
                 "--primary-input",str(output)]
            cp=subprocess.run(cmd,capture_output=True,text=True,timeout=45)
            self.assertEqual(cp.returncode,0,(cp.stdout,cp.stderr))
            report=json.loads(result_path.read_text())
            self.assertEqual(set(report["sha256_inputs"]),{"candidate","approval","tnc","future"})
            self.assertEqual(len(report["lineage_rows"]),108)
            self.assertNotIn("primary_input_rows",report)
            with output.open(newline="") as h:
                reader=csv.DictReader(h)
                self.assertEqual(tuple(reader.fieldnames),self.m.PRIMARY)
                self.assertEqual(len(list(reader)),108)

            # A failed new attempt must not overwrite an older model input.
            cp=subprocess.run(cmd,capture_output=True,text=True,timeout=45)
            self.assertNotEqual(cp.returncode,0)
            self.assertIn("do not overwrite",cp.stderr+cp.stdout)

    def test_swapped_core_point_id_cannot_make_false_future_effect(self):
        candidates,approved,tnc,future=copy.deepcopy(self.data)
        tnc[0]["point_location_id"],tnc[1]["point_location_id"]=(
            tnc[1]["point_location_id"],tnc[0]["point_location_id"])
        with self.assertRaisesRegex(ValueError,"core.*point|point.*core|anchor.*mark"):
            self.m.build(candidates,approved,tnc,future)

    def test_unrecognized_future_location_and_duplicate_future_fatal(self):
        candidates,approved,tnc,future=copy.deepcopy(self.data)
        with self.assertRaises(ValueError):
            self.m.build(candidates,approved,tnc,
                         [dict(future[0],point_location_id="unregistered")]+future[1:])
        with self.assertRaises(ValueError):
            self.m.build(candidates,approved,tnc,future+[future[0].copy()])

    def test_qc_failure_and_nonnumeric_future_drop_whole_node_without_reselection(self):
        candidates,approved,tnc,future=copy.deepcopy(self.data)
        tnc[0]["anchor_tnc_qc_pass"]="false"
        result=self.m.build(candidates,approved,tnc,future)
        self.assertEqual(result["status"],"STOP_COMPLETE_TRIPLET_GATE")
        self.assertEqual(result["complete_nodes"],35)
        self.assertEqual(len(result["primary_input_rows"]),105)
        self.assertTrue(any(x["node_id"]==candidates[0]["node_id"] for x in result["excluded_nodes"]))
        candidates,approved,tnc,future=copy.deepcopy(self.data)
        future[0]["future_bb_anchor"]="Reported"
        result=self.m.build(candidates,approved,tnc,future)
        self.assertEqual(result["status"],"STOP_COMPLETE_TRIPLET_GATE")
        self.assertEqual(result["complete_nodes"],35)

    def test_no_unapproved_or_post_collection_approval(self):
        candidates,approved,tnc,future=copy.deepcopy(self.data)
        approved[0]["approved_before_collection"]="false"
        with self.assertRaises(ValueError):
            self.m.build(candidates,approved,tnc,future)
        candidates,approved,tnc,future=copy.deepcopy(self.data)
        approved[0]["anchor_freeze_date"]="2027-08-04"
        with self.assertRaises(ValueError):
            self.m.build(candidates,approved,tnc,future)

    def test_approval_cannot_change_the_preselected_mark(self):
        candidates,approved,tnc,future=copy.deepcopy(self.data)
        approved[0]["point_location_id"]=approved[1]["point_location_id"]
        with self.assertRaises(ValueError):
            self.m.build(candidates,approved,tnc,future)

    def test_forbidden_future_column_in_baseline_manifest(self):
        candidates,approved,tnc,future=copy.deepcopy(self.data)
        candidates[0]["future_bb_anchor"]="4"
        with self.assertRaises(ValueError):
            self.m.build(candidates,approved,tnc,future)

if __name__=="__main__":
    unittest.main()
