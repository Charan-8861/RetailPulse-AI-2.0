import pandas as pd
import numpy as np


# ============================================================
# HELPERS
# ============================================================

def _safe_numeric(series):
    """
    Convert a pandas Series to numeric safely.
    Invalid values become NaN.
    """

    return (
        pd.to_numeric(
            series,
            errors="coerce"
        )
        .replace(
            [np.inf, -np.inf],
            np.nan
        )
    )


def _safe_float(value):
    """
    Convert a scalar value to a finite float.
    """

    try:
        value = float(value)

        if np.isfinite(value):
            return value

    except (TypeError, ValueError):
        pass

    return None


def _valid_column(data, column):
    """
    Check whether an optional configured column exists.
    """

    if column is None:
        return False

    if str(column).strip().lower() == "none":
        return False

    return column in data.columns


def _append_unique(container, message):
    """
    Add a recommendation only when it is not already present.
    """

    if message and message not in container:
        container.append(message)


# ============================================================
# DETECT OPTIONAL COLUMN
# ============================================================

def detect_optional_column(
    columns,
    keywords
):
    """
    Detect optional business-analysis columns such as
    Profit, Discount and Shipping Cost.

    Exact normalized matches are preferred before
    partial matches.
    """

    if columns is None or keywords is None:
        return None


    cleaned_map = {}


    for column in columns:

        cleaned = (
            str(column)
            .lower()
            .replace("_", " ")
            .replace("-", " ")
            .strip()
        )


        cleaned = " ".join(
            cleaned.split()
        )


        cleaned_map[
            cleaned
        ] = column


    # ========================================================
    # EXACT MATCH
    # ========================================================

    for keyword in keywords:

        key = (
            str(keyword)
            .lower()
            .replace("_", " ")
            .replace("-", " ")
            .strip()
        )


        key = " ".join(
            key.split()
        )


        if key in cleaned_map:
            return cleaned_map[key]


    # ========================================================
    # PARTIAL MATCH
    # ========================================================

    for cleaned, original in cleaned_map.items():

        for keyword in keywords:

            key = (
                str(keyword)
                .lower()
                .replace("_", " ")
                .replace("-", " ")
                .strip()
            )


            key = " ".join(
                key.split()
            )


            if key and key in cleaned:
                return original


    return None


# ============================================================
# GENERATE BUSINESS INSIGHTS
# ============================================================

