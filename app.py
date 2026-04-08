import pandas as pd
from dash import Dash, dcc, html, Input, Output, callback
import plotly.express as px
import plotly.graph_objects as go

from analysis import connect_db, extract_data, compute_kpis


# -----------------------------
# Data loading and preparation
# -----------------------------
def load_base_data():
    engine = connect_db()
    data = extract_data(engine)
    kpis = compute_kpis(data)

    merged = kpis["merged"].copy()
    merged["city"] = merged["city"].fillna("Unknown")
    merged["order_date"] = pd.to_datetime(merged["order_date"])
    merged["order_month"] = merged["order_date"].dt.to_period("M").astype(str)

    return kpis, merged


def build_kpi_summary(df):
    order_totals = (
        df.groupby(["order_id", "customer_id", "city", "order_date"], as_index=False)["revenue"]
        .sum()
        .rename(columns={"revenue": "order_value"})
    )

    total_revenue = float(df["revenue"].sum()) if not df.empty else 0.0
    average_order_value = float(order_totals["order_value"].mean()) if not order_totals.empty else 0.0
    total_orders = int(df["order_id"].nunique()) if not df.empty else 0

    top_city_df = (
        df.groupby("city", as_index=False)["revenue"]
        .sum()
        .sort_values("revenue", ascending=False)
    )
    top_city = top_city_df.iloc[0]["city"] if not top_city_df.empty else "N/A"
    top_city_revenue = float(top_city_df.iloc[0]["revenue"]) if not top_city_df.empty else 0.0

    return {
        "total_revenue": total_revenue,
        "average_order_value": average_order_value,
        "total_orders": total_orders,
        "top_city": top_city,
        "top_city_revenue": top_city_revenue,
    }


def build_filtered_df(df, selected_city, start_date, end_date):
    filtered = df.copy()

    if selected_city and selected_city != "All":
        filtered = filtered[filtered["city"] == selected_city]

    if start_date:
        filtered = filtered[filtered["order_date"] >= pd.to_datetime(start_date)]
    if end_date:
        filtered = filtered[filtered["order_date"] <= pd.to_datetime(end_date)]

    return filtered


# -----------------------------
# Initialize app + data
# -----------------------------
kpis, merged_df = load_base_data()
available_cities = ["All"] + sorted(merged_df["city"].dropna().unique().tolist())
min_date = merged_df["order_date"].min().date()
max_date = merged_df["order_date"].max().date()

app = Dash(__name__, suppress_callback_exceptions=True)
app.title = "Amman Digital Market Dash App"


# -----------------------------
# Page layouts
# -----------------------------
def page_overview_layout():
    return html.Div([
        html.H2("Page 1 — KPI Overview"),
        html.Div([
            html.Div([
                html.Label("Select City"),
                dcc.Dropdown(
                    id="city-filter",
                    options=[{"label": c, "value": c} for c in available_cities],
                    value="All",
                    clearable=False
                ),
            ], style={"width": "30%", "display": "inline-block", "marginRight": "2%"}),
            html.Div([
                html.Label("Select Date Range"),
                dcc.DatePickerRange(
                    id="date-range",
                    start_date=min_date,
                    end_date=max_date,
                    display_format="YYYY-MM-DD"
                ),
            ], style={"width": "60%", "display": "inline-block"}),
        ], style={"marginBottom": "20px"}),

        html.Div([
            dcc.Graph(id="gauge-total-revenue", style={"width": "49%", "display": "inline-block"}),
            dcc.Graph(id="gauge-aov", style={"width": "49%", "display": "inline-block"}),
        ]),
        html.Div([
            dcc.Graph(id="gauge-total-orders", style={"width": "49%", "display": "inline-block"}),
            dcc.Graph(id="gauge-top-city-revenue", style={"width": "49%", "display": "inline-block"}),
        ]),

        html.H4("Revenue by City"),
        dcc.Graph(id="overview-city-bar"),

        html.Div([
            html.P("The selected city and date range apply across all pages."),
        ], style={"marginTop": "12px"})
    ])


def page_timeseries_layout():
    return html.Div([
        html.H2("Page 2 — Time-Series Deep Dive"),
        html.P("This page is filtered by the city and date range selected on Page 1."),
        dcc.Graph(id="monthly-revenue-line"),
        dcc.Graph(id="monthly-orders-line"),
    ])


def page_cohort_layout():
    return html.Div([
        html.H2("Page 3 — Cohort Comparison"),
        html.P("This page is filtered by the city and date range selected on Page 1."),
        html.Div([
            html.Div([
                html.Label("Select Cohort View"),
                dcc.Dropdown(
                    id="cohort-dimension",
                    options=[
                        {"label": "Category", "value": "category"},
                        {"label": "City", "value": "city"},
                    ],
                    value="category",
                    clearable=False
                ),
            ], style={"width": "35%", "display": "inline-block", "marginRight": "2%"}),
        ], style={"marginBottom": "16px"}),

        dcc.Graph(id="cohort-bar"),
        dcc.Graph(id="cohort-box"),
    ])


app.layout = html.Div([
    dcc.Location(id="url"),
    dcc.Store(id="shared-filters", data={
        "city": "All",
        "start_date": str(min_date),
        "end_date": str(max_date)
    }),

    html.H1("Amman Digital Market — Multi-Page Analytical Report"),
    html.Div([
        dcc.Link("Page 1: KPI Overview", href="/", style={"marginRight": "20px"}),
        dcc.Link("Page 2: Time-Series Deep Dive", href="/timeseries", style={"marginRight": "20px"}),
        dcc.Link("Page 3: Cohort Comparison", href="/cohorts"),
    ], style={"marginBottom": "24px"}),

    html.Div(id="page-content")
])


