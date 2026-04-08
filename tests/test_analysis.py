"""Tests for the KPI dashboard analysis.

Write at least 3 tests:
1. test_extraction_returns_dataframes — extract_data returns a dict of DataFrames
2. test_kpi_computation_returns_expected_keys — compute_kpis returns a dict with your 5 KPI names
3. test_statistical_test_returns_pvalue — run_statistical_tests returns results with p-values
"""
import pandas as pd

from analysis import connect_db, extract_data, compute_kpis, run_statistical_tests


def test_extraction_returns_dataframes():
    """Connect to the database, extract data, and verify the result is a dict of DataFrames."""
    engine = connect_db()
    data = extract_data(engine)

    assert isinstance(data, dict)

    expected_tables = {"customers", "products", "orders", "order_items"}
    assert expected_tables.issubset(data.keys())

    for table_name in expected_tables:
        assert isinstance(data[table_name], pd.DataFrame)
        assert not data[table_name].empty


def test_kpi_computation_returns_expected_keys():
    """Compute KPIs and verify the result contains all expected KPI names."""
    engine = connect_db()
    data = extract_data(engine)
    kpis = compute_kpis(data)

    assert isinstance(kpis, dict)

    expected_kpi_keys = {
        "total_revenue",
        "monthly_revenue",
        "monthly_order_volume",
        "average_order_value",
        "revenue_by_city",
    }

    assert expected_kpi_keys.issubset(kpis.keys())


def test_statistical_test_returns_pvalue():
    """Run statistical tests and verify results include p-values."""
    engine = connect_db()
    data = extract_data(engine)
    stat_results = run_statistical_tests(data)

    assert isinstance(stat_results, dict)
    assert len(stat_results) >= 1

    found_valid_pvalue = False

    for result in stat_results.values():
        if "p_value" in result:
            assert isinstance(result["p_value"], float)
            assert 0.0 <= result["p_value"] <= 1.0
            found_valid_pvalue = True

    assert found_valid_pvalue