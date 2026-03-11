"""
Retail Sales Dashboard — Main Streamlit Application.

Entry point: ``streamlit run dashboard/app.py``
"""

import sys
import os

# Ensure the project root is on sys.path so ``src`` imports work when
# Streamlit is launched from the project root directory.
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

import streamlit as st
import pandas as pd

from src.data_loader import load_and_clean_data
from src.feature_engine import add_temporal_features, compute_rfm, compute_association_rules, detect_anomalies
from src import analysis
from dashboard.components import (
    render_kpi_cards,
    render_monthly_trend,
    render_category_bar,
    render_top_products,
    render_region_bar,
    render_profit_vs_sales_scatter,
    render_discount_impact,
    render_profit_margin_by_category,
    render_rfm_summary,
    render_anomaly_scatter,
    render_association_rules_table,
)

# ── Page configuration ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="Retail Sales Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    /* KPI card styling */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #667eea11, #764ba211);
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    div[data-testid="stMetric"] label {
        font-size: 0.85rem !important;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        font-size: 1.8rem !important;
        font-weight: 700;
    }
    /* Tab styling */
    button[data-baseweb="tab"] {
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ── Data Loading (cached) ───────────────────────────────────────────────────
DATA_PATH = os.path.join(_PROJECT_ROOT, "data", "01_raw", "superstore.csv")


@st.cache_data(show_spinner="Loading and cleaning data…")
def get_data() -> pd.DataFrame:
    df = load_and_clean_data(DATA_PATH)
    df = add_temporal_features(df)
    return df


@st.cache_data(show_spinner="Computing RFM segmentation…")
def get_rfm(df: pd.DataFrame) -> pd.DataFrame:
    return compute_rfm(df)


@st.cache_data(show_spinner="Mining association rules…")
def get_rules(df: pd.DataFrame) -> pd.DataFrame:
    return compute_association_rules(df)


@st.cache_data(show_spinner="Detecting anomalies…")
def get_anomalies(df: pd.DataFrame) -> pd.DataFrame:
    return detect_anomalies(df)


# ── Load full dataset ────────────────────────────────────────────────────────
df_full = get_data()

# ── Sidebar Filters ─────────────────────────────────────────────────────────
st.sidebar.image("https://img.icons8.com/fluency/96/shopping-cart.png", width=64)
st.sidebar.title("🔎 Filters")

regions = st.sidebar.multiselect(
    "Region",
    options=sorted(df_full["Region"].unique()),
    default=sorted(df_full["Region"].unique()),
)

categories = st.sidebar.multiselect(
    "Category",
    options=sorted(df_full["Category"].unique()),
    default=sorted(df_full["Category"].unique()),
)

segments = st.sidebar.multiselect(
    "Segment",
    options=sorted(df_full["Segment"].unique()),
    default=sorted(df_full["Segment"].unique()),
)

year_range = st.sidebar.slider(
    "Year Range",
    min_value=int(df_full["Year"].min()),
    max_value=int(df_full["Year"].max()),
    value=(int(df_full["Year"].min()), int(df_full["Year"].max())),
)

# ── Apply filters ────────────────────────────────────────────────────────────
df = df_full[
    (df_full["Region"].isin(regions))
    & (df_full["Category"].isin(categories))
    & (df_full["Segment"].isin(segments))
    & (df_full["Year"].between(*year_range))
]

if df.empty:
    st.warning("No data matches the current filter selection. Adjust the sidebar filters.")
    st.stop()

# ── Title ────────────────────────────────────────────────────────────────────
st.title("📊 Interactive Retail Sales Dashboard")
st.caption("Enterprise-grade analytics powered by Streamlit · Plotly · Pandas")

# ── Row 1: KPI Cards ────────────────────────────────────────────────────────
total_sales = df["Sales"].sum()
total_profit = df["Profit"].sum()
profit_margin = (total_profit / total_sales) * 100 if total_sales else 0
order_count = df["Order ID"].nunique()
render_kpi_cards(total_sales, total_profit, profit_margin, order_count)

st.divider()

# ── Row 2: Monthly Trend + Category ─────────────────────────────────────────
col_left, col_right = st.columns(2)
with col_left:
    st.subheader("Monthly Sales Trend")
    monthly = analysis.monthly_sales_trend(df)
    render_monthly_trend(monthly)

with col_right:
    st.subheader("Category Performance")
    cat = analysis.category_sales(df)
    render_category_bar(cat)

# ── Row 3: Top Products + Region ────────────────────────────────────────────
col_left2, col_right2 = st.columns(2)
with col_left2:
    st.subheader("Top 10 Sub-Categories")
    top = analysis.top_subcategories(df, n=10)
    render_top_products(top)

with col_right2:
    st.subheader("Regional Performance")
    reg = analysis.region_sales(df)
    render_region_bar(reg)

# ── Row 4: Profit vs Sales ──────────────────────────────────────────────────
st.divider()
st.subheader("Profit vs Sales Analysis")

col_scatter, col_margin = st.columns([2, 1])
with col_scatter:
    pvs = analysis.profit_vs_sales(df)
    render_profit_vs_sales_scatter(pvs)

with col_margin:
    margin = analysis.profit_margin_by_category(df)
    render_profit_margin_by_category(margin)
    disc = analysis.discount_impact(df)
    render_discount_impact(disc)

# ── Row 5: Advanced Analytics Tabs ──────────────────────────────────────────
st.divider()
st.subheader("Advanced Analytics")

tab_rfm, tab_rules, tab_anomaly = st.tabs(
    ["🧑‍🤝‍🧑 RFM Customer Segmentation", "🛒 Association Rules", "⚠️ Anomaly Detection"]
)

with tab_rfm:
    rfm_df = get_rfm(df_full)  # RFM uses full dataset (not filtered)
    render_rfm_summary(rfm_df)

with tab_rules:
    st.markdown("**Product co-purchase patterns** via FP-Growth association rule mining.")
    rules_df = get_rules(df_full)
    render_association_rules_table(rules_df)

with tab_anomaly:
    anomaly_df = get_anomalies(df)
    render_anomaly_scatter(anomaly_df)

# ── Footer ───────────────────────────────────────────────────────────────────
st.divider()
st.caption("Data source: Superstore Sales Dataset · Built with Streamlit & Plotly")
