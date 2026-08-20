import streamlit as st
import pandas as pd
import numpy as np

from utils.business_insights import (
    generate_business_insights,
    detect_optional_column
)


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


def safe_numeric_series(df, column):
    """
    Convert a dataframe column to numeric safely.
    """

    if not column:
        return None

    if column not in df.columns:
        return None

    values = pd.to_numeric(
        df[column],
        errors="coerce"
    )

    if not values.notna().any():
        return None

    return values


def safe_float(value):
    """
    Safely convert a value to float.
    """

    try:

        value = float(value)

        if not np.isfinite(value):
            return None

        return value

    except (TypeError, ValueError):
        return None


def format_metric_value(value):
    """
    Format insight metric values safely.
    """

    if value is None:
        return "N/A"

    if isinstance(
        value,
        (
            float,
            np.floating
        )
    ):

        if not np.isfinite(value):
            return "N/A"

        return f"{value:,.2f}"

    if isinstance(
        value,
        (
            int,
            np.integer
        )
    ):

        return f"{value:,}"

    return str(value)


# ============================================================
# BUSINESS INSIGHTS PAGE
# ============================================================

def show_business_insights():

    # ========================================================
    # HEADER
    # ========================================================

    st.title(
        "💡 Business Insights & Recommendations"
    )

    st.caption(
        "Data-driven retail recommendations based on "
        "sales, profitability, products, regions and forecasts."
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
            "Open **📁 Data Upload**, upload your retail "
            "dataset and confirm the dataset configuration first."
        )

        return


    df = st.session_state.get(
        "analysis_df"
    )


    if df is None:

        st.warning(
            "The processed dataset is unavailable.\n\n"
            "Please configure the dataset again from "
            "**📁 Data Upload**."
        )

        return


    if not isinstance(
        df,
        pd.DataFrame
    ):

        st.error(
            "The active dataset is not a valid dataframe."
        )

        return


    if df.empty:

        st.warning(
            "The configured dataset contains no usable records."
        )

        return


    df = df.copy()


    # ========================================================
    # COLUMN MAPPINGS
    # ========================================================

    sales_column = safe_column(
        st.session_state.get(
            "sales_column"
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


    columns = list(
        df.columns
    )


    # ========================================================
    # OPTIONAL BUSINESS COLUMNS
    # ========================================================

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
    # FORECAST SIGNAL
    # ========================================================

    forecast_change = None


    if st.session_state.get(
        "lstm_trained",
        False
    ):

        forecast_change = safe_float(
            st.session_state.get(
                "percentage_change"
            )
        )


    # ========================================================
    # GENERATE INSIGHTS
    # ========================================================

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

    except Exception as e:

        st.error(
            "Unable to generate business insights."
        )

        st.exception(e)

        return


    if not isinstance(
        insights,
        dict
    ):

        st.error(
            "The business insight engine returned an "
            "unexpected result."
        )

        return


    # ========================================================
    # HEALTH SCORE
    # ========================================================

    health_score = safe_float(
        insights.get(
            "health_score",
            0
        )
    )


    if health_score is None:
        health_score = 0


    health_score = max(
        0,
        min(
            100,
            health_score
        )
    )


    health_label = insights.get(
        "health_label",
        "Unknown"
    )


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
            str(
                health_label
            )
        )


    with h3:

        st.progress(
            int(
                health_score
            )
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
                "Several business areas require attention."
            )

        else:

            st.error(
                "Significant business risks require attention."
            )


    st.divider()


    # ========================================================
    # AVAILABLE INTELLIGENCE
    # ========================================================

    st.subheader(
        "🧠 Available Business Intelligence"
    )


    a1, a2, a3, a4 = st.columns(
        4
    )


    with a1:

        st.metric(
            "Sales Analysis",
            (
                "Available"
                if (
                    sales_column
                    and
                    sales_column in df.columns
                )
                else "Unavailable"
            )
        )


    with a2:

        st.metric(
            "Profit Analysis",
            (
                "Available"
                if (
                    profit_column
                    and
                    profit_column in df.columns
                )
                else "Unavailable"
            )
        )


    with a3:

        st.metric(
            "Discount Analysis",
            (
                "Available"
                if (
                    discount_column
                    and
                    discount_column in df.columns
                )
                else "Unavailable"
            )
        )


    with a4:

        st.metric(
            "Forecast Intelligence",
            (
                "Available"
                if forecast_change is not None
                else "Not Trained"
            )
        )


    # ========================================================
    # KEY BUSINESS METRICS
    # ========================================================

    metrics = insights.get(
        "metrics",
        {}
    )


    if isinstance(
        metrics,
        dict
    ) and metrics:

        st.divider()

        st.subheader(
            "📌 Key Business Indicators"
        )


        metric_rows = []


        for (
            metric_name,
            metric_value
        ) in metrics.items():

            metric_rows.append(
                {
                    "Business Metric":
                        metric_name,

                    "Value":
                        format_metric_value(
                            metric_value
                        )
                }
            )


        metric_df = pd.DataFrame(
            metric_rows
        )


        st.dataframe(
            metric_df,
            use_container_width=True,
            hide_index=True
        )


    # ========================================================
    # MANAGEMENT SUMMARY
    # ========================================================

    st.divider()

    st.subheader(
        "📝 Management Summary"
    )


    summary_points = []


    # --------------------------------------------------------
    # SALES
    # --------------------------------------------------------

    if (
        sales_column
        and
        sales_column in df.columns
    ):

        sales_values = safe_numeric_series(
            df,
            sales_column
        )


        if sales_values is not None:

            total_sales = float(
                sales_values.sum()
            )


            summary_points.append(
                f"Historical sales of approximately "
                f"{total_sales:,.2f} were analyzed using "
                f"the configured **{sales_column}** field."
            )

        else:

            summary_points.append(
                "The configured Sales field does not contain "
                "enough valid numeric values for a reliable "
                "sales summary."
            )


    # --------------------------------------------------------
    # PROFIT
    # --------------------------------------------------------

    if (
        profit_column
        and
        profit_column in df.columns
    ):

        profit_values = safe_numeric_series(
            df,
            profit_column
        )


        if profit_values is not None:

            total_profit = float(
                profit_values.sum()
            )


            if total_profit > 0:

                summary_points.append(
                    "The business generated positive overall "
                    "profit during the available historical period."
                )

            elif total_profit < 0:

                summary_points.append(
                    "The historical dataset shows an overall "
                    "loss, so profitability requires immediate "
                    "attention."
                )

            else:

                summary_points.append(
                    "Overall historical profit is approximately "
                    "break-even."
                )


    # --------------------------------------------------------
    # FORECAST
    # --------------------------------------------------------

    if forecast_change is not None:

        if forecast_change > 10:

            summary_points.append(
                f"Future demand is projected to increase by "
                f"approximately {forecast_change:.2f}%."
            )

        elif forecast_change > 0:

            summary_points.append(
                f"Future demand shows moderate projected "
                f"growth of {forecast_change:.2f}%."
            )

        elif forecast_change < -10:

            summary_points.append(
                f"Future demand is projected to decline by "
                f"approximately {abs(forecast_change):.2f}%."
            )

        elif forecast_change < 0:

            summary_points.append(
                f"Future demand shows a moderate projected "
                f"decline of {abs(forecast_change):.2f}%."
            )

        else:

            summary_points.append(
                "Future demand is projected to remain broadly stable."
            )


    if not summary_points:

        summary_points.append(
            "Additional retail fields would enable richer "
            "business-performance analysis."
        )


    for point in summary_points:

        st.write(
            f"• {point}"
        )


    # ========================================================
    # GROWTH OPPORTUNITIES
    # ========================================================

    opportunities = insights.get(
        "opportunities",
        []
    ) or []


    st.divider()

    st.subheader(
        "🟢 Growth & Profit Opportunities"
    )


    if opportunities:

        for index, opportunity in enumerate(
            opportunities,
            start=1
        ):

            st.success(
                f"{index}. {str(opportunity)}"
            )

    else:

        st.info(
            "No strong growth opportunity has been detected "
            "from the currently available fields."
        )


    # ========================================================
    # RECOMMENDED ACTIONS
    # ========================================================

    recommendations = insights.get(
        "recommendations",
        []
    ) or []


    st.subheader(
        "🟡 Recommended Business Actions"
    )


    if recommendations:

        for index, recommendation in enumerate(
            recommendations,
            start=1
        ):

            st.info(
                f"{index}. {str(recommendation)}"
            )

    else:

        st.info(
            "No additional actions were generated for the "
            "current dataset."
        )


    # ========================================================
    # RISKS
    # ========================================================

    warnings = insights.get(
        "warnings",
        []
    ) or []


    st.subheader(
        "🔴 Risks Requiring Attention"
    )


    if warnings:

        for index, warning in enumerate(
            warnings,
            start=1
        ):

            st.warning(
                f"{index}. {str(warning)}"
            )

    else:

        st.success(
            "No major risk warnings were detected from the "
            "currently available business indicators."
        )


    # ========================================================
    # PROFIT IMPROVEMENT FOCUS
    # ========================================================

    st.divider()

    st.subheader(
        "💰 Profit Improvement Focus"
    )


    if (
        profit_column is None
        or
        profit_column not in df.columns
    ):

        st.info(
            "A Profit field was not detected.\n\n"
            "Upload a dataset containing Profit or Margin data "
            "to enable direct profitability recommendations.\n\n"
            "RetailPulse can still provide sales, product, "
            "regional and demand-based recommendations."
        )

    else:

        profit_numeric = safe_numeric_series(
            df,
            profit_column
        )


        if profit_numeric is None:

            st.info(
                "The Profit field does not contain enough "
                "valid numeric values for profitability analysis."
            )

        else:

            valid_profit_count = int(
                profit_numeric.notna().sum()
            )


            loss_records = int(
                (
                    profit_numeric < 0
                ).sum()
            )


            if valid_profit_count > 0:

                loss_rate = (
                    loss_records
                    /
                    valid_profit_count
                ) * 100

            else:

                loss_rate = 0


            p1, p2 = st.columns(
                2
            )


            with p1:

                st.metric(
                    "Loss-Making Records",
                    f"{loss_records:,}"
                )


            with p2:

                st.metric(
                    "Loss-Making Share",
                    f"{loss_rate:.2f}%"
                )


            if loss_rate > 25:

                st.error(
                    "A high proportion of transactions are "
                    "loss-making.\n\n"
                    "Focus first on identifying the products, "
                    "regions and discounts associated with these "
                    "losses before attempting to increase total "
                    "sales volume."
                )

            elif loss_rate > 10:

                st.warning(
                    "A meaningful proportion of transactions "
                    "generate negative profit.\n\n"
                    "Review pricing, discount levels, shipping "
                    "costs and product mix for these transactions."
                )

            else:

                st.success(
                    "The proportion of loss-making transactions "
                    "is relatively controlled, but individual "
                    "loss drivers should still be monitored."
                )


    # ========================================================
    # FORECAST-BASED DECISION GUIDANCE
    # ========================================================

    st.divider()

    st.subheader(
        "🤖 Forecast-Based Decision Guidance"
    )


    if forecast_change is None:

        st.info(
            "No forecasting result is available yet.\n\n"
            "Open **🤖 Forecasting**, train the model and return "
            "here to receive forecast-enhanced recommendations."
        )

    else:

        best_model = st.session_state.get(
            "best_model"
        )


        best_mape = safe_float(
            st.session_state.get(
                "best_mape"
            )
        )


        forecast_target = st.session_state.get(
            "forecast_target_used"
        )


        forecast_frequency = st.session_state.get(
            "forecast_frequency"
        )


        f1, f2, f3, f4 = st.columns(
            4
        )


        with f1:

            st.metric(
                "Forecast Change",
                f"{forecast_change:+.2f}%"
            )


        with f2:

            st.metric(
                "Best Tested Model",
                best_model or "N/A"
            )


        with f3:

            st.metric(
                "Best MAPE",
                (
                    f"{best_mape:.2f}%"
                    if best_mape is not None
                    else "N/A"
                )
            )


        with f4:

            st.metric(
                "Forecast Target",
                forecast_target or "N/A"
            )


        if forecast_frequency:

            st.caption(
                f"Forecast frequency: **{forecast_frequency}**"
            )


        # ----------------------------------------------------
        # FORECAST ACTION
        # ----------------------------------------------------

        if forecast_change > 10:

            st.success(
                "Demand growth is projected.\n\n"
                "Recommended operational response: review "
                "inventory availability, supplier capacity, "
                "stock replenishment and fulfillment readiness."
            )

        elif forecast_change > 0:

            st.info(
                "Moderate demand growth is projected.\n\n"
                "Maintain adequate inventory while monitoring "
                "actual sales before making aggressive "
                "expansion decisions."
            )

        elif forecast_change < -10:

            st.warning(
                "A meaningful demand decline is projected.\n\n"
                "Consider conservative procurement, tighter "
                "inventory control and targeted promotions to "
                "reduce the risk of excess stock."
            )

        elif forecast_change < 0:

            st.warning(
                "A moderate decline is projected.\n\n"
                "Monitor replenishment levels and focus on "
                "profitable products rather than increasing "
                "inventory broadly."
            )

        else:

            st.info(
                "Demand is projected to remain stable.\n\n"
                "Focus on improving margins, reducing avoidable "
                "costs and increasing product/customer efficiency."
            )


        # ----------------------------------------------------
        # MODEL RELIABILITY
        # ----------------------------------------------------

        if (
            best_model is not None
            and
            best_model != "LSTM"
        ):

            st.warning(
                "⚠️ **Forecast Reliability Notice**\n\n"
                "The future demand forecast is generated by the "
                "LSTM model, but another forecasting method "
                "performed better during historical testing.\n\n"
                "Forecast-based recommendations should therefore "
                "be treated as decision-support guidance rather "
                "than guaranteed future outcomes."
            )

        elif (
            best_model == "LSTM"
            and
            best_mape is not None
        ):

            st.success(
                f"The LSTM was the strongest tested model "
                f"with a MAPE of approximately "
                f"{best_mape:.2f}%."
            )


    # ========================================================
    # RECOMMENDATION COVERAGE
    # ========================================================

    st.divider()

    st.subheader(
        "ℹ️ Recommendation Coverage"
    )


    missing_fields = []


    if profit_column is None:

        missing_fields.append(
            "Profit"
        )


    if discount_column is None:

        missing_fields.append(
            "Discount"
        )


    if shipping_column is None:

        missing_fields.append(
            "Shipping Cost"
        )


    if category_column is None:

        missing_fields.append(
            "Category"
        )


    if product_column is None:

        missing_fields.append(
            "Product"
        )


    if region_column is None:

        missing_fields.append(
            "Region"
        )


    if missing_fields:

        st.caption(
            "Additional analysis could be generated if the "
            "dataset contained or mapped: "
            + ", ".join(
                missing_fields
            )
            + "."
        )

    else:

        st.success(
            "The dataset contains the main fields required for "
            "comprehensive RetailPulse business recommendations."
        )


    # ========================================================
    # FOOTER
    # ========================================================

    st.divider()

    st.caption(
        "RetailPulse recommendations are generated from "
        "historical retail data and model outputs. They are "
        "intended to support business decisions and do not "
        "guarantee future profit."
    )