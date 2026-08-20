import os
import random
import numpy as np
import tensorflow as tf

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import (
    Input,
    LSTM,
    Dense,
    Dropout
)
from tensorflow.keras.optimizers import Adam


# ============================================================
# REPRODUCIBILITY
# ============================================================

SEED = 42

os.environ["PYTHONHASHSEED"] = str(SEED)

random.seed(SEED)

np.random.seed(SEED)

tf.random.set_seed(SEED)


# ============================================================
# CREATE LSTM SEQUENCES
# ============================================================

def create_sequences(
    data,
    lookback
):
    """
    Convert one-dimensional time-series data into
    supervised LSTM sequences.

    Parameters
    ----------
    data : array-like
        Scaled one-dimensional historical values.

    lookback : int
        Number of previous periods used to predict
        the next period.

    Returns
    -------
    X : numpy.ndarray
        Shape:
        (samples, lookback)

    y : numpy.ndarray
        Shape:
        (samples,)
    """

    if data is None:
        raise ValueError(
            "Time-series data is None."
        )


    try:

        values = np.asarray(
            data,
            dtype=np.float32
        ).flatten()

    except Exception as e:

        raise ValueError(
            "Unable to convert the time-series data "
            "to numeric values."
        ) from e


    # ========================================================
    # LOOKBACK VALIDATION
    # ========================================================

    try:

        lookback = int(
            lookback
        )

    except (TypeError, ValueError):

        raise ValueError(
            "Lookback must be an integer."
        )


    if lookback < 1:

        raise ValueError(
            "Lookback must be at least 1."
        )


    if len(values) <= lookback:

        raise ValueError(
            "Not enough observations are available "
            "for the selected lookback period."
        )


    # ========================================================
    # FINITE VALUE CHECK
    # ========================================================

    if not np.isfinite(
        values
    ).all():

        raise ValueError(
            "Time-series data contains NaN or "
            "infinite values."
        )


    # ========================================================
    # CREATE SEQUENCES
    # ========================================================

    X = []
    y = []


    for i in range(
        lookback,
        len(values)
    ):

        sequence = values[
            i - lookback:
            i
        ]

        target = values[
            i
        ]


        X.append(
            sequence
        )

        y.append(
            target
        )


    X = np.asarray(
        X,
        dtype=np.float32
    )


    y = np.asarray(
        y,
        dtype=np.float32
    )


    # ========================================================
    # FINAL CHECK
    # ========================================================

    if len(X) == 0:

        raise ValueError(
            "No LSTM sequences were created."
        )


    return X, y


# ============================================================
# BUILD LSTM MODEL
# ============================================================

def build_lstm_model(
    lookback
):
    """
    Build and compile the RetailPulse AI LSTM model.

    Architecture
    ------------
    Input
        ↓
    LSTM (32 units)
        ↓
    Dropout (20%)
        ↓
    LSTM (16 units)
        ↓
    Dropout (20%)
        ↓
    Dense (8, ReLU)
        ↓
    Dense (1)
    """

    try:

        lookback = int(
            lookback
        )

    except (TypeError, ValueError):

        raise ValueError(
            "Lookback must be an integer."
        )


    if lookback < 1:

        raise ValueError(
            "Lookback must be at least 1."
        )


    # ========================================================
    # MODEL
    # ========================================================

    model = Sequential(
        [
            Input(
                shape=(
                    lookback,
                    1
                )
            ),

            LSTM(
                units=32,
                return_sequences=True
            ),

            Dropout(
                rate=0.20
            ),

            LSTM(
                units=16,
                return_sequences=False
            ),

            Dropout(
                rate=0.20
            ),

            Dense(
                units=8,
                activation="relu"
            ),

            Dense(
                units=1
            )
        ]
    )


    # ========================================================
    # OPTIMIZER
    # ========================================================

    optimizer = Adam(
        learning_rate=0.001
    )


    # ========================================================
    # COMPILE
    # ========================================================

    model.compile(
        optimizer=optimizer,
        loss="mse"
    )


    return model


# ============================================================
# GENERATE FUTURE FORECAST
# ============================================================

