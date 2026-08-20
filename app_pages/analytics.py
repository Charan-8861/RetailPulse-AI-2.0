import streamlit as st
import pandas as pd

from utils.preprocessing import (
    create_monthly_sales,
    aggregate_by_column
)

from utils.business_insights import (
    detect_optional_column
)


# ============================================================
# HELPERS
# ============================================================

def safe_column(value):
    """
    Convert None-like configuration values to Python None.
    """

    if value is None:
        return None

    if str(value).strip().lower() == "none":
        return None

    return value


def numeric_series(df, column):
    """
    Safely convert a dataframe column into numeric values.
    """

    if not column:
        return None

    if column not in df.columns:
        return None

    series = pd.to_numeric(
        df[column],
        errors="coerce"
    )

    if not series.notna().any():
        return None

    return series


def format_number(value, decimals=0):
    """
    Safely format numeric KPI values.
    """

    if value is None:
        return "N/A"

    try:

        if pd.isna(value):
            return "N/A"

        return f"{value:,.{decimals}f}"

    except Exception:
        return "N/A"


def safe_percentage(
    numerator,
    denominator
):
    """
    Safely calculate percentage values.
    """

    if numerator is None:
        return None

    if denominator is None:
        return None

    try:

        if denominator == 0:
            return None

        return (
            numerator
            /
            denominator
        ) * 100

    except Exception:
        return None


# ============================================================
# ANALYTICS PAGE
# ============================================================

