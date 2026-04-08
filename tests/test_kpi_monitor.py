import pandas as pd

from kpi_monitor import evaluate_status, summarize_kpis, format_status_output


def test_evaluate_status_returns_expected_color():
    thresholds = {"green": 100, "yellow": 80}

    assert evaluate_status(120, thresholds) == "green"
    assert evaluate_status(90, thresholds) == "yellow"
    assert evaluate_status(70, thresholds) == "red"


def test_summarize_kpis_returns_expected_structure():
    kpi_results = {
        "total_revenue": 50000.0,
        "average_order_value": 110.0,
        "monthly_revenue": pd.DataFrame({"revenue": [2000.0, 5200.0]}),
        "monthly_order_volume": pd.DataFrame({"order_count": [20, 45]}),
        "revenue_by_city": pd.DataFrame({
            "city": ["Amman", "Irbid"],
            "revenue": [16000.0, 7000.0]
        }),
    }

    config = {
        "thresholds": {
            "total_revenue": {"green": 45000, "yellow": 35000},
            "average_order_value": {"green": 100, "yellow": 80},
            "peak_monthly_revenue": {"green": 4500, "yellow": 3000},
            "peak_monthly_order_volume": {"green": 40, "yellow": 25},
            "top_city_revenue": {"green": 14000, "yellow": 9000},
        }
    }

    summary = summarize_kpis(kpi_results, config)

    assert "total_revenue" in summary
    assert "average_order_value" in summary
    assert "peak_monthly_revenue" in summary
    assert "peak_monthly_order_volume" in summary
    assert "top_city_revenue" in summary

    assert summary["total_revenue"]["status"] == "green"
    assert summary["average_order_value"]["status"] == "green"


def test_format_status_output_returns_serializable_dict():
    summary = {
        "total_revenue": {"actual": 48701.5, "target": 45000, "status": "green"},
        "average_order_value": {"actual": 109.43, "target": 100, "status": "green"},
    }

    formatted = format_status_output(summary)

    assert isinstance(formatted, dict)
    assert formatted["total_revenue"]["status"] == "green"
    assert isinstance(formatted["average_order_value"]["actual"], float)