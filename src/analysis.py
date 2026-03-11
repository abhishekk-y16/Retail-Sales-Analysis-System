"""
Core Analytical Aggregation Functions.

Provides pre-computed groupby aggregations consumed by the EDA notebook
and the Streamlit dashboard layer.
"""

import pandas as pd


def monthly_sales_trend(df: pd.DataFrame) -> pd.DataFrame:
    """Monthly aggregate Sales and Profit over YearMonth."""
    out = (
        df.groupby("YearMonth", as_index=False)
        .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"))
        .sort_values("YearMonth")
    )
    return out


def category_sales(df: pd.DataFrame) -> pd.DataFrame:
    """Total Sales per Category, sorted descending."""
    return (
        df.groupby("Category", as_index=False)
        .agg(Sales=("Sales", "sum"))
        .sort_values("Sales", ascending=False)
    )


def top_subcategories(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """Top *n* Sub-Categories by total Sales."""
    return (
        df.groupby("Sub-Category", as_index=False)
        .agg(Sales=("Sales", "sum"))
        .sort_values("Sales", ascending=False)
        .head(n)
    )


def region_sales(df: pd.DataFrame) -> pd.DataFrame:
    """Total Sales per Region, sorted descending."""
    return (
        df.groupby("Region", as_index=False)
        .agg(Sales=("Sales", "sum"))
        .sort_values("Sales", ascending=False)
    )


def profit_vs_sales(df: pd.DataFrame) -> pd.DataFrame:
    """Return Sales, Profit, and Category for scatter-plot rendering."""
    return df[["Sales", "Profit", "Category"]].copy()


def profit_margin_by_category(df: pd.DataFrame) -> pd.DataFrame:
    """Profit margin (%) per Category: sum(Profit)/sum(Sales)*100."""
    agg = df.groupby("Category", as_index=False).agg(
        Sales=("Sales", "sum"), Profit=("Profit", "sum")
    )
    agg["Profit_Margin_Pct"] = (agg["Profit"] / agg["Sales"]) * 100
    return agg.sort_values("Profit_Margin_Pct", ascending=False)


def segment_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Sales and Profit aggregated by Customer Segment."""
    return (
        df.groupby("Segment", as_index=False)
        .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"))
        .sort_values("Sales", ascending=False)
    )


def state_level_sales(df: pd.DataFrame) -> pd.DataFrame:
    """Sales aggregated by State for choropleth mapping."""
    return (
        df.groupby("State", as_index=False)
        .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"))
        .sort_values("Sales", ascending=False)
    )


def discount_impact(df: pd.DataFrame) -> pd.DataFrame:
    """Group by Discount bucket and compute average Profit / Sales."""
    tmp = df.copy()
    tmp["Discount_Bucket"] = pd.cut(
        tmp["Discount"],
        bins=[-0.01, 0, 0.1, 0.2, 0.3, 0.5, 1.0],
        labels=["0%", "1-10%", "11-20%", "21-30%", "31-50%", "51-100%"],
    )
    return (
        tmp.groupby("Discount_Bucket", as_index=False, observed=True)
        .agg(
            Avg_Profit=("Profit", "mean"),
            Avg_Sales=("Sales", "mean"),
            Count=("Sales", "count"),
        )
    )
