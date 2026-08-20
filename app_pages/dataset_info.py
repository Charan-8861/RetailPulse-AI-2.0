import streamlit as st
import pandas as pd
import numpy as np


# ============================================================
# HELPERS
# ============================================================

def safe_column(value):
    """
    Convert None-like values into Python None.
    """

    if value is None:
        return None

    if str(value).strip().lower() == "none":
        return None

    return value


def calculate_memory_usage(df):
    """
    Calculate approximate dataframe memory usage in MB.
    """

    if df is None:
        return 0.0

    if not isinstance(df, pd.DataFrame):
        return 0.0

    try:

        memory_bytes = (
            df.memory_usage(
                deep=True
            )
            .sum()
        )

        return (
            memory_bytes
            /
            (1024 ** 2)
        )

    except Exception:

        return 0.0


def column_exists(df, column):
    """
    Check whether a configured column exists.
    """

    return (
        column is not None
        and
        column in df.columns
    )


def build_column_information(df):
    """
    Generate detailed information for each column.
    """

    rows = []

    total_rows = len(df)

    for column in df.columns:

        series = df[column]

        missing = int(
            series.isna().sum()
        )

        if total_rows > 0:

            missing_pct = (
                missing
                /
                total_rows
            ) * 100

        else:

            missing_pct = 0.0


        unique_values = int(
            series.nunique(
                dropna=True
            )
        )


        rows.append(
            {
                "Column":
                    str(column),

                "Data Type":
                    str(series.dtype),

                "Missing":
                    missing,

                "Missing (%)":
                    missing_pct,

                "Unique Values":
                    unique_values
            }
        )


    return pd.DataFrame(
        rows
    )


def calculate_quality_score(
    df,
    mappings
):
    """
    Calculate a simple RetailPulse data-quality score.
    """

    if (
        df is None
        or
        not isinstance(
            df,
            pd.DataFrame
        )
        or
        df.empty
    ):

        return 0


    rows = len(df)

    columns = len(
        df.columns
    )


    total_cells = (
        rows
        *
        columns
    )


    missing_values = int(
        df
        .isna()
        .sum()
        .sum()
    )


    duplicate_rows = int(
        df
        .duplicated()
        .sum()
    )


    # --------------------------------------------------------
    # MISSING VALUE RATE
    # --------------------------------------------------------

    if total_cells > 0:

        missing_rate = (
            missing_values
            /
            total_cells
        )

    else:

        missing_rate = 0


    # --------------------------------------------------------
    # DUPLICATE RATE
    # --------------------------------------------------------

    if rows > 0:

        duplicate_rate = (
            duplicate_rows
            /
            rows
        )

    else:

        duplicate_rate = 0


    # ========================================================
    # SCORE
    # ========================================================

    quality_score = 100.0


    # Missing values can reduce score by maximum 45 points.
    quality_score -= min(
        missing_rate * 100,
        45
    )


    # Duplicates can reduce score by maximum 25 points.
    quality_score -= min(
        duplicate_rate * 100,
        25
    )


    # --------------------------------------------------------
    # REQUIRED FORECASTING CONFIGURATION
    # --------------------------------------------------------

    date_mapping = mappings.get(
        "Date"
    )


    sales_mapping = mappings.get(
        "Sales / Revenue"
    )


    quantity_mapping = mappings.get(
        "Quantity / Demand"
    )


    if not column_exists(
        df,
        date_mapping
    ):

        quality_score -= 15


    if (
        not column_exists(
            df,
            sales_mapping
        )
        and
        not column_exists(
            df,
            quantity_mapping
        )
    ):

        quality_score -= 15


    # --------------------------------------------------------
    # PROTECT RANGE
    # --------------------------------------------------------

    quality_score = max(
        0,
        min(
            100,
            quality_score
        )
    )


    return int(
        round(
            quality_score
        )
    )


# ============================================================
# DATASET INFORMATION PAGE
# ============================================================

