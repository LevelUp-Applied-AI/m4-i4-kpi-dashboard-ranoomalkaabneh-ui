import os
import json
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from analysis import connect_db, extract_data, compute_kpis


def load_config(config_path="config.json"):
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def evaluate_status(actual, thresholds):
    """Return green/yellow/red based on threshold comparison."""
    if actual >= thresholds["green"]:
        return "green"
    elif actual >= thresholds["yellow"]:
        return "yellow"
    return "red"


def summarize_kpis(kpi_results, config):
    """Build KPI summary with actual values, targets, and statuses."""
    monthly_revenue = kpi_results["monthly_revenue"]
    monthly_order_volume = kpi_results["monthly_order_volume"]
    revenue_by_city = kpi_results["revenue_by_city"]

    summary = {
        "total_revenue": {
            "actual": float(kpi_results["total_revenue"]),
            "target": config["thresholds"]["total_revenue"]["green"],
        },
        "average_order_value": {
            "actual": float(kpi_results["average_order_value"]),
            "target": config["thresholds"]["average_order_value"]["green"],
        },
        "peak_monthly_revenue": {
            "actual": float(monthly_revenue["revenue"].max()),
            "target": config["thresholds"]["peak_monthly_revenue"]["green"],
        },
        "peak_monthly_order_volume": {
            "actual": float(monthly_order_volume["order_count"].max()),
            "target": config["thresholds"]["peak_monthly_order_volume"]["green"],
        },
        "top_city_revenue": {
            "actual": float(revenue_by_city["revenue"].max()),
            "target": config["thresholds"]["top_city_revenue"]["green"],
        },
    }

    for kpi_name, info in summary.items():
        info["status"] = evaluate_status(
            info["actual"],
            config["thresholds"][kpi_name]
        )

    return summary


def prepare_filter_data(kpi_results):
    """Prepare grouped data for dropdown filters."""
    merged = kpi_results["merged"].copy()
    merged["city"] = merged["city"].fillna("Unknown")
    merged["order_date"] = pd.to_datetime(merged["order_date"])
    merged["year"] = merged["order_date"].dt.year.astype(str)

    city_revenue = (
        merged.groupby("city", as_index=False)["revenue"]
        .sum()
        .sort_values("revenue", ascending=False)
    )

    category_revenue = (
        merged.groupby("category", as_index=False)["revenue"]
        .sum()
        .sort_values("revenue", ascending=False)
    )

    year_revenue = (
        merged.groupby("year", as_index=False)["revenue"]
        .sum()
        .sort_values("year")
    )

    return city_revenue, category_revenue, year_revenue