def generate_future_forecast(
    model,
    scaler,
    scaled_history,
    lookback,
    periods
):
    """
    Generate recursive multi-step future predictions
    using a trained LSTM model.

    The first future prediction uses the most recent
    historical lookback window.

    Every following prediction uses the previous
    prediction as part of the next input sequence.

    Parameters
    ----------
    model :
        Trained Keras LSTM model.

    scaler :
        Fitted MinMaxScaler.

    scaled_history : array-like
        Historical target values already transformed
        using the fitted scaler.

    lookback : int
        Number of historical periods supplied to LSTM.

    periods : int
        Number of future periods to forecast.

    Returns
    -------
    numpy.ndarray
        Future predictions transformed back into their
        original target scale.
    """

    # ========================================================
    # BASIC VALIDATION
    # ========================================================

    if model is None:

        raise ValueError(
            "A trained model is required."
        )


    if scaler is None:

        raise ValueError(
            "A fitted scaler is required."
        )


    if scaled_history is None:

        raise ValueError(
            "Scaled historical data is required."
        )


    # ========================================================
    # LOOKBACK
    # ========================================================

    try:

        lookback = int(
            lookback
        )

    except (TypeError, ValueError):

        raise ValueError(
            "Lookback must be an integer."
        )


    if lookback < 1:

        raise ValueError(
            "Lookback must be at least 1."
        )


    # ========================================================
    # FORECAST PERIODS
    # ========================================================

    try:

        periods = int(
            periods
        )

    except (TypeError, ValueError):

        raise ValueError(
            "Forecast periods must be an integer."
        )


    if periods < 1:

        raise ValueError(
            "Forecast periods must be at least 1."
        )


    # ========================================================
    # HISTORY
    # ========================================================

    history = np.asarray(
        scaled_history,
        dtype=np.float32
    ).flatten()


    if len(history) < lookback:

        raise ValueError(
            "Not enough historical values are available "
            "for the selected lookback period."
        )


    if not np.isfinite(
        history
    ).all():

        raise ValueError(
            "Scaled history contains NaN or "
            "infinite values."
        )


    # ========================================================
    # INITIAL WINDOW
    # ========================================================

    sequence = (
        history[
            -lookback:
        ]
        .copy()
    )


    scaled_predictions = []


    # ========================================================
    # RECURSIVE FORECAST
    # ========================================================

    for _ in range(
        periods
    ):

        model_input = (
            sequence
            .reshape(
                1,
                lookback,
                1
            )
        )


        prediction_output = model.predict(
            model_input,
            verbose=0
        )


        prediction_array = np.asarray(
            prediction_output
        ).flatten()


        if len(
            prediction_array
        ) == 0:

            raise ValueError(
                "The LSTM model returned an empty prediction."
            )


        prediction = float(
            prediction_array[0]
        )


        if not np.isfinite(
            prediction
        ):

            raise ValueError(
                "The LSTM model generated an invalid prediction."
            )


        scaled_predictions.append(
            prediction
        )


        # ----------------------------------------------------
        # Shift the rolling sequence and append prediction.
        # ----------------------------------------------------

        sequence = np.concatenate(
            [
                sequence[
                    1:
                ],

                np.asarray(
                    [
                        prediction
                    ],
                    dtype=np.float32
                )
            ]
        )


    # ========================================================
    # CONVERT TO NUMPY
    # ========================================================

    scaled_predictions = (
        np.asarray(
            scaled_predictions,
            dtype=np.float32
        )
        .reshape(
            -1,
            1
        )
    )


    # ========================================================
    # INVERSE SCALE
    # ========================================================

    try:

        predictions = (
            scaler
            .inverse_transform(
                scaled_predictions
            )
            .flatten()
        )

    except Exception as e:

        raise ValueError(
            "Unable to inverse-transform "
            "future predictions."
        ) from e


    # ========================================================
    # FINAL VALIDATION
    # ========================================================

    if len(
        predictions
    ) != periods:

        raise ValueError(
            "Unexpected number of future "
            "predictions generated."
        )


    if not np.isfinite(
        predictions
    ).all():

        raise ValueError(
            "Future predictions contain NaN "
            "or infinite values."
        )


    return predictions