# -----------------------------
# Routing
# -----------------------------
@callback(
    Output("page-content", "children"),
    Input("url", "pathname")
)
def render_page(pathname):
    if pathname == "/timeseries":
        return page_timeseries_layout()
    if pathname == "/cohorts":
        return page_cohort_layout()
    return page_overview_layout()


# -----------------------------
# Shared filters storage
# -----------------------------
@callback(
    Output("shared-filters", "data"),
    Input("city-filter", "value"),
    Input("date-range", "start_date"),
    Input("date-range", "end_date"),
    prevent_initial_call=True
)
def update_shared_filters(city, start_date, end_date):
    return {
        "city": city,
        "start_date": start_date,
        "end_date": end_date
    }


# -----------------------------
# Page 1 callbacks
# -----------------------------
@callback(
    Output("gauge-total-revenue", "figure"),
    Output("gauge-aov", "figure"),
    Output("gauge-total-orders", "figure"),
    Output("gauge-top-city-revenue", "figure"),
    Output("overview-city-bar", "figure"),
    Input("city-filter", "value"),
    Input("date-range", "start_date"),
    Input("date-range", "end_date"),
)
def update_overview(city, start_date, end_date):
    filtered = build_filtered_df(merged_df, city, start_date, end_date)
    summary = build_kpi_summary(filtered)

    def make_gauge(title, value, reference):
        max_axis = max(value, reference, 1) * 1.25
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=value,
            delta={"reference": reference},
            title={"text": title},
            gauge={
                "axis": {"range": [None, max_axis]},
                "bar": {"color": "darkblue"},
                "threshold": {
                    "line": {"color": "red", "width": 3},
                    "thickness": 0.75,
                    "value": reference
                }
            }
        ))
        fig.update_layout(margin=dict(l=30, r=30, t=60, b=20))
        return fig

    fig_revenue = make_gauge("Total Revenue", summary["total_revenue"], 45000)
    fig_aov = make_gauge("Average Order Value", summary["average_order_value"], 100)
    fig_orders = make_gauge("Total Orders", summary["total_orders"], 300)
    fig_top_city = make_gauge("Top City Revenue", summary["top_city_revenue"], 14000)

    city_revenue = (
        filtered.groupby("city", as_index=False)["revenue"]
        .sum()
        .sort_values("revenue", ascending=False)
    )
    city_bar = px.bar(
        city_revenue,
        x="city",
        y="revenue",
        title="Revenue by City for the Selected Filters"
    )

    return fig_revenue, fig_aov, fig_orders, fig_top_city, city_bar


# -----------------------------
# Page 2 callbacks
# -----------------------------
@callback(
    Output("monthly-revenue-line", "figure"),
    Output("monthly-orders-line", "figure"),
    Input("shared-filters", "data")
)
def update_timeseries(shared_filters):
    filtered = build_filtered_df(
        merged_df,
        shared_filters["city"],
        shared_filters["start_date"],
        shared_filters["end_date"]
    )

    monthly_revenue = (
        filtered.groupby("order_month", as_index=False)["revenue"]
        .sum()
        .sort_values("order_month")
    )

    monthly_orders = (
        filtered.groupby("order_month", as_index=False)["order_id"]
        .nunique()
        .rename(columns={"order_id": "order_count"})
        .sort_values("order_month")
    )

    revenue_fig = px.line(
        monthly_revenue,
        x="order_month",
        y="revenue",
        markers=True,
        title="Monthly Revenue Trend"
    )
    revenue_fig.update_layout(xaxis_title="Month", yaxis_title="Revenue")

    orders_fig = px.line(
        monthly_orders,
        x="order_month",
        y="order_count",
        markers=True,
        title="Monthly Order Volume"
    )
    orders_fig.update_layout(xaxis_title="Month", yaxis_title="Orders")

    return revenue_fig, orders_fig


# -----------------------------
# Page 3 callbacks
# -----------------------------
@callback(
    Output("cohort-bar", "figure"),
    Output("cohort-box", "figure"),
    Input("shared-filters", "data"),
    Input("cohort-dimension", "value")
)
def update_cohorts(shared_filters, cohort_dimension):
    filtered = build_filtered_df(
        merged_df,
        shared_filters["city"],
        shared_filters["start_date"],
        shared_filters["end_date"]
    )

    cohort_summary = (
        filtered.groupby(cohort_dimension, as_index=False)["revenue"]
        .sum()
        .sort_values("revenue", ascending=False)
    )

    bar_fig = px.bar(
        cohort_summary,
        x=cohort_dimension,
        y="revenue",
        title=f"Revenue by {cohort_dimension.title()}"
    )
    bar_fig.update_layout(xaxis_title=cohort_dimension.title(), yaxis_title="Revenue")

    order_level = (
        filtered.groupby(["order_id", cohort_dimension], as_index=False)["revenue"]
        .sum()
        .rename(columns={"revenue": "order_value"})
    )

    box_fig = px.box(
        order_level,
        x=cohort_dimension,
        y="order_value",
        title=f"Order Value Distribution by {cohort_dimension.title()}"
    )
    box_fig.update_layout(xaxis_title=cohort_dimension.title(), yaxis_title="Order Value")

    return bar_fig, box_fig


if __name__ == "__main__":
    app.run(debug=True)