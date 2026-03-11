"""
Data Loading, Schema Validation, and Cleaning Pipeline.

Handles CSV ingestion, Pandera schema enforcement, and deterministic
data cleansing for the Superstore retail dataset.
"""

import os
import pandas as pd
import pandera as pa
from pandera import Column, Check, DataFrameSchema


# ---------------------------------------------------------------------------
# Pandera Schema Definition
# ---------------------------------------------------------------------------

SUPERSTORE_SCHEMA = DataFrameSchema(
    {
        "Row ID": Column(int, nullable=False),
        "Order ID": Column(str, nullable=False),
        "Order Date": Column(str, nullable=False),   # validated pre-conversion
        "Ship Date": Column(str, nullable=False),
        "Ship Mode": Column(
            str,
            Check.isin(["First Class", "Second Class", "Standard Class", "Same Day"]),
            nullable=False,
        ),
        "Customer ID": Column(str, nullable=False),
        "Customer Name": Column(str, nullable=False),
        "Segment": Column(
            str,
            Check.isin(["Consumer", "Corporate", "Home Office"]),
            nullable=False,
        ),
        "Country": Column(str, nullable=False),
        "City": Column(str, nullable=False),
        "State": Column(str, nullable=False),
        "Postal Code": Column(nullable=True),  # some entries can be missing
        "Region": Column(
            str,
            Check.isin(["East", "West", "South", "Central"]),
            nullable=False,
        ),
        "Product ID": Column(str, nullable=False),
        "Category": Column(
            str,
            Check.isin(["Furniture", "Office Supplies", "Technology"]),
            nullable=False,
        ),
        "Sub-Category": Column(str, nullable=False),
        "Product Name": Column(str, nullable=False),
        "Sales": Column(float, Check.greater_than_or_equal_to(0), nullable=False),
        "Quantity": Column(int, Check.greater_than(0), nullable=False),
        "Discount": Column(
            float,
            [Check.greater_than_or_equal_to(0), Check.less_than_or_equal_to(1)],
            nullable=False,
        ),
        "Profit": Column(float, nullable=False),  # can be negative
    },
    coerce=True,
)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def load_raw_data(path: str) -> pd.DataFrame:
    """Load the Superstore CSV from *path*, handling encoding edge-cases."""
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Data file not found: {path}")
    df = pd.read_csv(path, encoding="latin-1")
    return df


def validate_schema(df: pd.DataFrame) -> pd.DataFrame:
    """Validate *df* against the Pandera schema contract.

    Raises ``pandera.errors.SchemaError`` on violations.
    """
    return SUPERSTORE_SCHEMA.validate(df, lazy=True)


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Apply deterministic cleaning steps.

    1. Drop rows with missing critical fields.
    2. Remove duplicate rows.
    3. Convert date columns to datetime.
    4. Normalise smart-quote characters in Product Name.
    """
    df = df.copy()

    # 1. Drop missing values
    df.dropna(subset=["Order Date", "Ship Date", "Sales", "Profit", "Region", "Category"], inplace=True)

    # 2. Remove duplicates
    df.drop_duplicates(inplace=True)

    # 3. Datetime conversion (MM/DD/YYYY)
    df["Order Date"] = pd.to_datetime(df["Order Date"], format="%m/%d/%Y")
    df["Ship Date"] = pd.to_datetime(df["Ship Date"], format="%m/%d/%Y")

    # 4. Normalise smart quotes (U+2018, U+2019) → ASCII apostrophe
    df["Product Name"] = (
        df["Product Name"]
        .str.replace("\u2018", "'", regex=False)
        .str.replace("\u2019", "'", regex=False)
        .str.replace("\u201c", '"', regex=False)
        .str.replace("\u201d", '"', regex=False)
    )

    df.reset_index(drop=True, inplace=True)
    return df


def load_and_clean_data(path: str) -> pd.DataFrame:
    """End-to-end pipeline: load → validate → clean → return."""
    df = load_raw_data(path)
    df = validate_schema(df)
    df = clean_data(df)
    return df