def show_dataset_info():

    # ========================================================
    # HEADER
    # ========================================================

    st.title(
        "⚙️ Dataset Information"
    )

    st.caption(
        "Review dataset structure, column mappings, "
        "data quality and descriptive statistics."
    )


    # ========================================================
    # DATASET CHECK
    # ========================================================

    if not st.session_state.get(
        "dataset_configured",
        False
    ):

        st.warning(
            "No dataset has been configured.\n\n"
            "Open **📁 Data Upload**, upload your dataset and "
            "confirm the column configuration first."
        )

        return


    analysis_df = st.session_state.get(
        "analysis_df"
    )


    if analysis_df is None:

        st.warning(
            "The processed dataset is unavailable.\n\n"
            "Please configure the dataset again from "
            "**📁 Data Upload**."
        )

        return


    if not isinstance(
        analysis_df,
        pd.DataFrame
    ):

        st.error(
            "The active analysis dataset is not a valid dataframe."
        )

        return


    if analysis_df.empty:

        st.warning(
            "The configured dataset contains no usable records."
        )

        return


    analysis_df = (
        analysis_df
        .copy()
    )


    # ========================================================
    # RAW DATASET
    # ========================================================

    raw_df = st.session_state.get(
        "retail_df"
    )


    if (
        raw_df is None
        or
        not isinstance(
            raw_df,
            pd.DataFrame
        )
    ):

        raw_df = (
            analysis_df
            .copy()
        )

    else:

        raw_df = (
            raw_df
            .copy()
        )


    # ========================================================
    # BASIC INFORMATION
    # ========================================================

    st.subheader(
        "📌 Dataset Overview"
    )


    rows = len(
        analysis_df
    )


    columns = len(
        analysis_df.columns
    )


    missing_values = int(
        analysis_df
        .isna()
        .sum()
        .sum()
    )


    duplicate_rows = int(
        analysis_df
        .duplicated()
        .sum()
    )


    memory_mb = calculate_memory_usage(
        analysis_df
    )


    c1, c2, c3, c4, c5 = st.columns(
        5
    )


    with c1:

        st.metric(
            "Rows",
            f"{rows:,}"
        )


    with c2:

        st.metric(
            "Columns",
            f"{columns:,}"
        )


    with c3:

        st.metric(
            "Missing Values",
            f"{missing_values:,}"
        )


    with c4:

        st.metric(
            "Duplicate Rows",
            f"{duplicate_rows:,}"
        )


    with c5:

        st.metric(
            "Memory",
            f"{memory_mb:.2f} MB"
        )


    # ========================================================
    # SOURCE INFORMATION
    # ========================================================

    st.divider()

    st.subheader(
        "📁 Source Information"
    )


    file_name = (
        st.session_state.get(
            "current_file_name"
        )
        or
        "Unknown"
    )


    sheet_name = (
        st.session_state.get(
            "current_sheet_name"
        )
    )


    source1, source2, source3 = st.columns(
        3
    )


    with source1:

        st.metric(
            "Source File",
            file_name
        )


    with source2:

        st.metric(
            "Worksheet",
            (
                sheet_name
                if sheet_name
                else "CSV / Not Applicable"
            )
        )


    with source3:

        st.metric(
            "Configured",
            "Yes"
        )


    # ========================================================
    # RAW VS ANALYSIS DATASET
    # ========================================================

    st.divider()

    st.subheader(
        "🔄 Raw vs Analysis Dataset"
    )


    raw_rows = len(
        raw_df
    )


    analysis_rows = len(
        analysis_df
    )


    removed_rows = max(
        raw_rows
        -
        analysis_rows,
        0
    )


    r1, r2, r3 = st.columns(
        3
    )


    with r1:

        st.metric(
            "Original Rows",
            f"{raw_rows:,}"
        )


    with r2:

        st.metric(
            "Analysis Rows",
            f"{analysis_rows:,}"
        )


    with r3:

        st.metric(
            "Rows Removed",
            f"{removed_rows:,}"
        )


    if removed_rows > 0:

        if raw_rows > 0:

            removed_percentage = (
                removed_rows
                /
                raw_rows
            ) * 100

        else:

            removed_percentage = 0


        st.info(
            f"{removed_rows:,} row(s) "
            f"({removed_percentage:.2f}%) "
            "were removed during preprocessing."
        )

    else:

        st.success(
            "No rows were removed during preprocessing."
        )


    # ========================================================
    # ACTIVE COLUMN MAPPINGS
    # ========================================================

    st.divider()

    st.subheader(
        "🧠 Active Retail Field Mapping"
    )


    mappings = {

        "Date":
            safe_column(
                st.session_state.get(
                    "date_column"
                )
            ),

        "Sales / Revenue":
            safe_column(
                st.session_state.get(
                    "sales_column"
                )
            ),

        "Quantity / Demand":
            safe_column(
                st.session_state.get(
                    "quantity_column"
                )
            ),

        "Product":
            safe_column(
                st.session_state.get(
                    "product_column"
                )
            ),

        "Category":
            safe_column(
                st.session_state.get(
                    "category_column"
                )
            ),

        "Region":
            safe_column(
                st.session_state.get(
                    "region_column"
                )
            ),

        "Customer":
            safe_column(
                st.session_state.get(
                    "customer_column"
                )
            )
    }


    mapping_rows = []


    for (
        field,
        mapped_column
    ) in mappings.items():

        if mapped_column is None:

            status = (
                "Required / Missing"
                if field in [
                    "Date"
                ]
                else "Optional / Missing"
            )

            display_column = (
                "Not Configured"
            )

        elif mapped_column in analysis_df.columns:

            status = (
                "Configured"
            )

            display_column = (
                mapped_column
            )

        else:

            status = (
                "Mapped Column Missing"
            )

            display_column = (
                mapped_column
            )


        mapping_rows.append(
            {
                "Retail Field":
                    field,

                "Mapped Dataset Column":
                    display_column,

                "Status":
                    status
            }
        )


    mapping_df = pd.DataFrame(
        mapping_rows
    )


    st.dataframe(
        mapping_df,
        use_container_width=True,
        hide_index=True
    )


    # ========================================================
    # FORECAST TARGET MAPPING CHECK
    # ========================================================

    sales_mapping = mappings[
        "Sales / Revenue"
    ]


    quantity_mapping = mappings[
        "Quantity / Demand"
    ]


    if (
        not column_exists(
            analysis_df,
            sales_mapping
        )
        and
        not column_exists(
            analysis_df,
            quantity_mapping
        )
    ):

        st.warning(
            "No valid Sales or Quantity forecasting target "
            "is currently mapped."
        )


    # ========================================================
    # DATASET PREVIEW
    # ========================================================

    st.divider()

    st.subheader(
        "👀 Dataset Preview"
    )


    max_preview_rows = min(
        100,
        len(
            analysis_df
        )
    )


    if max_preview_rows <= 0:

        st.info(
            "No rows are available for preview."
        )

    else:

        min_preview_rows = min(
            5,
            max_preview_rows
        )


        default_preview_rows = min(
            20,
            max_preview_rows
        )


        if max_preview_rows == 1:

            preview_rows = 1

        else:

            preview_rows = st.slider(
                "Number of rows to preview",
                min_value=min_preview_rows,
                max_value=max_preview_rows,
                value=max(
                    min_preview_rows,
                    default_preview_rows
                ),
                key="dataset_preview_rows"
            )


        st.dataframe(
            analysis_df.head(
                preview_rows
            ),
            use_container_width=True
        )


    # ========================================================
    # COLUMN INFORMATION
    # ========================================================

    st.divider()

    st.subheader(
        "🔎 Column Information"
    )


    column_info_df = (
        build_column_information(
            analysis_df
        )
    )


    if column_info_df.empty:

        st.info(
            "No column information is available."
        )

    else:

        st.dataframe(
            column_info_df.style.format(
                {
                    "Missing (%)":
                        "{:.2f}%"
                }
            ),
            use_container_width=True,
            hide_index=True
        )


    # ========================================================
    # DATA TYPE DISTRIBUTION
    # ========================================================

    st.divider()

    st.subheader(
        "🧬 Data Type Distribution"
    )


    dtype_counts = (
        analysis_df
        .dtypes
        .astype(str)
        .value_counts()
        .rename_axis(
            "Data Type"
        )
        .reset_index(
            name="Column Count"
        )
    )


    if dtype_counts.empty:

        st.info(
            "No data types are available."
        )

    else:

        d1, d2 = st.columns(
            [1, 2],
            gap="large"
        )


        with d1:

            st.dataframe(
                dtype_counts,
                use_container_width=True,
                hide_index=True
            )


        with d2:

            st.bar_chart(
                dtype_counts,
                x="Data Type",
                y="Column Count",
                use_container_width=True
            )


    # ========================================================
    # MISSING VALUE ANALYSIS
    # ========================================================

    st.divider()

    st.subheader(
        "⚠️ Missing Value Analysis"
    )


    missing_df = (
        analysis_df
        .isna()
        .sum()
        .rename_axis(
            "Column"
        )
        .reset_index(
            name="Missing Values"
        )
    )


    if len(
        analysis_df
    ) > 0:

        missing_df[
            "Missing (%)"
        ] = (
            missing_df[
                "Missing Values"
            ]
            /
            len(
                analysis_df
            )
            *
            100
        )

    else:

        missing_df[
            "Missing (%)"
        ] = 0.0


    missing_df = (
        missing_df[
            missing_df[
                "Missing Values"
            ] > 0
        ]
        .sort_values(
            "Missing Values",
            ascending=False
        )
        .reset_index(
            drop=True
        )
    )


    if missing_df.empty:

        st.success(
            "No missing values were detected in the "
            "analysis dataset."
        )

    else:

        st.dataframe(
            missing_df.style.format(
                {
                    "Missing (%)":
                        "{:.2f}%"
                }
            ),
            use_container_width=True,
            hide_index=True
        )


        high_missing = (
            missing_df[
                missing_df[
                    "Missing (%)"
                ] >= 30
            ]
        )


        if not high_missing.empty:

            st.warning(
                "One or more columns contain at least 30% "
                "missing values. These fields should be reviewed "
                "before using them for advanced modeling."
            )


    # ========================================================
    # DUPLICATE ANALYSIS
    # ========================================================

    st.divider()

    st.subheader(
        "📑 Duplicate Analysis"
    )


    if duplicate_rows == 0:

        st.success(
            "No duplicate rows were detected."
        )

    else:

        if len(
            analysis_df
        ) > 0:

            duplicate_percentage = (
                duplicate_rows
                /
                len(
                    analysis_df
                )
            ) * 100

        else:

            duplicate_percentage = 0


        st.warning(
            f"{duplicate_rows:,} duplicate row(s) were detected, "
            f"representing approximately "
            f"{duplicate_percentage:.2f}% of the dataset."
        )


        with st.expander(
            "View Duplicate Records",
            expanded=False
        ):

            duplicates = (
                analysis_df[
                    analysis_df
                    .duplicated(
                        keep=False
                    )
                ]
                .copy()
            )


            st.dataframe(
                duplicates.head(
                    100
                ),
                use_container_width=True
            )


    # ========================================================
    # NUMERICAL STATISTICS
    # ========================================================

    st.divider()

    st.subheader(
        "📊 Numerical Statistics"
    )


    numeric_df = (
        analysis_df
        .select_dtypes(
            include=[
                np.number
            ]
        )
    )


    if numeric_df.empty:

        st.info(
            "No numerical columns are available."
        )

    else:

        try:

            numeric_stats = (
                numeric_df
                .describe()
                .T
                .reset_index()
                .rename(
                    columns={
                        "index":
                            "Column"
                    }
                )
            )


            st.dataframe(
                numeric_stats,
                use_container_width=True,
                hide_index=True
            )

        except Exception as e:

            st.info(
                "Unable to calculate numerical statistics."
            )

            st.caption(
                str(e)
            )


    # ========================================================
    # CATEGORICAL STATISTICS
    # ========================================================

    st.divider()

    st.subheader(
        "🏷️ Categorical Overview"
    )


    categorical_columns = (
        analysis_df
        .select_dtypes(
            include=[
                "object",
                "category",
                "string"
            ]
        )
        .columns
        .tolist()
    )


    if not categorical_columns:

        st.info(
            "No categorical columns were detected."
        )

    else:

        categorical_rows = []


        for column in categorical_columns:

            series = (
                analysis_df[
                    column
                ]
            )


            non_null = (
                series
                .dropna()
            )


            unique_values = int(
                series.nunique(
                    dropna=True
                )
            )


            if not non_null.empty:

                mode_values = (
                    non_null
                    .mode()
                )


                if not mode_values.empty:

                    most_common = (
                        mode_values.iloc[0]
                    )


                    frequency = int(
                        (
                            non_null
                            ==
                            most_common
                        )
                        .sum()
                    )

                else:

                    most_common = (
                        "N/A"
                    )

                    frequency = 0

            else:

                most_common = (
                    "N/A"
                )

                frequency = 0


            categorical_rows.append(
                {
                    "Column":
                        column,

                    "Unique Values":
                        unique_values,

                    "Most Common Value":
                        str(
                            most_common
                        ),

                    "Frequency":
                        frequency
                }
            )


        categorical_df = pd.DataFrame(
            categorical_rows
        )


        st.dataframe(
            categorical_df,
            use_container_width=True,
            hide_index=True
        )


    # ========================================================
    # DATA QUALITY SCORE
    # ========================================================

    st.divider()

    st.subheader(
        "🛡️ Data Quality Score"
    )


    quality_score = (
        calculate_quality_score(
            analysis_df,
            mappings
        )
    )


    q1, q2 = st.columns(
        [1, 3]
    )


    with q1:

        st.metric(
            "Quality Score",
            f"{quality_score}/100"
        )


    with q2:

        st.progress(
            quality_score
        )


        if quality_score >= 90:

            st.success(
                "Excellent dataset quality."
            )

        elif quality_score >= 75:

            st.info(
                "Good dataset quality with minor issues."
            )

        elif quality_score >= 60:

            st.warning(
                "Moderate dataset quality. Review missing "
                "values, duplicates and field mappings."
            )

        else:

            st.error(
                "Dataset quality requires attention before "
                "advanced analysis."
            )


    # ========================================================
    # QUALITY EXPLANATION
    # ========================================================

    with st.expander(
        "How is the quality score calculated?",
        expanded=False
    ):

        st.write(
            "The RetailPulse data-quality score considers:"
        )

        st.write(
            "• Missing-value rate"
        )

        st.write(
            "• Duplicate-row rate"
        )

        st.write(
            "• Availability of a valid Date field"
        )

        st.write(
            "• Availability of at least one forecasting "
            "target: Sales or Quantity"
        )

        st.caption(
            "The score is intended as a quick diagnostic "
            "indicator rather than a formal statistical "
            "data-quality certification."
        )


    # ========================================================
    # FORECASTING READINESS
    # ========================================================

    st.divider()

    st.subheader(
        "🤖 Forecasting Readiness"
    )


    date_ready = column_exists(
        analysis_df,
        mappings[
            "Date"
        ]
    )


    sales_ready = column_exists(
        analysis_df,
        mappings[
            "Sales / Revenue"
        ]
    )


    quantity_ready = column_exists(
        analysis_df,
        mappings[
            "Quantity / Demand"
        ]
    )


    forecast_target_ready = (
        sales_ready
        or
        quantity_ready
    )


    f1, f2, f3 = st.columns(
        3
    )


    with f1:

        st.metric(
            "Date Field",
            (
                "Ready"
                if date_ready
                else "Missing"
            )
        )


    with f2:

        st.metric(
            "Forecast Target",
            (
                "Ready"
                if forecast_target_ready
                else "Missing"
            )
        )


    with f3:

        st.metric(
            "Overall Status",
            (
                "Ready"
                if (
                    date_ready
                    and
                    forecast_target_ready
                )
                else "Not Ready"
            )
        )


    if (
        date_ready
        and
        forecast_target_ready
    ):

        st.success(
            "The configured dataset contains the minimum "
            "field mappings required for forecasting."
        )

    else:

        st.warning(
            "Forecasting requires a valid Date column and at "
            "least one target column: Sales or Quantity."
        )


    # ========================================================
    # DOWNLOAD CLEANED DATASET
    # ========================================================

    st.divider()

    st.subheader(
        "⬇️ Export Analysis Dataset"
    )


    try:

        csv_data = (
            analysis_df
            .to_csv(
                index=False
            )
            .encode(
                "utf-8"
            )
        )


        st.download_button(
            label="⬇️ Download Processed Dataset",
            data=csv_data,
            file_name="retailpulse_processed_data.csv",
            mime="text/csv",
            key="download_processed_dataset"
        )

    except Exception as e:

        st.warning(
            "The processed dataset could not be prepared "
            "for download."
        )

        st.caption(
            str(e)
        )


    # ========================================================
    # FOOTER
    # ========================================================

    st.divider()

    st.caption(
        "Dataset information is calculated from the currently "
        "configured analysis dataset used by RetailPulse AI."
    )