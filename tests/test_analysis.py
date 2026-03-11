"""Unit tests for src/analysis.py."""

import os
import pytest
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RAW_PATH = os.path.join(ROOT, "data", "01_raw", "superstore.csv")

from src.data_loader import load_and_clean_data
from src.feature_engine import add_temporal_features
from src import analysis


@pytest.fixture(scope="module")
def df():
    raw = load_and_clean_data(RAW_PATH)
    return add_temporal_features(raw)


class TestMonthlySalesTrend:
    def test_columns(self, df):
        result = analysis.monthly_sales_trend(df)
        assert "YearMonth" in result.columns
        assert "Sales" in result.columns

    def test_sorted(self, df):
        result = analysis.monthly_sales_trend(df)
        assert list(result["YearMonth"]) == sorted(result["YearMonth"])


class TestCategorySales:
    def test_three_categories(self, df):
        result = analysis.category_sales(df)
        assert len(result) == 3

    def test_descending(self, df):
        result = analysis.category_sales(df)
        assert result["Sales"].is_monotonic_decreasing


class TestTopSubcategories:
    def test_limit(self, df):
        result = analysis.top_subcategories(df, n=5)
        assert len(result) <= 5

    def test_default_ten(self, df):
        result = analysis.top_subcategories(df)
        assert len(result) <= 10


class TestRegionSales:
    def test_four_regions(self, df):
        result = analysis.region_sales(df)
        assert len(result) == 4


class TestProfitMargin:
    def test_margin_range(self, df):
        result = analysis.profit_margin_by_category(df)
        # Margins should be between -100% and +100% for this dataset
        assert result["Profit_Margin_Pct"].between(-100, 100).all()


class TestDiscountImpact:
    def test_buckets(self, df):
        result = analysis.discount_impact(df)
        assert "Discount_Bucket" in result.columns
        assert "Avg_Profit" in result.columns
