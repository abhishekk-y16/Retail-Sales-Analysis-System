"""Unit tests for src/feature_engine.py."""

import os
import pytest
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RAW_PATH = os.path.join(ROOT, "data", "01_raw", "superstore.csv")

from src.data_loader import load_and_clean_data
from src.feature_engine import add_temporal_features, compute_rfm, compute_association_rules, detect_anomalies


@pytest.fixture(scope="module")
def clean_df():
    return load_and_clean_data(RAW_PATH)


class TestTemporalFeatures:
    def test_columns_added(self, clean_df):
        df = add_temporal_features(clean_df)
        for col in ("Year", "Month", "Day", "DayOfWeek", "YearMonth"):
            assert col in df.columns

    def test_year_range(self, clean_df):
        df = add_temporal_features(clean_df)
        assert df["Year"].min() >= 2014
        assert df["Year"].max() <= 2017

    def test_month_range(self, clean_df):
        df = add_temporal_features(clean_df)
        assert df["Month"].between(1, 12).all()


class TestRFM:
    def test_rfm_columns(self, clean_df):
        rfm = compute_rfm(clean_df)
        for col in ("Customer ID", "Recency", "Frequency", "Monetary", "R_Score", "F_Score", "M_Score", "Segment"):
            assert col in rfm.columns

    def test_score_range(self, clean_df):
        rfm = compute_rfm(clean_df)
        assert rfm["R_Score"].between(1, 5).all()
        assert rfm["F_Score"].between(1, 5).all()
        assert rfm["M_Score"].between(1, 5).all()


class TestAssociationRules:
    def test_rules_structure(self, clean_df):
        rules = compute_association_rules(clean_df)
        for col in ("antecedents", "consequents", "support", "confidence", "lift"):
            assert col in rules.columns

    def test_confidence_range(self, clean_df):
        rules = compute_association_rules(clean_df)
        if not rules.empty:
            assert (rules["confidence"] >= 0.3).all()


class TestAnomalyDetection:
    def test_anomaly_column(self, clean_df):
        df = detect_anomalies(clean_df)
        assert "Is_Anomaly" in df.columns
        assert df["Is_Anomaly"].dtype == bool

    def test_contamination_ratio(self, clean_df):
        df = detect_anomalies(clean_df, contamination=0.05)
        ratio = df["Is_Anomaly"].mean()
        assert 0.01 < ratio < 0.15  # Reasonable range around 5%
