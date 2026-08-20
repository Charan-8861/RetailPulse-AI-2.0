import pandas as pd
import numpy as np


# ============================================================
# HELPERS
# ============================================================

def _validate_dataframe(df):
    """
    Validate that the supplied object is a usable DataFrame.
    """

    if df is None:
        raise ValueError("Dataset is None.")

    if not isinstance(df, pd.DataFrame):
        raise TypeError("Dataset must be a pandas DataFrame.")

    if df.empty:
        raise ValueError("Dataset is empty.")


def _validate_column(df, column, column_label="Column"):
    """
    Ensure a configured column exists in the DataFrame.
    """

    if column is None:
        raise ValueError(
            f"{column_label} is not configured."
        )

    if str(column).strip().lower() == "none":
        raise ValueError(
            f"{column_label} is not configured."
        )

    if column not in df.columns:
        raise ValueError(
            f"{column_label} '{column}' was not found "
            "in the dataset."
        )


def _safe_optional_column(column):
    """
    Convert None-like values to Python None.
    """

    if column is None:
        return None

    if str(column).strip().lower() == "none":
        return None

    return column


# ============================================================
# PREPROCESS RETAIL DATA
# ============================================================

def preprocess_retail_data(
    df,
    date_column,
    sales_column=None,
    quantity_column=None
):
    """
    Prepare uploaded retail data for analytics and forecasting.

    Parameters
    ----------
    df : pandas.DataFrame
        Original uploaded retail dataset.

    date_column : str
        Column containing transaction/order dates.

    sales_column : str or None
        Optional Sales / Revenue column.

    quantity_column : str or None
        Optional Quantity / Demand column.

    Returns
    -------
    analysis_df : pandas.DataFrame
        Cleaned analysis-ready dataset.

    invalid_dates : int
        Number of rows removed because of invalid dates.
    """

    _validate_dataframe(df)

    _validate_column(
        df,
        date_column,
        "Date column"
    )


    sales_column = _safe_optional_column(
        sales_column
    )

    quantity_column = _safe_optional_column(
        quantity_column
    )


    if (
        sales_column is not None
        and
        sales_column not in df.columns
    ):
        raise ValueError(
            f"Sales column '{sales_column}' "
            "was not found in the dataset."
        )


    if (
        quantity_column is not None
        and
        quantity_column not in df.columns
    ):
        raise ValueError(
            f"Quantity column '{quantity_column}' "
            "was not found in the dataset."
        )


    analysis_df = df.copy()


    # ========================================================
    # CLEAN COLUMN NAMES
    # ========================================================

    analysis_df.columns = [
        str(column).strip()
        for column in analysis_df.columns
    ]


    # ========================================================
    # DATE CLEANING
    # ========================================================

    analysis_df[
        date_column
    ] = pd.to_datetime(
        analysis_df[
            date_column
        ],
        errors="coerce"
    )


    invalid_dates = int(
        analysis_df[
            date_column
        ]
        .isna()
        .sum()
    )


    analysis_df = (
        analysis_df
        .dropna(
            subset=[
                date_column
            ]
        )
        .copy()
    )


    # ========================================================
    # SALES CLEANING
    # ========================================================

    if sales_column is not None:

        analysis_df[
            sales_column
        ] = pd.to_numeric(
            analysis_df[
                sales_column
            ],
            errors="coerce"
        )


    # ========================================================
    # QUANTITY CLEANING
    # ========================================================

    if quantity_column is not None:

        analysis_df[
            quantity_column
        ] = pd.to_numeric(
            analysis_df[
                quantity_column
            ],
            errors="coerce"
        )


    # ========================================================
    # REMOVE COMPLETELY UNUSABLE FORECAST TARGET ROWS
    # ========================================================

    target_columns = []

    if sales_column is not None:
        target_columns.append(
            sales_column
        )

    if quantity_column is not None:
        target_columns.append(
            quantity_column
        )


    if target_columns:

        analysis_df = (
            analysis_df
            .dropna(
                subset=target_columns,
                how="all"
            )
            .copy()
        )


    # ========================================================
    # SORT BY DATE
    # ========================================================

    analysis_df = (
        analysis_df
        .sort_values(
            date_column
        )
        .reset_index(
            drop=True
        )
    )


    return (
        analysis_df,
        invalid_dates
    )


# ============================================================
# CREATE FORECASTING TIME SERIES
# ============================================================