def generate_business_insights(
    df,
    sales_column=None,
    profit_column=None,
    discount_column=None,
    shipping_column=None,
    category_column=None,
    product_column=None,
    region_column=None,
    forecast_change=None
):
    """
    Generate RetailPulse business health indicators
    and actionable recommendations.

    Returns
    -------
    dict containing:

        metrics
        recommendations
        warnings
        opportunities
        health_score
        health_label
    """

    # ========================================================
    # DATA VALIDATION
    # ========================================================

    if df is None:
        raise ValueError(
            "Dataset is None."
        )


    if not isinstance(
        df,
        pd.DataFrame
    ):
        raise TypeError(
            "Dataset must be a pandas DataFrame."
        )


    if df.empty:

        return {
            "metrics": {},
            "opportunities": [],
            "recommendations": [
                "Upload a dataset containing usable retail "
                "records before generating business recommendations."
            ],
            "warnings": [
                "The current dataset contains no records."
            ],
            "health_score": 0,
            "health_label": "High Attention Required"
        }


    data = df.copy()


    metrics = {}

    recommendations = []

    warnings = []

    opportunities = []


    # Neutral starting point.
    score = 50


    # ========================================================
    # VALID COLUMN FLAGS
    # ========================================================

    has_sales = _valid_column(
        data,
        sales_column
    )

    has_profit = _valid_column(
        data,
        profit_column
    )

    has_discount = _valid_column(
        data,
        discount_column
    )

    has_shipping = _valid_column(
        data,
        shipping_column
    )

    has_category = _valid_column(
        data,
        category_column
    )

    has_product = _valid_column(
        data,
        product_column
    )

    has_region = _valid_column(
        data,
        region_column
    )


    # ========================================================
    # NUMERIC PREPARATION
    # ========================================================

    if has_sales:

        data[
            sales_column
        ] = _safe_numeric(
            data[
                sales_column
            ]
        )


    if has_profit:

        data[
            profit_column
        ] = _safe_numeric(
            data[
                profit_column
            ]
        )


    if has_discount:

        data[
            discount_column
        ] = _safe_numeric(
            data[
                discount_column
            ]
        )


    if has_shipping:

        data[
            shipping_column
        ] = _safe_numeric(
            data[
                shipping_column
            ]
        )


    # ========================================================
    # SALES ANALYSIS
    # ========================================================

    total_sales = None


    if has_sales:

        sales_values = (
            data[
                sales_column
            ]
            .dropna()
        )


        if not sales_values.empty:

            total_sales = float(
                sales_values.sum()
            )


            average_sale = float(
                sales_values.mean()
            )


            median_sale = float(
                sales_values.median()
            )


            metrics[
                "Total Sales"
            ] = total_sales


            metrics[
                "Average Sale"
            ] = average_sale


            metrics[
                "Median Sale"
            ] = median_sale


            if total_sales > 0:

                score += 3


        else:

            _append_unique(
                warnings,
                "The configured Sales field does not contain "
                "usable numeric values."
            )


    # ========================================================
    # PROFIT ANALYSIS
    # ========================================================

    total_profit = None
    profit_margin = None


    if has_profit:

        profit_values = (
            data[
                profit_column
            ]
            .dropna()
        )


        if not profit_values.empty:

            total_profit = float(
                profit_values.sum()
            )


            metrics[
                "Total Profit"
            ] = total_profit


            # =================================================
            # PROFIT MARGIN
            # =================================================

            if (
                total_sales is not None
                and
                total_sales != 0
            ):

                profit_margin = (
                    total_profit
                    /
                    total_sales
                ) * 100


                metrics[
                    "Profit Margin (%)"
                ] = profit_margin


                if profit_margin >= 20:

                    score += 15

                    _append_unique(
                        opportunities,
                        "Profit margins are strong. Prioritize "
                        "high-margin products while protecting "
                        "pricing discipline."
                    )


                elif profit_margin >= 10:

                    score += 8

                    _append_unique(
                        recommendations,
                        "Profit margins are positive but still "
                        "have room for improvement. Review pricing, "
                        "discounts and operating costs."
                    )


                elif profit_margin > 0:

                    score -= 5

                    _append_unique(
                        warnings,
                        "Profit margin is relatively low. Review "
                        "discounting, product mix and fulfillment costs."
                    )


                else:

                    score -= 20

                    _append_unique(
                        warnings,
                        "Overall profitability is negative. Prioritize "
                        "loss-making products, excessive discounts and "
                        "high-cost regions for immediate review."
                    )


            # =================================================
            # LOSS-MAKING TRANSACTIONS
            # =================================================

            valid_profit_rows = (
                data[
                    profit_column
                ]
                .dropna()
            )


            valid_profit_count = len(
                valid_profit_rows
            )


            loss_count = int(
                (
                    valid_profit_rows < 0
                )
                .sum()
            )


            if valid_profit_count > 0:

                loss_share = (
                    loss_count
                    /
                    valid_profit_count
                ) * 100


                metrics[
                    "Loss-Making Transactions (%)"
                ] = loss_share


                metrics[
                    "Loss-Making Transactions"
                ] = loss_count


                if loss_share > 25:

                    score -= 12

                    _append_unique(
                        warnings,
                        f"{loss_share:.1f}% of valid profit records "
                        "are loss-making. Identify the products, "
                        "discounts and regions driving these losses."
                    )


                elif loss_share > 10:

                    score -= 5

                    _append_unique(
                        recommendations,
                        f"{loss_share:.1f}% of valid profit records "
                        "are loss-making. Review these transactions "
                        "before attempting to increase sales volume."
                    )


                elif loss_share > 0:

                    score += 2

                    _append_unique(
                        recommendations,
                        "Loss-making transactions are relatively "
                        "limited, but they should still be monitored "
                        "for recurring product or regional patterns."
                    )


                else:

                    score += 5

                    _append_unique(
                        opportunities,
                        "No loss-making transactions were detected "
                        "among records with valid profit values."
                    )


        else:

            _append_unique(
                warnings,
                "The detected Profit field does not contain "
                "usable numeric values."
            )


    # ========================================================
    # DISCOUNT ANALYSIS
    # ========================================================

    if has_discount:

        discount_values = (
            data[
                discount_column
            ]
            .dropna()
        )


        if not discount_values.empty:

            avg_discount = float(
                discount_values.mean()
            )


            metrics[
                "Average Discount"
            ] = avg_discount


            # =================================================
            # DISCOUNT / PROFIT RELATIONSHIP
            # =================================================

            if has_profit:

                discount_profit = (
                    data[
                        [
                            discount_column,
                            profit_column
                        ]
                    ]
                    .dropna()
                )


                if len(
                    discount_profit
                ) >= 5:

                    discount_unique = (
                        discount_profit[
                            discount_column
                        ]
                        .nunique()
                    )


                    profit_unique = (
                        discount_profit[
                            profit_column
                        ]
                        .nunique()
                    )


                    if (
                        discount_unique > 1
                        and
                        profit_unique > 1
                    ):

                        correlation = (
                            discount_profit[
                                discount_column
                            ]
                            .corr(
                                discount_profit[
                                    profit_column
                                ]
                            )
                        )


                        if pd.notna(
                            correlation
                        ):

                            correlation = float(
                                correlation
                            )


                            metrics[
                                "Discount-Profit Correlation"
                            ] = correlation


                            if correlation < -0.50:

                                score -= 10

                                _append_unique(
                                    warnings,
                                    "Higher discounts show a strong "
                                    "negative relationship with profit. "
                                    "Review discount limits and replace "
                                    "broad discounting with targeted promotions."
                                )


                            elif correlation < -0.20:

                                score -= 6

                                _append_unique(
                                    warnings,
                                    "Higher discounts are associated with "
                                    "lower profit. Consider tighter discount "
                                    "controls and targeted promotions."
                                )


                            elif correlation > 0.20:

                                _append_unique(
                                    opportunities,
                                    "Discounting does not currently show a "
                                    "strong negative relationship with profit, "
                                    "but promotion effectiveness should still "
                                    "be monitored by product and category."
                                )


    # ========================================================
    # CATEGORY ANALYSIS
    # ========================================================

    if (
        has_category
        and
        has_sales
    ):

        category_sales_data = (
            data[
                [
                    category_column,
                    sales_column
                ]
            ]
            .dropna()
        )


        if not category_sales_data.empty:

            category_sales = (
                category_sales_data
                .groupby(
                    category_column
                )[sales_column]
                .sum()
                .sort_values(
                    ascending=False
                )
            )


            if not category_sales.empty:

                best_category = (
                    category_sales.index[0]
                )


                best_category_sales = float(
                    category_sales.iloc[0]
                )


                metrics[
                    "Top Sales Category"
                ] = best_category


                metrics[
                    "Top Category Sales"
                ] = best_category_sales


                _append_unique(
                    opportunities,
                    f"{best_category} is the strongest category "
                    "by sales. Ensure adequate inventory and "
                    "evaluate opportunities to expand its "
                    "highest-performing products."
                )


        # ====================================================
        # CATEGORY PROFITABILITY
        # ====================================================

        if has_profit:

            category_profit_data = (
                data[
                    [
                        category_column,
                        profit_column
                    ]
                ]
                .dropna()
            )


            if not category_profit_data.empty:

                category_profit = (
                    category_profit_data
                    .groupby(
                        category_column
                    )[profit_column]
                    .sum()
                    .sort_values()
                )


                if not category_profit.empty:

                    weakest_category = (
                        category_profit.index[0]
                    )


                    weakest_profit = float(
                        category_profit.iloc[0]
                    )


                    metrics[
                        "Weakest Profit Category"
                    ] = weakest_category


                    if weakest_profit < 0:

                        _append_unique(
                            warnings,
                            f"{weakest_category} is the weakest "
                            "category by profitability. Review "
                            "product pricing, discounts and costs "
                            "within this category."
                        )


    # ========================================================
    # PRODUCT ANALYSIS
    # ========================================================

    if (
        has_product
        and
        has_sales
    ):

        product_sales_data = (
            data[
                [
                    product_column,
                    sales_column
                ]
            ]
            .dropna()
        )


        if not product_sales_data.empty:

            product_sales = (
                product_sales_data
                .groupby(
                    product_column
                )[sales_column]
                .sum()
                .sort_values(
                    ascending=False
                )
            )


            if not product_sales.empty:

                top_product = (
                    product_sales.index[0]
                )


                top_product_sales = float(
                    product_sales.iloc[0]
                )


                metrics[
                    "Top Product"
                ] = top_product


                metrics[
                    "Top Product Sales"
                ] = top_product_sales


                _append_unique(
                    opportunities,
                    f"{top_product} is the highest-selling product. "
                    "Protect availability and evaluate complementary "
                    "cross-sell or bundle opportunities."
                )


        # ====================================================
        # PRODUCT PROFITABILITY
        # ====================================================

        if has_profit:

            product_profit_data = (
                data[
                    [
                        product_column,
                        profit_column
                    ]
                ]
                .dropna()
            )


            if not product_profit_data.empty:

                product_profit = (
                    product_profit_data
                    .groupby(
                        product_column
                    )[profit_column]
                    .sum()
                    .sort_values()
                )


                loss_products = (
                    product_profit[
                        product_profit < 0
                    ]
                )


                if not loss_products.empty:

                    worst_product = (
                        loss_products.index[0]
                    )


                    worst_product_loss = float(
                        loss_products.iloc[0]
                    )


                    metrics[
                        "Most Loss-Making Product"
                    ] = worst_product


                    metrics[
                        "Worst Product Profit"
                    ] = worst_product_loss


                    _append_unique(
                        warnings,
                        f"{worst_product} is among the most "
                        "loss-making products. Review its pricing, "
                        "discount level, shipping cost and whether "
                        "it should remain in the current product mix."
                    )


    # ========================================================
    # REGION ANALYSIS
    # ========================================================

    if (
        has_region
        and
        has_sales
    ):

        region_sales_data = (
            data[
                [
                    region_column,
                    sales_column
                ]
            ]
            .dropna()
        )


        if not region_sales_data.empty:

            region_sales = (
                region_sales_data
                .groupby(
                    region_column
                )[sales_column]
                .sum()
                .sort_values(
                    ascending=False
                )
            )


            if not region_sales.empty:

                best_region = (
                    region_sales.index[0]
                )


                best_region_sales = float(
                    region_sales.iloc[0]
                )


                metrics[
                    "Top Sales Region"
                ] = best_region


                metrics[
                    "Top Region Sales"
                ] = best_region_sales


                _append_unique(
                    opportunities,
                    f"{best_region} is the strongest region by "
                    "sales. Study its product mix and demand "
                    "patterns for practices that may transfer "
                    "to weaker regions."
                )


        # ====================================================
        # REGION PROFITABILITY
        # ====================================================

        if has_profit:

            region_profit_data = (
                data[
                    [
                        region_column,
                        profit_column
                    ]
                ]
                .dropna()
            )


            if not region_profit_data.empty:

                region_profit = (
                    region_profit_data
                    .groupby(
                        region_column
                    )[profit_column]
                    .sum()
                    .sort_values()
                )


                if not region_profit.empty:

                    weakest_region = (
                        region_profit.index[0]
                    )


                    weakest_region_profit = float(
                        region_profit.iloc[0]
                    )


                    metrics[
                        "Weakest Profit Region"
                    ] = weakest_region


                    if weakest_region_profit < 0:

                        _append_unique(
                            warnings,
                            f"{weakest_region} is generating "
                            "negative profit. Review logistics "
                            "costs, product mix and discounting "
                            "within this region."
                        )


    # ========================================================
    # SHIPPING COST ANALYSIS
    # ========================================================

    if has_shipping:

        shipping_values = (
            data[
                shipping_column
            ]
            .dropna()
        )


        if not shipping_values.empty:

            total_shipping = float(
                shipping_values.sum()
            )


            average_shipping = float(
                shipping_values.mean()
            )


            metrics[
                "Total Shipping Cost"
            ] = total_shipping


            metrics[
                "Average Shipping Cost"
            ] = average_shipping


            if (
                total_sales is not None
                and
                total_sales != 0
            ):

                shipping_ratio = (
                    total_shipping
                    /
                    total_sales
                ) * 100


                metrics[
                    "Shipping Cost / Sales (%)"
                ] = shipping_ratio


                if shipping_ratio > 20:

                    score -= 12

                    _append_unique(
                        warnings,
                        "Shipping costs represent a very high "
                        "share of sales. Review carrier rates, "
                        "fulfillment methods and low-value shipments."
                    )


                elif shipping_ratio > 15:

                    score -= 8

                    _append_unique(
                        recommendations,
                        "Shipping cost represents a relatively "
                        "high share of sales. Review fulfillment "
                        "methods, carrier rates and low-value shipments."
                    )


                elif shipping_ratio < 5:

                    score += 3

                    _append_unique(
                        opportunities,
                        "Shipping costs represent a relatively "
                        "small share of sales, indicating good "
                        "cost control in fulfillment."
                    )


    # ========================================================
    # FORECAST SIGNAL
    # ========================================================

    forecast_change = _safe_float(
        forecast_change
    )


    if forecast_change is not None:

        metrics[
            "Forecast Change (%)"
        ] = forecast_change


        if forecast_change > 10:

            score += 8

            _append_unique(
                opportunities,
                "Demand is forecast to increase meaningfully. "
                "Review inventory levels, supplier capacity "
                "and fulfillment readiness before the expected "
                "growth period."
            )


        elif forecast_change > 0:

            score += 3

            _append_unique(
                opportunities,
                "Demand is forecast to increase moderately. "
                "Maintain sufficient inventory while monitoring "
                "actual demand."
            )


        elif forecast_change < -10:

            score -= 8

            _append_unique(
                recommendations,
                "Demand is forecast to decline meaningfully. "
                "Avoid excessive inventory buildup and review "
                "procurement and promotional strategies."
            )


        elif forecast_change < 0:

            score -= 3

            _append_unique(
                recommendations,
                "Demand is forecast to decline moderately. "
                "Use conservative replenishment and monitor "
                "inventory turnover."
            )


        else:

            _append_unique(
                recommendations,
                "Forecast demand is relatively stable. Focus "
                "on margin improvement and inventory efficiency "
                "rather than aggressive expansion."
            )


    # ========================================================
    # DATA COVERAGE GUIDANCE
    # ========================================================

    if not has_profit:

        _append_unique(
            recommendations,
            "Profit data is unavailable. Add or map a Profit "
            "field to enable direct profitability analysis."
        )


    if not has_discount:

        _append_unique(
            recommendations,
            "Discount data is unavailable. Including discount "
            "information would help evaluate promotional impact."
        )


    if not has_shipping:

        _append_unique(
            recommendations,
            "Shipping-cost data is unavailable. Including "
            "fulfillment costs would improve cost-efficiency analysis."
        )


    # ========================================================
    # HEALTH SCORE
    # ========================================================

    score = int(
        round(
            max(
                0,
                min(
                    100,
                    score
                )
            )
        )
    )


    if score >= 80:

        health_label = (
            "Strong"
        )


    elif score >= 60:

        health_label = (
            "Good"
        )


    elif score >= 40:

        health_label = (
            "Needs Attention"
        )


    else:

        health_label = (
            "High Attention Required"
        )


    # ========================================================
    # FALLBACK GUIDANCE
    # ========================================================

    if not recommendations:

        recommendations.append(
            "Continue monitoring sales trends, product "
            "performance, profitability and forecasting "
            "accuracy before making major business decisions."
        )


    # ========================================================
    # RETURN
    # ========================================================

    return {

        "metrics":
            metrics,

        "opportunities":
            opportunities,

        "recommendations":
            recommendations,

        "warnings":
            warnings,

        "health_score":
            score,

        "health_label":
            health_label
    }