def build_monitor_dashboard(summary, city_revenue, category_revenue, year_revenue):
    """Create KPI gauges + dropdown-filter charts and save as HTML."""
    fig = make_subplots(
        rows=4,
        cols=2,
        specs=[
            [{"type": "indicator"}, {"type": "indicator"}],
            [{"type": "indicator"}, {"type": "indicator"}],
            [{"type": "indicator"}, {"type": "bar"}],
            [{"type": "bar"}, {"type": "bar"}]
        ],
        subplot_titles=(
            "Total Revenue vs Target",
            "Average Order Value vs Target",
            "Peak Monthly Revenue vs Target",
            "Peak Monthly Order Volume vs Target",
            "Top City Revenue vs Target",
            "Revenue by City",
            "Revenue by Category",
            "Revenue by Year"
        )
    )

    gauge_order = [
        "total_revenue",
        "average_order_value",
        "peak_monthly_revenue",
        "peak_monthly_order_volume",
        "top_city_revenue"
    ]

    positions = [(1, 1), (1, 2), (2, 1), (2, 2), (3, 1)]

    for kpi_name, (row, col) in zip(gauge_order, positions):
        actual = summary[kpi_name]["actual"]
        target = summary[kpi_name]["target"]
        status = summary[kpi_name]["status"]

        max_axis = max(actual, target) * 1.25 if max(actual, target) > 0 else 1

        fig.add_trace(
            go.Indicator(
                mode="gauge+number+delta",
                value=actual,
                delta={"reference": target},
                title={"text": kpi_name.replace("_", " ").title()},
                gauge={
                    "axis": {"range": [None, max_axis]},
                    "bar": {"color": status},
                    "steps": [
                        {"range": [0, target * 0.8], "color": "#f8d7da"},
                        {"range": [target * 0.8, target], "color": "#fff3cd"},
                        {"range": [target, max_axis], "color": "#d4edda"},
                    ],
                    "threshold": {
                        "line": {"color": "black", "width": 3},
                        "thickness": 0.75,
                        "value": target
                    }
                }
            ),
            row=row,
            col=col
        )

    # Row 3 Col 2: City Revenue
    fig.add_trace(
        go.Bar(
            x=city_revenue["city"],
            y=city_revenue["revenue"],
            name="Revenue by City"
        ),
        row=3,
        col=2
    )

    # Row 4 Col 1: Category Revenue
    fig.add_trace(
        go.Bar(
            x=category_revenue["category"],
            y=category_revenue["revenue"],
            name="Revenue by Category"
        ),
        row=4,
        col=1
    )

    # Row 4 Col 2: Year Revenue
    fig.add_trace(
        go.Bar(
            x=year_revenue["year"],
            y=year_revenue["revenue"],
            name="Revenue by Year"
        ),
        row=4,
        col=2
    )

    # Dropdowns using updatemenus
    fig.update_layout(
        title="Automated KPI Monitoring Dashboard",
        height=1400,
        width=1200,
        showlegend=False,
        updatemenus=[
            {
                "buttons": [
                    {
                        "label": "All Cities",
                        "method": "restyle",
                        "args": [{"x": [city_revenue["city"]], "y": [city_revenue["revenue"]]}, [5]]
                    },
                    *[
                        {
                            "label": city,
                            "method": "restyle",
                            "args": [{"x": [[city]], "y": [[revenue]]}, [5]]
                        }
                        for city, revenue in zip(city_revenue["city"], city_revenue["revenue"])
                    ]
                ],
                "direction": "down",
                "x": 0.02,
                "y": 1.12,
                "showactive": True
            },
            {
                "buttons": [
                    {
                        "label": "All Categories",
                        "method": "restyle",
                        "args": [{"x": [category_revenue["category"]], "y": [category_revenue["revenue"]]}, [6]]
                    },
                    *[
                        {
                            "label": category,
                            "method": "restyle",
                            "args": [{"x": [[category]], "y": [[revenue]]}, [6]]
                        }
                        for category, revenue in zip(category_revenue["category"], category_revenue["revenue"])
                    ]
                ],
                "direction": "down",
                "x": 0.36,
                "y": 1.12,
                "showactive": True
            },
            {
                "buttons": [
                    {
                        "label": "All Years",
                        "method": "restyle",
                        "args": [{"x": [year_revenue["year"]], "y": [year_revenue["revenue"]]}, [7]]
                    },
                    *[
                        {
                            "label": year,
                            "method": "restyle",
                            "args": [{"x": [[year]], "y": [[revenue]]}, [7]]
                        }
                        for year, revenue in zip(year_revenue["year"], year_revenue["revenue"])
                    ]
                ],
                "direction": "down",
                "x": 0.70,
                "y": 1.12,
                "showactive": True
            }
        ]
    )

    fig.add_annotation(x=0.07, y=1.16, xref="paper", yref="paper", text="City Filter", showarrow=False)
    fig.add_annotation(x=0.42, y=1.16, xref="paper", yref="paper", text="Category Filter", showarrow=False)
    fig.add_annotation(x=0.76, y=1.16, xref="paper", yref="paper", text="Date Range Filter", showarrow=False)

    os.makedirs("output", exist_ok=True)
    fig.write_html("output/kpi_monitor.html")

    return fig


def format_status_output(summary):
    """Return a simple serializable output for logging/testing."""
    return {
        kpi: {
            "actual": round(values["actual"], 2),
            "target": values["target"],
            "status": values["status"]
        }
        for kpi, values in summary.items()
    }


def main():
    config = load_config("config.json")
    engine = connect_db()
    data = extract_data(engine)
    kpi_results = compute_kpis(data)

    summary = summarize_kpis(kpi_results, config)
    city_revenue, category_revenue, year_revenue = prepare_filter_data(kpi_results)

    build_monitor_dashboard(summary, city_revenue, category_revenue, year_revenue)

    output = format_status_output(summary)

    print("=== KPI MONITOR STATUS ===")
    for kpi_name, values in output.items():
        print(
            f"{kpi_name}: actual={values['actual']}, "
            f"target={values['target']}, status={values['status']}"
        )


if __name__ == "__main__":
    main()