def create_time_series(
    df,
    date_column,
    target_column,
    frequency="W"
):
    """
    Aggregate transactional retail data into a time series.

    Supported examples:
        W  -> Weekly
        ME -> Month-end
    """

    _validate_dataframe(df)

    _validate_column(
        df,
        date_column,
        "Date column"
    )

    _validate_column(
        df,
        target_column,
        "Forecast target"
    )


    data = df[
        [
            date_column,
            target_column
        ]
    ].copy()


    # ========================================================
    # DATE CONVERSION
    # ========================================================

    data[
        date_column
    ] = pd.to_datetime(
        data[
            date_column
        ],
        errors="coerce"
    )


    # ========================================================
    # NUMERIC TARGET CONVERSION
    # ========================================================

    data[
        target_column
    ] = pd.to_numeric(
        data[
            target_column
        ],
        errors="coerce"
    )


    # ========================================================
    # REMOVE INVALID RECORDS
    # ========================================================

    data = (
        data
        .dropna(
            subset=[
                date_column,
                target_column
            ]
        )
        .copy()
    )


    if data.empty:

        return pd.DataFrame(
            columns=[
                date_column,
                target_column
            ]
        )


    # ========================================================
    # SORT
    # ========================================================

    data = (
        data
        .sort_values(
            date_column
        )
    )


    # ========================================================
    # NORMALIZE FREQUENCY
    # ========================================================

    frequency_value = str(
        frequency
    ).strip()


    if frequency_value.upper() in {
        "M",
        "MONTHLY",
        "MONTH"
    }:
        frequency_value = "ME"


    elif frequency_value.upper() in {
        "WEEKLY",
        "WEEK"
    }:
        frequency_value = "W"


    # ========================================================
    # RESAMPLE
    # ========================================================

    data = (
        data
        .set_index(
            date_column
        )
    )


    time_series = (
        data
        .resample(
            frequency_value
        )[target_column]
        .sum(
            min_count=1
        )
        .reset_index()
    )


    # ========================================================
    # CLEAN RESULT
    # ========================================================

    time_series[
        target_column
    ] = pd.to_numeric(
        time_series[
            target_column
        ],
        errors="coerce"
    )


    time_series = (
        time_series
        .dropna(
            subset=[
                date_column,
                target_column
            ]
        )
        .sort_values(
            date_column
        )
        .reset_index(
            drop=True
        )
    )


    return time_series


# ============================================================
# MONTHLY SALES
# ============================================================

def create_monthly_sales(
    df,
    date_column,
    sales_column
):
    """
    Create monthly sales totals for analytics dashboards.
    """

    _validate_dataframe(df)

    _validate_column(
        df,
        date_column,
        "Date column"
    )

    _validate_column(
        df,
        sales_column,
        "Sales column"
    )


    monthly_df = df[
        [
            date_column,
            sales_column
        ]
    ].copy()


    # ========================================================
    # DATE
    # ========================================================

    monthly_df[
        date_column
    ] = pd.to_datetime(
        monthly_df[
            date_column
        ],
        errors="coerce"
    )


    # ========================================================
    # SALES
    # ========================================================

    monthly_df[
        sales_column
    ] = pd.to_numeric(
        monthly_df[
            sales_column
        ],
        errors="coerce"
    )


    # ========================================================
    # CLEAN
    # ========================================================

    monthly_df = (
        monthly_df
        .dropna(
            subset=[
                date_column,
                sales_column
            ]
        )
        .copy()
    )


    if monthly_df.empty:

        return pd.DataFrame(
            columns=[
                date_column,
                sales_column
            ]
        )


    # ========================================================
    # AGGREGATE MONTHLY
    # ========================================================

    monthly_sales = (
        monthly_df
        .set_index(
            date_column
        )
        .sort_index()
        .resample(
            "ME"
        )[sales_column]
        .sum(
            min_count=1
        )
        .reset_index()
    )


    monthly_sales = (
        monthly_sales
        .dropna(
            subset=[
                sales_column
            ]
        )
        .reset_index(
            drop=True
        )
    )


    return monthly_sales


# ============================================================
# GENERIC RETAIL AGGREGATION
# ============================================================

def aggregate_by_column(
    df,
    group_column,
    value_column
):
    """
    Aggregate a numeric retail value by product, category,
    region, customer, etc.
    """

    _validate_dataframe(df)

    _validate_column(
        df,
        group_column,
        "Grouping column"
    )

    _validate_column(
        df,
        value_column,
        "Value column"
    )


    data = df[
        [
            group_column,
            value_column
        ]
    ].copy()


    # ========================================================
    # NUMERIC VALUE
    # ========================================================

    data[
        value_column
    ] = pd.to_numeric(
        data[
            value_column
        ],
        errors="coerce"
    )


    # ========================================================
    # CLEAN
    # ========================================================

    data = (
        data
        .dropna(
            subset=[
                group_column,
                value_column
            ]
        )
        .copy()
    )


    if data.empty:

        return pd.DataFrame(
            columns=[
                group_column,
                value_column
            ]
        )


    # ========================================================
    # GROUP
    # ========================================================

    result = (
        data
        .groupby(
            group_column,
            as_index=False,
            dropna=False
        )[value_column]
        .sum()
        .sort_values(
            value_column,
            ascending=False
        )
        .reset_index(
            drop=True
        )
    )


    return result


