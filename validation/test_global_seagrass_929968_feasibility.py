"""Synthetic source-format, pairing and site-year grain tests. No live data needed."""
from __future__ import annotations
import importlib.util
import unittest
from pathlib import Path

PATH=Path(__file__).resolve().parents[1]/"analysis"/"114_global_seagrass_929968_feasibility.py"
SPEC=importlib.util.spec_from_file_location("tampa_global929968",PATH)
M=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)

HEAD=[
    "Latitude","Longitude","Seagr bioregion","Habitat","Genus","Year obs [a AD]",
    "Seagr biom above dm [g/m**2]","Seagr biom below dm [g/m**2]",
    "Seagr biom tot dm [g/m**2]","Seagr shoot dens [#/m**2]","Seagr cov [%]","Reference"
]
def fake_rows():
    return [
        dict(zip(HEAD,["21.0","-80.0","Tropical Atlantic","Coastal","Thalassia","2016",
                      "12","60","","80","25","Author A 2020"])),
        dict(zip(HEAD,["21.0","-80.0","Tropical Atlantic","Coastal","Thalassia","2017",
                      "15","45","","","30","Author A 2020"])),
        dict(zip(HEAD,["21.0","-80.0","Tropical Atlantic","Coastal","Thalassia","2017",
                      "","","","","","0","Author A 2020"])),
        dict(zip(HEAD,["40.0","-70.0","Temperate North Atlantic","Estuarine","Zostera","2018",
                      "50","25","","600","","Author B 2019"])),
    ]
def keys():
    return {short:next(h for h in HEAD if h==prefix or h.startswith(prefix+" ["))
            for short,prefix in M.EXPECTED.items()}

class GlobalFeasibilityTests(unittest.TestCase):
    def test_full_header_and_metadata_accepted(self):
        row="\t".join(HEAD)+"\n"
        r0=["\t".join(x[k] for k in HEAD) for x in fake_rows()]
        raw=("/* DATA DESCRIPTION:\nCitation: Synthetic\n*/\n"+row+"\n".join(r0*28)+"\n").encode()
        rows,k,metadata=M.tabular(raw)
        self.assertEqual(len(rows),112)
        self.assertEqual(k["ag"],"Seagr biom above dm [g/m**2]")

    def test_paired_allocation_is_same_row_only(self):
        x=M.audit(fake_rows(),keys())
        self.assertEqual(x["source_row_count"],4)
        self.assertEqual(x["exact_same_row_paired_above_below_count"],3)
        self.assertEqual(x["references_in_exact_same_row_biomass_pairs"],2)
        self.assertEqual(x["publication_geocoordinate_genus_candidates_with_two_or_more_years"],1)
        self.assertEqual(x["references_with_multiple_reported_years"],1)
        self.assertEqual(x["paired_ratio_by_genus"][0]["paired_rows"],2)
        self.assertEqual(x["cover_values_with_positive_value"],2)

    def test_exact_duplicate_rows_flagged_not_removed(self):
        d=fake_rows()
        d.append(d[0].copy())
        x=M.audit(d,keys())
        self.assertEqual(x["exact_duplicate_member_rows_not_automatically_removed"],2)
        self.assertEqual(x["exact_duplicate_row_groups"],1)
        self.assertEqual(x["source_row_count"],5)
        self.assertEqual(x["raw_reference_strings_not_independent_publications"],2)

    def test_non_numeric_is_not_zero(self):
        d=fake_rows()
        d[2][HEAD[10]]="N/A"
        x=M.audit(d,keys())
        self.assertEqual(x["parse_and_domain_warnings"]["nonnumeric_cover"],1)
        self.assertEqual(x["total_numeric_cover_values"],2)

    def test_no_fake_years(self):
        d=fake_rows()
        d[1][HEAD[5]]=""
        d[2][HEAD[5]]=""
        x=M.audit(d,keys())
        self.assertEqual(x["publication_geocoordinate_genus_candidates_with_two_or_more_years"],0)
        self.assertEqual(x["parse_and_domain_warnings"]["missing_or_noninteger_year"],2)

    def test_html_is_rejected(self):
        with self.assertRaises(ValueError):
            M.tabular(b"<!DOCTYPE html> forbidden")

    def test_duplicate_column_is_rejected(self):
        raw=("\t".join(HEAD+["Reference"])+"\n"+("\t".join(["1"]*len(HEAD+["Reference"]))+"\n")*100).encode()
        with self.assertRaises(ValueError):
            M.tabular(raw)

if __name__=="__main__":
    unittest.main()
