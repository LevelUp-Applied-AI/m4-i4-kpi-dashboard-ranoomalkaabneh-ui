# Executive Summary — Amman Digital Market Analytics

## Top Findings

<!-- List 3-5 key findings from your analysis. Each finding should be one sentence
     that a non-technical stakeholder can understand. Support each with a specific
     number or statistic. -->

1.Amman is the primary revenue driver of the marketplace, generating 15,719.0 in total revenue, more than double Irbid’s 7,250.5.
2-Revenue peaks are driven by surges in order volume, with June 2025 reaching 5,086.5 in revenue and 47 orders—the highest in the dataset.
3-Product categories significantly impact order value, with a one-way ANOVA confirming meaningful differences across categories (F = 56.79, p < 0.001).
4-Higher revenue in Amman is not due to higher order value, as a Welch t-test found no statistically significant difference in average order value between Amman and Irbid (p = 0.527).


## Supporting Data

<!-- For each finding above, reference the specific KPI value, statistical test result,
     or visualization that supports it. Include chart filenames so the reader can
     locate the evidence. -->
     Finding 1:
    KPI: Revenue by City
     Values: Amman = 15,719.0, Irbid = 7,250.5
      Chart: revenue_by_city.png
     Finding 2:
     KPIs: Monthly Revenue Trend & Monthly Order Volume
     Values: June 2025 = 5,086.5 revenue, 47 orders
     Charts: monthly_revenue_trend.png, monthly_order_volume.png
     Finding 3:
      KPI: Order Value by Category
     Statistical Test: ANOVA (F = 56.79, p < 0.001)
      Chart: order_value_by_category_boxplot.png
     Finding 4:
     KPI: Average Order Value by City
     Statistical Test: Welch t-test (t = 0.63, p = 0.527)
     Interpretation: No significant difference between Amman and Irbid

## Recommendations

<!-- Based on your findings, what actions should the business take?
     Each recommendation should be specific, actionable, and tied to a finding above. -->

1-Prioritize growth strategies in Amman, focusing on increasing order volume rather than changing pricing, since higher revenue is driven by more transactions, not higher order values.
2-Analyze and replicate the drivers behind March and June 2025 spikes, such as promotions, campaigns, or seasonal demand, to consistently boost order volume.
3-Focus on high-performing product categories, as category-level differences significantly impact order value, and optimizing product mix can increase overall revenue.