# ============================================================
# FORECASTING DATA VALIDATION
# ============================================================

def validate_forecasting_data(
    df,
    date_column,
    target_column,
    minimum_rows=30
):
    """
    Check whether the selected retail dataset is suitable
    for time-series forecasting.

    Returns
    -------
    is_valid : bool

    messages : list[str]
    """

    messages = []


    # ========================================================
    # DATAFRAME VALIDATION
    # ========================================================

    if df is None:

        return (
            False,
            [
                "No dataset is available."
            ]
        )


    if not isinstance(
        df,
        pd.DataFrame
    ):

        return (
            False,
            [
                "The supplied dataset is not a valid dataframe."
            ]
        )


    if df.empty:

        return (
            False,
            [
                "The supplied dataset is empty."
            ]
        )


    # ========================================================
    # COLUMN EXISTENCE
    # ========================================================

    if (
        not date_column
        or
        date_column not in df.columns
    ):

        messages.append(
            f"Date column '{date_column}' was not found."
        )


    if (
        not target_column
        or
        target_column not in df.columns
    ):

        messages.append(
            f"Forecast target '{target_column}' "
            "was not found."
        )


    if messages:

        return (
            False,
            messages
        )


    # ========================================================
    # DATE VALIDATION
    # ========================================================

    valid_dates = pd.to_datetime(
        df[
            date_column
        ],
        errors="coerce"
    )


    valid_date_count = int(
        valid_dates
        .notna()
        .sum()
    )


    if valid_date_count == 0:

        messages.append(
            "The selected Date column does not "
            "contain usable dates."
        )


    # ========================================================
    # NUMERIC TARGET VALIDATION
    # ========================================================

    numeric_target = pd.to_numeric(
        df[
            target_column
        ],
        errors="coerce"
    )


    # Replace infinity values.
    numeric_target = numeric_target.replace(
        [
            np.inf,
            -np.inf
        ],
        np.nan
    )


    valid_numeric_count = int(
        numeric_target
        .notna()
        .sum()
    )


    if valid_numeric_count == 0:

        messages.append(
            "The forecasting target does not "
            "contain usable numeric values."
        )


    # ========================================================
    # USABLE ROWS
    # ========================================================

    usable_mask = (
        valid_dates.notna()
        &
        numeric_target.notna()
    )


    usable_rows = int(
        usable_mask.sum()
    )


    if usable_rows < minimum_rows:

        messages.append(
            f"Only {usable_rows} usable rows were found. "
            f"At least {minimum_rows} rows are recommended."
        )


    # ========================================================
    # TARGET VARIATION
    # ========================================================

    usable_target = (
        numeric_target[
            usable_mask
        ]
        .dropna()
    )


    if (
        not usable_target.empty
        and
        usable_target.nunique() <= 1
    ):

        messages.append(
            "The forecasting target has little or no variation."
        )


    # ========================================================
    # DATE RANGE
    # ========================================================

    usable_dates = (
        valid_dates[
            usable_mask
        ]
        .dropna()
    )


    if not usable_dates.empty:

        date_range_days = (
            usable_dates.max()
            -
            usable_dates.min()
        ).days


        if date_range_days < 30:

            messages.append(
                "The dataset covers less than 30 days. "
                "A longer historical period is recommended."
            )


    # ========================================================
    # UNIQUE DATE CHECK
    # ========================================================

    unique_dates = int(
        usable_dates.nunique()
    )


    if unique_dates < 10:

        messages.append(
            "Too few unique dates are available for "
            "reliable time-series forecasting."
        )


    # ========================================================
    # TARGET FINITE VALUES
    # ========================================================

    if not usable_target.empty:

        target_array = usable_target.to_numpy(
            dtype=float
        )


        if not np.isfinite(
            target_array
        ).all():

            messages.append(
                "The forecasting target contains infinite "
                "or invalid numeric values."
            )


    # ========================================================
    # RESULT
    # ========================================================

    return (
        len(messages) == 0,
        messages
    )