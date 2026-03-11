"""Unit tests for src/data_loader.py."""

import os
import pytest
import pandas as pd
import pandera

# Resolve the project root (two levels up from tests/)
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RAW_PATH = os.path.join(ROOT, "data", "01_raw", "superstore.csv")

from src.data_loader import load_raw_data, validate_schema, clean_data, load_and_clean_data


class TestLoadRawData:
    def test_loads_without_error(self):
        df = load_raw_data(RAW_PATH)
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 9000

    def test_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            load_raw_data("/nonexistent/path.csv")


class TestValidateSchema:
    def test_valid_data_passes(self):
        df = load_raw_data(RAW_PATH)
        validated = validate_schema(df)
        assert len(validated) == len(df)

    def test_bad_region_fails(self):
        df = load_raw_data(RAW_PATH).head(5).copy()
        df.loc[0, "Region"] = "Antarctica"
        with pytest.raises(pandera.errors.SchemaErrors):
            validate_schema(df)

    def test_negative_quantity_fails(self):
        df = load_raw_data(RAW_PATH).head(5).copy()
        df.loc[0, "Quantity"] = -1
        with pytest.raises(pandera.errors.SchemaErrors):
            validate_schema(df)


class TestCleanData:
    def test_removes_duplicates(self):
        df = load_raw_data(RAW_PATH)
        # Manually duplicate
        df_dup = pd.concat([df, df.head(3)], ignore_index=True)
        cleaned = clean_data(df_dup)
        assert len(cleaned) <= len(df)

    def test_datetime_conversion(self):
        df = load_raw_data(RAW_PATH)
        cleaned = clean_data(df)
        assert pd.api.types.is_datetime64_any_dtype(cleaned["Order Date"])
        assert pd.api.types.is_datetime64_any_dtype(cleaned["Ship Date"])


class TestEndToEnd:
    def test_load_and_clean(self):
        df = load_and_clean_data(RAW_PATH)
        assert len(df) > 9000
        assert pd.api.types.is_datetime64_any_dtype(df["Order Date"])
