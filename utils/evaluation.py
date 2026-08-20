import numpy as np

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)


# ============================================================
# MODEL EVALUATION
# ============================================================

def evaluate_model(
    actual,
    predicted
):
    """
    Calculate forecasting evaluation metrics.

    Metrics returned
    ----------------
    MAE
        Mean Absolute Error

    RMSE
        Root Mean Squared Error

    MAPE
        Mean Absolute Percentage Error

    R2
        R-squared score

    Notes
    -----
    Invalid NaN / infinite pairs are removed before evaluation.

    MAPE ignores actual values equal to zero because
    percentage error cannot be calculated for zero targets.

    R2 returns NaN when fewer than two valid observations
    are available or when the actual target has no variation.
    """

    # ========================================================
    # CONVERT INPUTS
    # ========================================================

    actual = np.asarray(
        actual,
        dtype=float
    ).flatten()


    predicted = np.asarray(
        predicted,
        dtype=float
    ).flatten()


    # ========================================================
    # EMPTY INPUT CHECK
    # ========================================================

    if (
        actual.size == 0
        or
        predicted.size == 0
    ):

        raise ValueError(
            "Actual and predicted values "
            "cannot be empty."
        )


    # ========================================================
    # LENGTH CHECK
    # ========================================================

    if actual.size != predicted.size:

        raise ValueError(
            "Actual and predicted arrays must "
            "contain the same number of values."
        )


    # ========================================================
    # REMOVE INVALID VALUE PAIRS
    # ========================================================

    valid_mask = (
        np.isfinite(actual)
        &
        np.isfinite(predicted)
    )


    actual_clean = actual[
        valid_mask
    ]


    predicted_clean = predicted[
        valid_mask
    ]


    # ========================================================
    # VALID PAIR CHECK
    # ========================================================

    if actual_clean.size == 0:

        raise ValueError(
            "No valid actual/predicted pairs "
            "are available for evaluation."
        )


    # ========================================================
    # MAE
    # ========================================================

    mae = mean_absolute_error(
        actual_clean,
        predicted_clean
    )


    # ========================================================
    # RMSE
    # ========================================================

    mse = mean_squared_error(
        actual_clean,
        predicted_clean
    )


    rmse = np.sqrt(
        mse
    )


    # ========================================================
    # MAPE
    # ========================================================
    # Ignore zero actual values because percentage error
    # is mathematically undefined when actual == 0.
    # ========================================================

    non_zero_mask = (
        actual_clean != 0
    )


    if non_zero_mask.any():

        mape = (
            np.mean(
                np.abs(
                    (
                        actual_clean[
                            non_zero_mask
                        ]
                        -
                        predicted_clean[
                            non_zero_mask
                        ]
                    )
                    /
                    np.abs(
                        actual_clean[
                            non_zero_mask
                        ]
                    )
                )
            )
            *
            100
        )

    else:

        mape = np.nan


    # ========================================================
    # R-SQUARED
    # ========================================================

    if (
        actual_clean.size >= 2
        and
        np.unique(
            actual_clean
        ).size > 1
    ):

        r2 = r2_score(
            actual_clean,
            predicted_clean
        )

    else:

        r2 = np.nan


    # ========================================================
    # SAFE OUTPUT
    # ========================================================

    mae = float(
        mae
    )

    rmse = float(
        rmse
    )


    if np.isfinite(
        mape
    ):

        mape = float(
            mape
        )

    else:

        mape = np.nan


    if np.isfinite(
        r2
    ):

        r2 = float(
            r2
        )

    else:

        r2 = np.nan


    return (
        mae,
        rmse,
        mape,
        r2
    )