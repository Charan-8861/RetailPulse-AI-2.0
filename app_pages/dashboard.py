import streamlit as st
import pandas as pd

from utils.business_insights import (
    generate_business_insights,
    detect_optional_column
)

from utils.preprocessing import (
    create_monthly_sales,
    aggregate_by_column
)


# ============================================================
# HELPERS
# ============================================================

def safe_column(name):
    """
    Convert missing values or the string 'None' into Python None.
    """

    if name is None:
        return None

    if str(name).strip().lower() == "none":
        return None

    return name


def safe_numeric_series(df, column):
    """
    Safely convert a dataframe column to numeric values.
    """

    if not column:
        return None

    if column not in df.columns:
        return None

    return pd.to_numeric(
        df[column],
        errors="coerce"
    )


def format_number(value):
    """
    Format KPI values safely.
    """

    if value is None:
        return "N/A"

    try:
        return f"{value:,.0f}"

    except Exception:
        return "N/A"


def format_percentage(value):
    """
    Format percentage KPI values safely.
    """

    if value is None:
        return "N/A"

    try:
        return f"{value:.2f}%"

    except Exception:
        return "N/A"


# ============================================================
# MAIN DASHBOARD
# ============================================================

def show_dashboard():

    # ========================================================
    # DATASET CHECK
    # ========================================================

    if not st.session_state.get(
        "dataset_configured",
        False
    ):

        st.title(
            "🏠 Executive Dashboard"
        )

        st.info(
            "No retail dataset has been configured yet.\n\n"
            "Go to **📁 Data Upload**, upload your retail "
            "dataset and confirm the column configuration."
        )

        return


    analysis_df = st.session_state.get(
        "analysis_df"
    )


    if analysis_df is None:

        st.title(
            "🏠 Executive Dashboard"
        )

        st.warning(
            "The dataset configuration exists, but the "
            "processed dataset is unavailable.\n\n"
            "Please configure the dataset again from "
            "**📁 Data Upload**."
        )

        return


    if not isinstance(
        analysis_df,
        pd.DataFrame
    ):

        st.error(
            "The active dataset is not a valid dataframe."
        )

        return


    if analysis_df.empty:

        st.warning(
            "The configured dataset contains no usable records."
        )

        return


    df = analysis_df.copy()


    # ========================================================
    # COLUMN MAPPINGS
    # ========================================================

    date_column = safe_column(
        st.session_state.get(
            "date_column"
        )
    )

    sales_column = safe_column(
        st.session_state.get(
            "sales_column"
        )
    )

    quantity_column = safe_column(
        st.session_state.get(
            "quantity_column"
        )
    )

    product_column = safe_column(
        st.session_state.get(
            "product_column"
        )
    )

    category_column = safe_column(
        st.session_state.get(
            "category_column"
        )
    )

    region_column = safe_column(
        st.session_state.get(
            "region_column"
        )
    )

    customer_column = safe_column(
        st.session_state.get(
            "customer_column"
        )
    )


    # ========================================================
    # OPTIONAL BUSINESS COLUMNS
    # ========================================================

    columns = list(
        df.columns
    )


    profit_column = detect_optional_column(
        columns,
        [
            "profit",
            "net profit",
            "gross profit"
        ]
    )


    discount_column = detect_optional_column(
        columns,
        [
            "discount",
            "discount percentage",
            "discount percent"
        ]
    )


    shipping_column = detect_optional_column(
        columns,
        [
            "shipping cost",
            "shipping",
            "freight cost",
            "delivery cost"
        ]
    )


    # ========================================================
    # HEADER
    # ========================================================

    st.title(
        "🏠 Executive Dashboard"
    )

    st.caption(
        "Real-time overview of retail performance, "
        "profitability and business health."
    )


    # ========================================================
    # ACTIVE DATASET INFORMATION
    # ========================================================

    file_name = (
        st.session_state.get(
            "current_file_name"
        )
        or
        "Retail Dataset"
    )

    sheet_name = st.session_state.get(
        "current_sheet_name"
    )


    with st.expander(
        "📁 Active Dataset",
        expanded=False
    ):

        d1, d2, d3 = st.columns(3)

        with d1:

            st.metric(
                "Rows",
                f"{len(df):,}"
            )

        with d2:

            st.metric(
                "Columns",
                f"{len(df.columns):,}"
            )

        with d3:

            st.metric(
                "Configured",
                "Yes"
            )

        st.write(
            f"**File:** {file_name}"
        )

        if sheet_name:

            st.write(
                f"**Worksheet:** {sheet_name}"
            )


    # ========================================================
    # KPI CALCULATIONS
    # ========================================================

    sales_values = safe_numeric_series(
        df,
        sales_column
    )

    profit_values = safe_numeric_series(
        df,
        profit_column
    )

    quantity_values = safe_numeric_series(
        df,
        quantity_column
    )


    # --------------------------------------------------------
    # TOTAL SALES
    # --------------------------------------------------------

    if (
        sales_values is not None
        and
        sales_values.notna().any()
    ):

        total_sales = float(
            sales_values.sum()
        )

    else:

        total_sales = None


    # --------------------------------------------------------
    # TOTAL PROFIT
    # --------------------------------------------------------

    if (
        profit_values is not None
        and
        profit_values.notna().any()
    ):

        total_profit = float(
            profit_values.sum()
        )

    else:

        total_profit = None


    # --------------------------------------------------------
    # TOTAL QUANTITY
    # --------------------------------------------------------

    if (
        quantity_values is not None
        and
        quantity_values.notna().any()
    ):

        total_quantity = float(
            quantity_values.sum()
        )

    else:

        total_quantity = None


    # --------------------------------------------------------
    # PROFIT MARGIN
    # --------------------------------------------------------

    if (
        total_sales is not None
        and
        total_profit is not None
        and
        total_sales != 0
    ):

        profit_margin = (
            total_profit
            /
            total_sales
        ) * 100

    else:

        profit_margin = None


    # --------------------------------------------------------
    # CUSTOMERS
    # --------------------------------------------------------

    if (
        customer_column
        and
        customer_column in df.columns
    ):

        customers = int(
            df[
                customer_column
            ]
            .dropna()
            .nunique()
        )

    else:

        customers = None


    # ========================================================
    # BUSINESS INSIGHTS
    # ========================================================

    forecast_change = st.session_state.get(
        "percentage_change"
    )


    try:

        insights = generate_business_insights(
            df=df,
            sales_column=sales_column,
            profit_column=profit_column,
            discount_column=discount_column,
            shipping_column=shipping_column,
            category_column=category_column,
            product_column=product_column,
            region_column=region_column,
            forecast_change=forecast_change
        )

    except Exception:

        insights = {
            "health_score": 0,
            "health_label": "Unavailable",
            "opportunities": [],
            "recommendations": [],
            "warnings": []
        }


    if not isinstance(
        insights,
        dict
    ):

        insights = {}


    health_score = insights.get(
        "health_score",
        0
    )

    health_label = insights.get(
        "health_label",
        "Unavailable"
    )


    # --------------------------------------------------------
    # PROTECT HEALTH SCORE
    # --------------------------------------------------------

    try:

        health_score = float(
            health_score
        )

    except Exception:

        health_score = 0


    health_score = max(
        0,
        min(
            100,
            health_score
        )
    )


    # ========================================================
    # KPI ROW
    # ========================================================

    st.subheader(
        "📌 Key Performance Indicators"
    )


    k1, k2, k3, k4, k5 = st.columns(
        5
    )


    with k1:

        st.metric(
            "💰 Total Sales",
            format_number(
                total_sales
            )
        )


    with k2:

        st.metric(
            "📈 Total Profit",
            format_number(
                total_profit
            )
        )


    with k3:

        st.metric(
            "💹 Profit Margin",
            format_percentage(
                profit_margin
            )
        )


    with k4:

        st.metric(
            "📦 Units Sold",
            format_number(
                total_quantity
            )
        )


    with k5:

        st.metric(
            "👥 Customers",
            (
                f"{customers:,}"
                if customers is not None
                else "N/A"
            )
        )


    st.divider()


    # ========================================================
    # BUSINESS HEALTH
    # ========================================================

    st.subheader(
        "💼 Business Health"
    )


    h1, h2, h3 = st.columns(
        [1, 1, 2]
    )


    with h1:

        st.metric(
            "Health Score",
            f"{health_score:.0f}/100"
        )


    with h2:

        st.metric(
            "Status",
            health_label
        )


    with h3:

        st.progress(
            int(health_score)
        )


        if health_score >= 80:

            st.success(
                "Business performance is currently strong."
            )

        elif health_score >= 60:

            st.info(
                "Business performance is generally healthy."
            )

        elif health_score >= 40:

            st.warning(
                "Some business areas require attention."
            )

        else:

            st.error(
                "Significant business risks require attention."
            )


    st.divider()


    # ========================================================
    # SALES TREND + CATEGORY PERFORMANCE
    # ========================================================

    chart_left, chart_right = st.columns(
        2,
        gap="large"
    )


    # ========================================================
    # SALES TREND
    # ========================================================

    with chart_left:

        st.subheader(
            "📈 Sales Trend"
        )


        if (
            date_column
            and
            sales_column
            and
            date_column in df.columns
            and
            sales_column in df.columns
        ):

            try:

                monthly_sales = create_monthly_sales(
                    df,
                    date_column,
                    sales_column
                )


                if (
                    monthly_sales is not None
                    and
                    not monthly_sales.empty
                ):

                    st.line_chart(
                        monthly_sales,
                        x=date_column,
                        y=sales_column,
                        use_container_width=True
                    )

                else:

                    st.info(
                        "No sales trend data available."
                    )

            except Exception:

                st.info(
                    "Unable to generate the sales trend."
                )

        else:

            st.info(
                "Date and Sales columns are required."
            )


    # ========================================================
    # CATEGORY PERFORMANCE
    # ========================================================

    with chart_right:

        st.subheader(
            "🏷️ Category Performance"
        )


        if (
            category_column
            and
            sales_column
            and
            category_column in df.columns
            and
            sales_column in df.columns
        ):

            try:

                category_sales = aggregate_by_column(
                    df,
                    category_column,
                    sales_column
                )


                if (
                    category_sales is not None
                    and
                    not category_sales.empty
                ):

                    category_sales = (
                        category_sales
                        .head(10)
                    )


                    st.bar_chart(
                        category_sales,
                        x=category_column,
                        y=sales_column,
                        use_container_width=True
                    )

                else:

                    st.info(
                        "No category performance data available."
                    )

            except Exception:

                st.info(
                    "Unable to generate category performance."
                )

        else:

            st.info(
                "Category and Sales columns are required."
            )


    # ========================================================
    # REGION + PRODUCTS
    # ========================================================

    chart_left2, chart_right2 = st.columns(
        2,
        gap="large"
    )


    # ========================================================
    # REGIONAL PERFORMANCE
    # ========================================================

    with chart_left2:

        st.subheader(
            "🌍 Regional Performance"
        )


        if (
            region_column
            and
            sales_column
            and
            region_column in df.columns
            and
            sales_column in df.columns
        ):

            try:

                region_sales = aggregate_by_column(
                    df,
                    region_column,
                    sales_column
                )


                if (
                    region_sales is not None
                    and
                    not region_sales.empty
                ):

                    region_sales = (
                        region_sales
                        .head(10)
                    )


                    st.bar_chart(
                        region_sales,
                        x=region_column,
                        y=sales_column,
                        use_container_width=True
                    )

                else:

                    st.info(
                        "No regional performance data available."
                    )

            except Exception:

                st.info(
                    "Unable to generate regional performance."
                )

        else:

            st.info(
                "Region and Sales columns are required."
            )


    # ========================================================
    # TOP PRODUCTS
    # ========================================================

    with chart_right2:

        st.subheader(
            "🏆 Top Products"
        )


        if (
            product_column
            and
            sales_column
            and
            product_column in df.columns
            and
            sales_column in df.columns
        ):

            try:

                top_products = aggregate_by_column(
                    df,
                    product_column,
                    sales_column
                )


                if (
                    top_products is not None
                    and
                    not top_products.empty
                ):

                    top_products = (
                        top_products
                        .head(10)
                        .copy()
                    )


                    st.dataframe(
                        top_products,
                        use_container_width=True,
                        hide_index=True
                    )

                else:

                    st.info(
                        "No product ranking data available."
                    )

            except Exception:

                st.info(
                    "Unable to generate product rankings."
                )

        else:

            st.info(
                "Product and Sales columns are required."
            )


    st.divider()


    # ========================================================
    # EXECUTIVE INSIGHTS
    # ========================================================

    st.subheader(
        "💡 Executive Insights"
    )


    opportunity_list = insights.get(
        "opportunities",
        []
    ) or []


    recommendation_list = insights.get(
        "recommendations",
        []
    ) or []


    warning_list = insights.get(
        "warnings",
        []
    ) or []


    insight_col1, insight_col2 = st.columns(
        2,
        gap="large"
    )


    # ========================================================
    # OPPORTUNITIES
    # ========================================================

    with insight_col1:

        st.markdown(
            "#### 🟢 Growth Opportunities"
        )


        if opportunity_list:

            for opportunity in opportunity_list[:3]:

                st.success(
                    str(opportunity)
                )

        else:

            st.info(
                "No major growth opportunities detected yet."
            )


    # ========================================================
    # RECOMMENDATIONS
    # ========================================================

    with insight_col2:

        st.markdown(
            "#### 🟡 Recommended Actions"
        )


        if recommendation_list:

            for recommendation in recommendation_list[:3]:

                st.info(
                    str(recommendation)
                )

        else:

            st.info(
                "No additional recommendations available."
            )


    # ========================================================
    # WARNINGS
    # ========================================================

    if warning_list:

        st.markdown(
            "#### 🔴 Risks Requiring Attention"
        )


        for warning in warning_list[:3]:

            st.warning(
                str(warning)
            )


    # ========================================================
    # FORECAST SUMMARY
    # ========================================================

    if st.session_state.get(
        "lstm_trained",
        False
    ):

        st.divider()

        st.subheader(
            "🤖 Forecast Summary"
        )


        f1, f2, f3, f4 = st.columns(
            4
        )


        best_model = st.session_state.get(
            "best_model"
        )


        best_mape = st.session_state.get(
            "best_mape"
        )


        forecast_change = st.session_state.get(
            "percentage_change"
        )


        forecast_target = st.session_state.get(
            "forecast_target_used"
        )


        with f1:

            st.metric(
                "Best Tested Model",
                (
                    best_model
                    if best_model
                    else "N/A"
                )
            )


        with f2:

            st.metric(
                "Best MAPE",
                (
                    f"{best_mape:.2f}%"
                    if best_mape is not None
                    else "N/A"
                )
            )


        with f3:

            st.metric(
                "Forecast Change",
                (
                    f"{forecast_change:+.2f}%"
                    if forecast_change is not None
                    else "N/A"
                )
            )


        with f4:

            st.metric(
                "Forecast Target",
                (
                    forecast_target
                    if forecast_target
                    else "N/A"
                )
            )


        # ----------------------------------------------------
        # FORECAST DIRECTION
        # ----------------------------------------------------

        if forecast_change is not None:

            if forecast_change > 0:

                st.success(
                    "📈 The forecast indicates an expected "
                    "increase in future demand."
                )

            elif forecast_change < 0:

                st.warning(
                    "📉 The forecast indicates a potential "
                    "decline in future demand."
                )

            else:

                st.info(
                    "➡️ The forecast indicates relatively "
                    "stable future demand."
                )


    # ========================================================
    # NO FORECAST MESSAGE
    # ========================================================

    else:

        st.divider()

        st.subheader(
            "🤖 Forecast Status"
        )

        st.info(
            "No forecasting model has been trained for the "
            "current dataset yet. Open **🤖 Forecasting** "
            "to generate a demand forecast."
        )


    # ========================================================
    # FOOTER
    # ========================================================

    st.divider()

    st.caption(
        "RetailPulse recommendations are generated from the "
        "uploaded retail data and forecasting results. "
        "They are decision-support insights rather than "
        "guaranteed financial outcomes."
    )