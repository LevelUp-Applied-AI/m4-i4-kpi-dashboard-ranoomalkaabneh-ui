import os
from analysis import connect_db, extract_data, compute_kpis
import plotly.express as px
from plotly.subplots import make_subplots

def create_interactive_dashboard(kpi_results):
    monthly_revenue = kpi_results["monthly_revenue"]
    monthly_order_volume = kpi_results["monthly_order_volume"]
    revenue_by_city = kpi_results["revenue_by_city"]
    revenue_by_category = kpi_results["revenue_by_category"]

    fig = make_subplots(
        rows=2,
        cols=2,
        subplot_titles=(
            "Monthly Revenue",
            "Monthly Orders",
            "Revenue by City",
            "Revenue by Category"
        )
    )

    # Revenue
    fig1 = px.line(monthly_revenue, x="order_month", y="revenue", markers=True)
    for t in fig1.data:
        fig.add_trace(t, row=1, col=1)

    # Orders
    fig2 = px.bar(monthly_order_volume, x="order_month", y="order_count")
    for t in fig2.data:
        fig.add_trace(t, row=1, col=2)

    # City
    fig3 = px.bar(revenue_by_city, x="city", y="revenue")
    for t in fig3.data:
        fig.add_trace(t, row=2, col=1)

    # Category
    fig4 = px.bar(revenue_by_category, x="category", y="revenue")
    for t in fig4.data:
        fig.add_trace(t, row=2, col=2)

    fig.update_layout(
        title="Interactive KPI Dashboard",
        height=800,
        width=1200,
        showlegend=False
    )

    os.makedirs("output", exist_ok=True)
    fig.write_html("output/dashboard.html")


def main():
    engine = connect_db()
    data = extract_data(engine)
    kpis = compute_kpis(data)

    create_interactive_dashboard(kpis)

    print("Dashboard saved to output/dashboard.html")


if __name__ == "__main__":
    main()