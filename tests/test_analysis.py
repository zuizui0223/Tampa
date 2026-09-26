import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "scale_decoupling", ROOT / "analysis" / "analyze_scale_decoupling.py"
)
MOD = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MOD)


def test_frozen_exploratory_result():
    annual = MOD.load_annual(ROOT / "data" / "annual_transect_frequency.csv")
    coverage = MOD.load_coverage(ROOT / "data" / "seagrass_coverage_tbep.csv")
    out = MOD.analyze(annual, coverage)

    assert out["design"]["annual_transect_rows"] == 1470
    assert out["design"]["mapping_year_count"] == 13

    ext = out["extent_frequency"]
    assert abs(ext["level_correlation"]["total_seagrass"] - 0.9364575110) < 1e-9
    assert abs(ext["level_correlation"]["Thalassia"] - 0.00081982647) < 1e-9
    assert abs(ext["annualized_change_correlation"]["total_seagrass"] - 0.7314054741) < 1e-9
    assert abs(ext["annualized_change_correlation"]["Thalassia"] - 0.08480639382) < 1e-9
    assert ext["annualized_change_permutation_p"]["total_seagrass"] < 0.05
    assert ext["annualized_change_permutation_p"]["Thalassia"] > 0.10

    assert abs(ext["change_2016_2022_pct"]["acres"] - (-27.65122016096)) < 1e-9
    assert abs(ext["change_2016_2022_pct"]["total_seagrass"] - (-12.91779355551)) < 1e-9
    assert abs(ext["change_2016_2022_pct"]["Thalassia"] - 15.50602373376) < 1e-9

    mem = out["thalassia_memory"]
    assert mem["all"]["n"] == 1179
    assert abs(mem["through_2016"]["persistence"] - 0.96131528046) < 1e-9
    assert abs(mem["2017_2025"]["persistence"] - 0.97727272727) < 1e-9
    assert abs(mem["frequency_lag_slope"]["through_2016"] - 0.91171778071) < 1e-9
    assert abs(mem["frequency_lag_slope"]["2017_2025"] - 0.94101521175) < 1e-9

    lo, hi = mem["cluster_bootstrap_95pct_post_minus_pre"]["persistence"]
    assert lo < 0 < hi
    lo, hi = mem["cluster_bootstrap_95pct_post_minus_pre"]["frequency_lag_slope"]
    assert lo < 0 < hi


if __name__ == "__main__":
    test_frozen_exploratory_result()
    print("frozen exploratory result: OK")
