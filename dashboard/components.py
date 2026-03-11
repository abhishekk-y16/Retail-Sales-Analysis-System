"""
Reusable Streamlit UI Components.

Each function renders a self-contained Plotly chart or metric card
into the active Streamlit context.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


# ---------------------------------------------------------------------------
# KPI Cards
# ---------------------------------------------------------------------------


def render_kpi_cards(
    total_sales: float,
    total_profit: float,
    profit_margin: float,
    order_count: int,
) -> None:
    """Render four metric cards in a single row."""
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Sales", f"${total_sales:,.0f}")
    c2.metric("Total Profit", f"${total_profit:,.0f}")
    c3.metric("Profit Margin", f"{profit_margin:.1f}%")
    c4.metric("Orders", f"{order_count:,}")


# ---------------------------------------------------------------------------
# Chart Renderers
# ---------------------------------------------------------------------------


def render_monthly_trend(df: pd.DataFrame) -> None:
    """Line chart of monthly Sales and Profit."""
    fig = px.line(
        df,
        x="YearMonth",
        y="Sales",
        markers=True,
        title="Monthly Revenue Trend",
        labels={"YearMonth": "Month", "Sales": "Revenue ($)"},
    )
    fig.add_scatter(
        x=df["YearMonth"],
        y=df["Profit"],
        mode="lines+markers",
        name="Profit",
        line=dict(dash="dot"),
    )
    fig.update_layout(hovermode="x unified", legend_title_text="Metric")
    st.plotly_chart(fig, use_container_width=True)


def render_category_bar(df: pd.DataFrame) -> None:
    """Bar chart of Sales by Category."""
    fig = px.bar(
        df,
        x="Category",
        y="Sales",
        color="Category",
        title="Sales by Category",
        labels={"Sales": "Revenue ($)"},
        text_auto=",.0f",
    )
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)


def render_top_products(df: pd.DataFrame) -> None:
    """Horizontal bar chart of top Sub-Categories by Sales."""
    fig = px.bar(
        df.sort_values("Sales"),
        x="Sales",
        y="Sub-Category",
        orientation="h",
        title="Top Sub-Categories by Revenue",
        labels={"Sales": "Revenue ($)", "Sub-Category": ""},
        text_auto=",.0f",
        color="Sales",
        color_continuous_scale="Teal",
    )
    fig.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)


def render_region_bar(df: pd.DataFrame) -> None:
    """Bar chart of Sales by Region."""
    fig = px.bar(
        df,
        x="Region",
        y="Sales",
        color="Region",
        title="Regional Revenue Performance",
        labels={"Sales": "Revenue ($)"},
        text_auto=",.0f",
    )
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)


def render_profit_vs_sales_scatter(df: pd.DataFrame) -> None:
    """Scatter plot of Profit vs Sales with zero-profit baseline."""
    fig = px.scatter(
        df,
        x="Sales",
        y="Profit",
        color="Category",
        opacity=0.55,
        title="Profit vs Sales — Identifying Margin Anomalies",
        labels={"Sales": "Revenue ($)", "Profit": "Profit ($)"},
    )
    fig.add_hline(y=0, line_dash="dash", line_color="red", annotation_text="Break-even")
    fig.update_layout(hovermode="closest")
    st.plotly_chart(fig, use_container_width=True)


def render_state_choropleth(df: pd.DataFrame) -> None:
    """US choropleth map of Sales by State."""
    fig = px.choropleth(
        df,
        locations="State",
        locationmode="USA-states",
        color="Sales",
        scope="usa",
        color_continuous_scale="Blues",
        title="Sales by State",
        labels={"Sales": "Revenue ($)"},
    )
    # Map state full names to abbreviations for Plotly
    st.plotly_chart(fig, use_container_width=True)


def render_discount_impact(df: pd.DataFrame) -> None:
    """Bar chart showing average profit by discount bucket."""
    fig = px.bar(
        df,
        x="Discount_Bucket",
        y="Avg_Profit",
        title="Impact of Discount on Average Profit",
        labels={"Discount_Bucket": "Discount Range", "Avg_Profit": "Avg Profit ($)"},
        text_auto=".1f",
        color="Avg_Profit",
        color_continuous_scale="RdYlGn",
    )
    fig.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)


def render_profit_margin_by_category(df: pd.DataFrame) -> None:
    """Bar chart of profit margin % by category."""
    fig = px.bar(
        df,
        x="Category",
        y="Profit_Margin_Pct",
        color="Category",
        title="Profit Margin by Category",
        labels={"Profit_Margin_Pct": "Profit Margin (%)"},
        text_auto=".1f",
    )
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)


# ---------------------------------------------------------------------------
# Advanced Analytics Renderers
# ---------------------------------------------------------------------------


def render_rfm_summary(rfm_df: pd.DataFrame) -> None:
    """Bar chart of RFM segment distribution + summary table."""
    seg_counts = rfm_df["Segment"].value_counts().reset_index()
    seg_counts.columns = ["Segment", "Customers"]

    fig = px.bar(
        seg_counts.sort_values("Customers", ascending=True),
        x="Customers",
        y="Segment",
        orientation="h",
        title="Customer Segmentation (RFM Analysis)",
        color="Customers",
        color_continuous_scale="Viridis",
        text_auto=True,
    )
    fig.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("Customer Detail Table"):
        st.dataframe(
            rfm_df[["Customer ID", "Recency", "Frequency", "Monetary", "RFM_Score", "Segment"]]
            .sort_values("RFM_Score", ascending=False),
            use_container_width=True,
            height=400,
        )


def render_anomaly_scatter(df: pd.DataFrame) -> None:
    """Scatter plot highlighting anomalous transactions."""
    fig = px.scatter(
        df,
        x="Sales",
        y="Profit",
        color="Is_Anomaly",
        color_discrete_map={True: "red", False: "steelblue"},
        opacity=0.5,
        title="Anomaly Detection — Flagged Transactions",
        labels={"Sales": "Revenue ($)", "Profit": "Profit ($)", "Is_Anomaly": "Anomaly"},
    )
    fig.add_hline(y=0, line_dash="dash", line_color="gray")
    st.plotly_chart(fig, use_container_width=True)

    anomalies = df[df["Is_Anomaly"]]
    st.info(f"**{len(anomalies)}** transactions flagged as anomalous ({len(anomalies)/len(df)*100:.1f}%)")
    with st.expander("View Flagged Transactions"):
        st.dataframe(
            anomalies[["Order ID", "Product Name", "Category", "Sales", "Profit", "Discount"]].head(100),
            use_container_width=True,
        )


def render_association_rules_table(rules_df: pd.DataFrame) -> None:
    """Display top association rules with key metrics."""
    if rules_df.empty:
        st.warning("No association rules found with the current thresholds.")
        return

    display = rules_df.head(20).copy()
    display["antecedents"] = display["antecedents"].apply(lambda x: ", ".join(list(x)))
    display["consequents"] = display["consequents"].apply(lambda x: ", ".join(list(x)))

    st.dataframe(
        display[["antecedents", "consequents", "support", "confidence", "lift"]].style.format(
            {"support": "{:.3f}", "confidence": "{:.3f}", "lift": "{:.2f}"}
        ),
        use_container_width=True,
    )