def show_analytics():

    # ========================================================
    # HEADER
    # ========================================================

    st.title(
        "📊 Business Analytics"
    )

    st.caption(
        "Explore sales, profitability, products, categories, "
        "regions and discount performance."
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
            "Open **📁 Data Upload** from the sidebar, "
            "upload your dataset and confirm the configuration."
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
    # COLUMN CONFIGURATION
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
    # KPI CALCULATIONS
    # ========================================================

    sales_values = numeric_series(
        df,
        sales_column
    )

    profit_values = numeric_series(
        df,
        profit_column
    )

    quantity_values = numeric_series(
        df,
        quantity_column
    )


    # --------------------------------------------------------
    # TOTAL SALES
    # --------------------------------------------------------

    if sales_values is not None:

        total_sales = float(
            sales_values.sum()
        )

        avg_transaction = float(
            sales_values.mean()
        )

    else:

        total_sales = None
        avg_transaction = None


    # --------------------------------------------------------
    # TOTAL PROFIT
    # --------------------------------------------------------

    if profit_values is not None:

        total_profit = float(
            profit_values.sum()
        )

    else:

        total_profit = None


    # --------------------------------------------------------
    # TOTAL QUANTITY
    # --------------------------------------------------------

    if quantity_values is not None:

        total_quantity = float(
            quantity_values.sum()
        )

    else:

        total_quantity = None


    # --------------------------------------------------------
    # PROFIT MARGIN
    # --------------------------------------------------------

    profit_margin = safe_percentage(
        total_profit,
        total_sales
    )


    # ========================================================
    # KPI CARDS
    # ========================================================

    st.subheader(
        "📌 Performance Overview"
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
            (
                f"{profit_margin:.2f}%"
                if profit_margin is not None
                else "N/A"
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
            "🧾 Avg. Transaction",
            format_number(
                avg_transaction,
                2
            )
        )


    st.divider()


    # ========================================================
    # SALES TREND
    # ========================================================

    st.subheader(
        "📈 Sales Performance Over Time"
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


                # ------------------------------------------------
                # TREND CHANGE
                # ------------------------------------------------

                if len(monthly_sales) >= 2:

                    first_value = pd.to_numeric(
                        monthly_sales[
                            sales_column
                        ],
                        errors="coerce"
                    ).iloc[0]


                    last_value = pd.to_numeric(
                        monthly_sales[
                            sales_column
                        ],
                        errors="coerce"
                    ).iloc[-1]


                    if (
                        pd.notna(first_value)
                        and
                        pd.notna(last_value)
                        and
                        first_value != 0
                    ):

                        trend_change = (
                            (
                                last_value
                                -
                                first_value
                            )
                            /
                            first_value
                        ) * 100


                        if trend_change > 0:

                            st.success(
                                f"Sales increased by approximately "
                                f"{trend_change:.2f}% from the first "
                                f"period to the latest period."
                            )

                        elif trend_change < 0:

                            st.warning(
                                f"Sales decreased by approximately "
                                f"{abs(trend_change):.2f}% from the first "
                                f"period to the latest period."
                            )

                        else:

                            st.info(
                                "Sales remained approximately unchanged."
                            )

            else:

                st.info(
                    "No monthly sales trend is available."
                )


        except Exception as e:

            st.warning(
                "Unable to generate the sales trend."
            )

            st.caption(
                str(e)
            )

    else:

        st.info(
            "Date and Sales columns are required "
            "for trend analysis."
        )


    st.divider()


    # ========================================================
    # CATEGORY + REGION
    # ========================================================

    category_col, region_col = st.columns(
        2,
        gap="large"
    )


    # ========================================================
    # CATEGORY ANALYSIS
    # ========================================================

    with category_col:

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
                        .head(15)
                        .copy()
                    )


                    st.bar_chart(
                        category_sales,
                        x=category_column,
                        y=sales_column,
                        use_container_width=True
                    )


                    top_category = (
                        category_sales
                        .iloc[0][category_column]
                    )


                    top_category_sales = (
                        category_sales
                        .iloc[0][sales_column]
                    )


                    st.success(
                        f"Top category: **{top_category}** "
                        f"with {top_category_sales:,.2f} in sales."
                    )

                else:

                    st.info(
                        "No category performance data available."
                    )


            except Exception as e:

                st.info(
                    "Unable to generate category analysis."
                )

                st.caption(
                    str(e)
                )

        else:

            st.info(
                "Category and Sales columns are required."
            )


    # ========================================================
    # REGION ANALYSIS
    # ========================================================

    with region_col:

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
                        .head(15)
                        .copy()
                    )


                    st.bar_chart(
                        region_sales,
                        x=region_column,
                        y=sales_column,
                        use_container_width=True
                    )


                    top_region = (
                        region_sales
                        .iloc[0][region_column]
                    )


                    top_region_sales = (
                        region_sales
                        .iloc[0][sales_column]
                    )


                    st.success(
                        f"Top region: **{top_region}** "
                        f"with {top_region_sales:,.2f} in sales."
                    )

                else:

                    st.info(
                        "No regional performance data available."
                    )


            except Exception as e:

                st.info(
                    "Unable to generate regional analysis."
                )

                st.caption(
                    str(e)
                )

        else:

            st.info(
                "Region and Sales columns are required."
            )


    st.divider()


    # ========================================================
    # PRODUCT ANALYSIS
    # ========================================================

    st.subheader(
        "🏆 Product Performance"
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

            product_sales = aggregate_by_column(
                df,
                product_column,
                sales_column
            )


            if (
                product_sales is not None
                and
                not product_sales.empty
            ):

                top_products = (
                    product_sales
                    .head(10)
                    .copy()
                )


                product_left, product_right = st.columns(
                    [2, 1],
                    gap="large"
                )


                with product_left:

                    st.bar_chart(
                        top_products,
                        x=product_column,
                        y=sales_column,
                        use_container_width=True
                    )


                with product_right:

                    st.markdown(
                        "#### Top 10 Products"
                    )

                    st.dataframe(
                        top_products,
                        use_container_width=True,
                        hide_index=True
                    )

            else:

                st.info(
                    "No product performance data available."
                )


        except Exception as e:

            st.info(
                "Unable to generate product analysis."
            )

            st.caption(
                str(e)
            )

    else:

        st.info(
            "Product and Sales columns are required."
        )


    st.divider()


    # ========================================================
    # PROFITABILITY ANALYSIS
    # ========================================================

    st.subheader(
        "💹 Profitability Analysis"
    )


    if (
        profit_column
        and
        profit_column in df.columns
    ):

        profit_numeric = numeric_series(
            df,
            profit_column
        )


        if profit_numeric is None:

            st.info(
                "The Profit column does not contain "
                "usable numeric values."
            )

        else:

            valid_profit_count = int(
                profit_numeric.notna().sum()
            )


            profitable_transactions = int(
                (
                    profit_numeric > 0
                ).sum()
            )


            loss_transactions = int(
                (
                    profit_numeric < 0
                ).sum()
            )


            break_even_transactions = int(
                (
                    profit_numeric == 0
                ).sum()
            )


            p1, p2, p3 = st.columns(3)


            with p1:

                st.metric(
                    "Profitable Transactions",
                    f"{profitable_transactions:,}"
                )


            with p2:

                st.metric(
                    "Loss-Making Transactions",
                    f"{loss_transactions:,}"
                )


            with p3:

                st.metric(
                    "Break-Even Transactions",
                    f"{break_even_transactions:,}"
                )


            # ------------------------------------------------
            # LOSS RATE
            # ------------------------------------------------

            if valid_profit_count > 0:

                loss_percentage = (
                    loss_transactions
                    /
                    valid_profit_count
                ) * 100


                if loss_percentage > 25:

                    st.error(
                        f"{loss_percentage:.2f}% of transactions "
                        f"with valid profit values are loss-making."
                    )

                elif loss_percentage > 10:

                    st.warning(
                        f"{loss_percentage:.2f}% of transactions "
                        f"with valid profit values are loss-making."
                    )

                else:

                    st.success(
                        "Loss-making transactions account for "
                        f"{loss_percentage:.2f}% of records with "
                        "valid profit values."
                    )


            # =================================================
            # CATEGORY PROFIT
            # =================================================

            if (
                category_column
                and
                category_column in df.columns
            ):

                st.markdown(
                    "#### Profit by Category"
                )


                category_profit_df = df[
                    [
                        category_column,
                        profit_column
                    ]
                ].copy()


                category_profit_df[
                    profit_column
                ] = pd.to_numeric(
                    category_profit_df[
                        profit_column
                    ],
                    errors="coerce"
                )


                category_profit_df = (
                    category_profit_df
                    .dropna(
                        subset=[
                            category_column,
                            profit_column
                        ]
                    )
                )


                if not category_profit_df.empty:

                    category_profit = (
                        category_profit_df
                        .groupby(
                            category_column,
                            as_index=False
                        )[profit_column]
                        .sum()
                        .sort_values(
                            profit_column,
                            ascending=False
                        )
                    )


                    st.bar_chart(
                        category_profit,
                        x=category_column,
                        y=profit_column,
                        use_container_width=True
                    )


                    if not category_profit.empty:

                        best_profit_category = (
                            category_profit
                            .iloc[0][category_column]
                        )


                        worst_profit_category = (
                            category_profit
                            .iloc[-1][category_column]
                        )


                        best_profit_value = (
                            category_profit
                            .iloc[0][profit_column]
                        )


                        worst_profit_value = (
                            category_profit
                            .iloc[-1][profit_column]
                        )


                        c1, c2 = st.columns(2)


                        with c1:

                            st.success(
                                "Most profitable category: "
                                f"**{best_profit_category}** "
                                f"({best_profit_value:,.2f})"
                            )


                        with c2:

                            if worst_profit_value < 0:

                                st.warning(
                                    "Lowest-profit category: "
                                    f"**{worst_profit_category}** "
                                    f"({worst_profit_value:,.2f})"
                                )

                            else:

                                st.info(
                                    "Lowest-profit category: "
                                    f"**{worst_profit_category}** "
                                    f"({worst_profit_value:,.2f})"
                                )

                else:

                    st.info(
                        "No usable category-profit data is available."
                    )


    else:

        st.info(
            "Profitability analysis is unavailable because "
            "a Profit column was not detected."
        )


    st.divider()


    # ========================================================
    # DISCOUNT ANALYSIS
    # ========================================================

    st.subheader(
        "🏷️ Discount Impact"
    )


    if (
        discount_column
        and
        discount_column in df.columns
    ):

        discount_numeric = numeric_series(
            df,
            discount_column
        )


        if discount_numeric is None:

            st.info(
                "The Discount column does not contain "
                "usable numeric values."
            )

        else:

            average_discount = float(
                discount_numeric.mean()
            )


            d1, d2 = st.columns(2)


            with d1:

                st.metric(
                    "Average Discount",
                    f"{average_discount:,.3f}"
                )


            # ------------------------------------------------
            # DISCOUNT / PROFIT CORRELATION
            # ------------------------------------------------

            correlation = None


            if (
                profit_column
                and
                profit_column in df.columns
            ):

                profit_for_discount = numeric_series(
                    df,
                    profit_column
                )


                if profit_for_discount is not None:

                    discount_profit = pd.DataFrame(
                        {
                            "Discount": discount_numeric,
                            "Profit": profit_for_discount
                        }
                    ).dropna()


                    if (
                        len(discount_profit) >= 5
                        and
                        discount_profit[
                            "Discount"
                        ].nunique() > 1
                        and
                        discount_profit[
                            "Profit"
                        ].nunique() > 1
                    ):

                        correlation = (
                            discount_profit[
                                "Discount"
                            ]
                            .corr(
                                discount_profit[
                                    "Profit"
                                ]
                            )
                        )


            with d2:

                if (
                    correlation is not None
                    and
                    pd.notna(correlation)
                ):

                    st.metric(
                        "Discount-Profit Correlation",
                        f"{correlation:.3f}"
                    )

                else:

                    st.metric(
                        "Discount-Profit Correlation",
                        "N/A"
                    )


            if (
                correlation is not None
                and
                pd.notna(correlation)
            ):

                if correlation < -0.20:

                    st.warning(
                        "Higher discounts are associated with "
                        "lower profitability in this dataset. "
                        "Review aggressive discounting policies."
                    )

                elif correlation > 0.20:

                    st.info(
                        "Discounts show a positive relationship "
                        "with profit in this dataset. Investigate "
                        "whether targeted promotions are driving "
                        "profitable volume."
                    )

                else:

                    st.info(
                        "The dataset shows only a weak relationship "
                        "between discount and profit."
                    )

            elif profit_column:

                st.info(
                    "A stable Discount-Profit correlation could "
                    "not be calculated from the available data."
                )


    else:

        st.info(
            "No Discount column was detected."
        )


    st.divider()


    # ========================================================
    # SHIPPING COST ANALYSIS
    # ========================================================

    st.subheader(
        "🚚 Shipping Cost Analysis"
    )


    if (
        shipping_column
        and
        shipping_column in df.columns
    ):

        shipping_values = numeric_series(
            df,
            shipping_column
        )


        if shipping_values is None:

            st.info(
                "The Shipping Cost column does not contain "
                "usable numeric values."
            )

        else:

            total_shipping = float(
                shipping_values.sum()
            )


            average_shipping = float(
                shipping_values.mean()
            )


            shipping_ratio = safe_percentage(
                total_shipping,
                total_sales
            )


            s1, s2, s3 = st.columns(3)


            with s1:

                st.metric(
                    "Total Shipping Cost",
                    f"{total_shipping:,.2f}"
                )


            with s2:

                st.metric(
                    "Average Shipping Cost",
                    f"{average_shipping:,.2f}"
                )


            with s3:

                st.metric(
                    "Shipping / Sales",
                    (
                        f"{shipping_ratio:.2f}%"
                        if shipping_ratio is not None
                        else "N/A"
                    )
                )


            if shipping_ratio is not None:

                if shipping_ratio > 15:

                    st.warning(
                        "Shipping cost represents a relatively "
                        "high proportion of sales. Review carriers, "
                        "fulfillment methods and low-value shipments."
                    )

                else:

                    st.info(
                        "Shipping costs are currently within a "
                        "moderate proportion of sales."
                    )


    else:

        st.info(
            "No Shipping Cost column was detected."
        )


    st.divider()


    # ========================================================
    # CUSTOMER ANALYSIS
    # ========================================================

    st.subheader(
        "👥 Customer Overview"
    )


    if (
        customer_column
        and
        customer_column in df.columns
    ):

        customer_series = (
            df[
                customer_column
            ]
            .dropna()
        )


        unique_customers = int(
            customer_series.nunique()
        )


        total_transactions = int(
            len(df)
        )


        if unique_customers > 0:

            avg_transactions = (
                total_transactions
                /
                unique_customers
            )

        else:

            avg_transactions = 0


        u1, u2, u3 = st.columns(3)


        with u1:

            st.metric(
                "Unique Customers",
                f"{unique_customers:,}"
            )


        with u2:

            st.metric(
                "Transaction Records",
                f"{total_transactions:,}"
            )


        with u3:

            st.metric(
                "Records per Customer",
                f"{avg_transactions:.2f}"
            )


        # ----------------------------------------------------
        # TOP CUSTOMERS BY SALES
        # ----------------------------------------------------

        if (
            sales_column
            and
            sales_column in df.columns
        ):

            customer_sales_df = df[
                [
                    customer_column,
                    sales_column
                ]
            ].copy()


            customer_sales_df[
                sales_column
            ] = pd.to_numeric(
                customer_sales_df[
                    sales_column
                ],
                errors="coerce"
            )


            customer_sales_df = (
                customer_sales_df
                .dropna(
                    subset=[
                        customer_column,
                        sales_column
                    ]
                )
            )


            if not customer_sales_df.empty:

                top_customers = (
                    customer_sales_df
                    .groupby(
                        customer_column,
                        as_index=False
                    )[sales_column]
                    .sum()
                    .sort_values(
                        sales_column,
                        ascending=False
                    )
                    .head(10)
                )


                st.markdown(
                    "#### Top Customers by Sales"
                )


                st.dataframe(
                    top_customers,
                    use_container_width=True,
                    hide_index=True
                )

            else:

                st.info(
                    "No usable customer-sales records are available."
                )

        else:

            st.info(
                "Sales is not configured, so customer sales "
                "ranking is unavailable."
            )


    else:

        st.info(
            "Customer analysis is unavailable because "
            "no Customer column was configured."
        )


    # ========================================================
    # FOOTER
    # ========================================================

    st.divider()


    st.caption(
        "Analytics are calculated directly from the currently "
        "configured retail dataset. Interpret correlations as "
        "relationships in the data rather than proof of causation."
    )