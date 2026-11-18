"""Synthetic metadata gate regression tests. No real source data is fetched."""
import hashlib
import unittest

from check_metadata import SCHEMA, ROLES, DOCS, FLAGS, EXCLUDE, gate

def fake_manifest():
    # A deliberately fictional passing specimen. Never constitutes CHAP validation.
    return {
        "schema": SCHEMA, "program_id": 570, "response_values_opened": False,
        "authorization": "confirmed_by_data_requester",
        "published_aggregate_outcomes_seen": True,
        "external_predictive_validation_eligible": False,
        "official_program_url": "https://data.florida-seacar.org/programs/details/570",
        "source": {
            "original_workbook_filename": "SYNTHETIC-NOT-AN-EXISTING-WORKBOOK.xlsx",
            "original_workbook_sha256": hashlib.sha256(b"SYNTHETIC").hexdigest(),
            "provenance_method": "SYNTHETIC_TEST_ONLY",
            "raw_response_opened": False
        },
        "documentation": {key: {"url":"https://example.org/protocol",
                                "locator":"FICTITIOUS "+key} for key in DOCS},
        "column_roles": {key:"FAKE_"+key for key in ROLES},
        "identity_and_observation": {
            **{key:True for key in FLAGS},
            "raw_bb_few_category_resolution":"confirmed_0.5",
            "zero_assignment":"sampled_complete_focal_negative_only",
            "primary_start_year":2016, "primary_end_year":2025
        },
        "excluded_station_codes":sorted(EXCLUDE)
    }

class MetadataGateTests(unittest.TestCase):
    def test_synthetic_positive_is_not_scientific_result(self):
        r=gate(fake_manifest())
        self.assertEqual(r["status"],"PASS_METADATA_DOCUMENTATION_ONLY",r)
        self.assertFalse(r["external_replication_observed"])
        self.assertEqual(r["response_rows_read"],0)
        self.assertEqual(r["model_fits"],0)

    def blocked(self,change,error):
        m=fake_manifest()
        change(m)
        r=gate(m)
        self.assertEqual(r["status"],"STOP_METADATA_GATE")
        self.assertIn(error,r["errors"])
        self.assertEqual(r["model_fits"],0)
        self.assertEqual(r["response_rows_read"],0)

    def test_published_exposure_cannot_be_silently_omitted(self):
        self.blocked(lambda m:m.update(published_aggregate_outcomes_seen=False),
                     "PUBLISHED_OUTCOME_EXPOSURE_NOT_ACKNOWLEDGED")
    def test_untouched_validation_claim_is_forbidden(self):
        self.blocked(lambda m:m.update(external_predictive_validation_eligible=True),
                     "UNTOUCHED_PREDICTION_CLAIM_FORBIDDEN")
    def test_postresponse_access(self):
        self.blocked(lambda m:m.update(response_values_opened=True),"RESPONSES_ALREADY_OPENED")
    def test_wrong_program(self):
        self.blocked(lambda m:m.update(program_id=5721),"PROGRAM_NOT_570")
    def test_unverified_access(self):
        self.blocked(lambda m:m.update(authorization="pending"),"DATA_ACCESS_UNCONFIRMED")
    def test_not_repeated_quadrat(self):
        self.blocked(lambda m:m["identity_and_observation"].update(repeat_quadrats_only=False),
                     "IDENTITY_RULE_UNRESOLVED:repeat_quadrats_only")
    def test_bed_edge(self):
        self.blocked(lambda m:m["identity_and_observation"].update(exclude_variable_bed_edges=False),
                     "IDENTITY_RULE_UNRESOLVED:exclude_variable_bed_edges")
    def test_missing_as_zero(self):
        self.blocked(lambda m:m["identity_and_observation"].update(zero_assignment="missing_as_zero"),
                     "ZERO_MISSING_POLICY_UNSAFE")
    def test_missing_roster(self):
        self.blocked(lambda m:m["column_roles"].pop("surveyed_quadrat_roster"),
                     "COLUMN_ROLE_UNRESOLVED:surveyed_quadrat_roster")
    def test_bb_rounding(self):
        self.blocked(lambda m:m["identity_and_observation"].update(raw_bb_few_category_resolution="unknown"),
                     "BB_FEW_CATEGORY_UNRESOLVED_0.05_VS_0.5")
    def test_blade_sampling_not_documented(self):
        self.blocked(lambda m:m["identity_and_observation"].update(healthy_thalassia_blade_selection_documented=False),
                     "IDENTITY_RULE_UNRESOLVED:healthy_thalassia_blade_selection_documented")
    def test_shoot_extrapolation_not_documented(self):
        self.blocked(lambda m:m["documentation"].pop("shoot_subquadrat_extrapolation_protocol"),
                     "DOCUMENTATION_MISSING:shoot_subquadrat_extrapolation_protocol")
    def test_station_exclusions(self):
        self.blocked(lambda m:m.update(excluded_station_codes=["CR01"]),
                     "STATION_EXCLUSION_LIST_INCOMPLETE_OR_CHANGED")
    def test_another_year_window(self):
        self.blocked(lambda m:m["identity_and_observation"].update(primary_end_year=2024),
                     "PRIMARY_WINDOW_DRIFT")
    def test_doc_not_located(self):
        self.blocked(lambda m:m["documentation"]["sampling_zero_missing_protocol"].update(locator=""),
                     "DOCUMENTATION_MISSING:sampling_zero_missing_protocol")
    def test_duplicate_column_role(self):
        self.blocked(lambda m:m["column_roles"].update(shoot_count=m["column_roles"]["blade_length_cm"]),
                     "COLUMN_ROLE_AMBIGUOUS_DUPLICATE")
    def test_no_file_hash(self):
        self.blocked(lambda m:m["source"].update(original_workbook_sha256=None),
                     "WORKBOOK_SHA256_MISSING")

if __name__=="__main__":
    unittest.main()
