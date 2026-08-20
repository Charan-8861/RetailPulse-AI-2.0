import os
import streamlit as st
import pandas as pd
import numpy as np

from sklearn.preprocessing import MinMaxScaler

from tensorflow.keras.callbacks import (
    EarlyStopping,
    ReduceLROnPlateau
)

from utils.preprocessing import (
    create_time_series,
    validate_forecasting_data
)

from utils.forecasting import (
    create_sequences,
    build_lstm_model,
    generate_future_forecast
)

from utils.evaluation import evaluate_model


# ============================================================
# HELPERS
# ============================================================

def safe_column(value):

    if value is None:
        return None

    if str(value).strip().lower() == "none":
        return None

    return value


def clear_forecast_results():

    keys = [
        "lstm_trained",
        "mae",
        "rmse",
        "mape",
        "r2",
        "comparison_df",
        "future_df",
        "loss_df",
        "combined_df",
        "model_comparison",
        "best_model",
        "best_mape",
        "percentage_change",
        "epochs_used",
        "forecast_frequency",
        "forecast_target_used"
    ]

    for key in keys:

        if key in st.session_state:
            del st.session_state[key]

    st.session_state.lstm_trained = False


def safe_float(value):

    try:

        value = float(value)

        if not np.isfinite(value):
            return None

        return value

    except (TypeError, ValueError):
        return None


def build_model_comparison(rows):

    comparison = pd.DataFrame(rows)

    if comparison.empty:
        return comparison

    numeric_columns = [
        "MAE",
        "RMSE",
        "MAPE (%)",
        "R2"
    ]

    for column in numeric_columns:

        if column in comparison.columns:

            comparison[column] = pd.to_numeric(
                comparison[column],
                errors="coerce"
            )

    # Replace infinite values.
    comparison = comparison.replace(
        [np.inf, -np.inf],
        np.nan
    )

    # Prefer MAPE when it is available.
    valid_mape = comparison[
        comparison["MAPE (%)"].notna()
    ]

    if not valid_mape.empty:

        comparison = comparison.sort_values(
            by=["MAPE (%)", "RMSE"],
            ascending=[True, True],
            na_position="last"
        )

    else:

        # RMSE fallback if MAPE cannot be calculated.
        comparison = comparison.sort_values(
            by="RMSE",
            ascending=True,
            na_position="last"
        )

    return comparison.reset_index(
        drop=True
    )


def create_future_dates(
    last_date,
    periods,
    frequency_label
):

    last_date = pd.to_datetime(
        last_date
    )

    if frequency_label == "Weekly":

        # Preserve a weekly forecasting sequence.
        return pd.date_range(
            start=last_date + pd.Timedelta(days=7),
            periods=periods,
            freq="7D"
        )

    return pd.date_range(
        start=last_date + pd.offsets.MonthEnd(1),
        periods=periods,
        freq="ME"
    )


# ============================================================
# FORECASTING PAGE
# ============================================================

def show_forecasting():

    # ========================================================
    # HEADER
    # ========================================================

    st.title(
        "🤖 Demand Forecasting"
    )

    st.caption(
        "Train an LSTM forecasting model, compare it with "
        "baseline models and estimate future retail demand."
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
            "confirm the configuration before training."
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


    # ========================================================
    # DATE VALIDATION
    # ========================================================

    if (
        date_column is None
        or
        date_column not in df.columns
    ):

        st.error(
            "A valid Date column is required for forecasting."
        )

        return


    # ========================================================
    # TARGET SELECTION
    # ========================================================

    target_options = []


    if (
        sales_column
        and
        sales_column in df.columns
    ):

        target_options.append(
            sales_column
        )


    if (
        quantity_column
        and
        quantity_column in df.columns
        and
        quantity_column not in target_options
    ):

        target_options.append(
            quantity_column
        )


    if not target_options:

        st.error(
            "No valid Sales or Quantity forecasting target "
            "is available."
        )

        return


    # ========================================================
    # CONFIGURATION
    # ========================================================

    st.subheader(
        "⚙️ Forecast Configuration"
    )


    config1, config2 = st.columns(2)


    # --------------------------------------------------------
    # PREVIOUS TARGET
    # --------------------------------------------------------

    previous_target = st.session_state.get(
        "forecast_target_used"
    )

    if previous_target in target_options:

        target_index = target_options.index(
            previous_target
        )

    else:

        target_index = 0


    with config1:

        forecast_target = st.selectbox(
            "Forecast Target",
            target_options,
            index=target_index,
            key="forecast_target_selector"
        )


    # --------------------------------------------------------
    # PREVIOUS FREQUENCY
    # --------------------------------------------------------

    frequency_options = [
        "Weekly",
        "Monthly"
    ]

    previous_frequency = st.session_state.get(
        "forecast_frequency"
    )

    if previous_frequency in frequency_options:

        frequency_index = frequency_options.index(
            previous_frequency
        )

    else:

        frequency_index = 0


    with config2:

        frequency_label = st.selectbox(
            "Forecast Frequency",
            frequency_options,
            index=frequency_index,
            key="forecast_frequency_selector"
        )


    frequency = (
        "W"
        if frequency_label == "Weekly"
        else "ME"
    )


    # ========================================================
    # CREATE TIME SERIES
    # ========================================================

    try:

        time_series = create_time_series(
            df,
            date_column,
            forecast_target,
            frequency
        )

    except Exception as e:

        st.error(
            "Unable to create the forecasting time series."
        )

        st.exception(e)

        return


    # ========================================================
    # TIME SERIES VALIDATION
    # ========================================================

    if (
        time_series is None
        or
        not isinstance(
            time_series,
            pd.DataFrame
        )
        or
        time_series.empty
    ):

        st.error(
            "No usable time-series observations were generated."
        )

        return


    if (
        date_column not in time_series.columns
        or
        forecast_target not in time_series.columns
    ):

        st.error(
            "The generated time series does not contain the "
            "required Date and forecasting target columns."
        )

        return


    # ========================================================
    # CLEAN GENERATED TIME SERIES
    # ========================================================

    time_series = time_series.copy()


    time_series[
        date_column
    ] = pd.to_datetime(
        time_series[
            date_column
        ],
        errors="coerce"
    )


    time_series[
        forecast_target
    ] = pd.to_numeric(
        time_series[
            forecast_target
        ],
        errors="coerce"
    )


    time_series = (
        time_series
        .dropna(
            subset=[
                date_column,
                forecast_target
            ]
        )
        .sort_values(
            date_column
        )
        .reset_index(
            drop=True
        )
    )


    observations = len(
        time_series
    )


    # ========================================================
    # FORECAST DATA VALIDATION
    # ========================================================

    st.subheader(
        "🔍 Forecasting Dataset Validation"
    )


    try:

        valid_forecast, messages = (
            validate_forecasting_data(
                df,
                date_column,
                forecast_target
            )
        )

    except Exception as e:

        st.error(
            "Forecast validation failed."
        )

        st.exception(e)

        return


    if valid_forecast:

        st.success(
            "✅ Dataset is suitable for time-series forecasting."
        )

    else:

        st.error(
            "The dataset does not currently satisfy the "
            "forecasting requirements."
        )

        for message in messages or []:

            st.warning(
                str(message)
            )

        return


    # ========================================================
    # DATA SUMMARY
    # ========================================================

    s1, s2, s3 = st.columns(3)


    with s1:

        st.metric(
            "Historical Observations",
            f"{observations:,}"
        )


    with s2:

        st.metric(
            "Forecast Target",
            forecast_target
        )


    with s3:

        st.metric(
            "Frequency",
            frequency_label
        )


    # ========================================================
    # MINIMUM OBSERVATIONS
    # ========================================================

    if observations < 20:

        st.error(
            f"Only {observations} aggregated observations are "
            "available.\n\nAt least 20 observations are "
            "recommended before training the forecasting models."
        )

        return


    # ========================================================
    # HISTORICAL SERIES
    # ========================================================

    st.subheader(
        "📈 Historical Time Series"
    )


    st.line_chart(
        time_series,
        x=date_column,
        y=forecast_target,
        use_container_width=True
    )


    st.divider()


    # ========================================================
    # MODEL SETTINGS
    # ========================================================

    st.subheader(
        "🧠 LSTM Model Settings"
    )


    max_lookback = min(
        20,
        max(
            3,
            observations // 4
        )
    )


    if frequency_label == "Weekly":

        default_lookback = 8

    else:

        default_lookback = 6


    default_lookback = min(
        default_lookback,
        max_lookback
    )


    setting1, setting2, setting3 = (
        st.columns(3)
    )


    with setting1:

        lookback = st.slider(
            "Lookback Periods",
            min_value=3,
            max_value=max_lookback,
            value=default_lookback,
            key="forecast_lookback"
        )


    with setting2:

        epochs = st.slider(
            "Maximum Epochs",
            min_value=20,
            max_value=200,
            value=100,
            step=10,
            key="forecast_epochs"
        )


    with setting3:

        if frequency_label == "Weekly":

            forecast_periods = st.selectbox(
                "Future Forecast Periods",
                [4, 8, 12],
                index=1,
                key="forecast_periods_weekly"
            )

        else:

            forecast_periods = st.selectbox(
                "Future Forecast Periods",
                [3, 6, 12],
                index=1,
                key="forecast_periods_monthly"
            )


    st.caption(
        "EarlyStopping is enabled automatically. Training may "
        "stop before the maximum number of epochs when validation "
        "loss stops improving."
    )


    # ========================================================
    # RESULT COMPATIBILITY
    # ========================================================

    result_target = st.session_state.get(
        "forecast_target_used"
    )

    result_frequency = st.session_state.get(
        "forecast_frequency"
    )


    if st.session_state.get(
        "lstm_trained",
        False
    ):

        if (
            result_target != forecast_target
            or
            result_frequency != frequency_label
        ):

            st.info(
                "The displayed controls differ from the previously "
                "trained forecast. Train again to generate results "
                "for the new target/frequency."
            )


    # ========================================================
    # BUTTONS
    # ========================================================

    train_col, clear_col = st.columns(
        [3, 1]
    )


    with train_col:

        train_button = st.button(
            "🚀 Train LSTM & Compare Models",
            type="primary",
            use_container_width=True,
            key="train_forecasting_model"
        )


    with clear_col:

        clear_button = st.button(
            "🗑️ Clear Results",
            use_container_width=True,
            key="clear_forecasting_results"
        )


    if clear_button:

        clear_forecast_results()

        st.rerun()


    # ========================================================
    # TRAINING
    # ========================================================

    if train_button:

        # Remove old model results before starting a new run.
        clear_forecast_results()

        try:

            with st.spinner(
                "Training LSTM and evaluating forecasting models..."
            ):

                # =================================================
                # VALUES
                # =================================================

                values = (
                    pd.to_numeric(
                        time_series[
                            forecast_target
                        ],
                        errors="coerce"
                    )
                    .to_numpy(
                        dtype=float
                    )
                    .reshape(
                        -1,
                        1
                    )
                )


                valid_mask = np.isfinite(
                    values.flatten()
                )


                values = values[
                    valid_mask
                ]


                time_series = (
                    time_series
                    .loc[
                        valid_mask
                    ]
                    .reset_index(
                        drop=True
                    )
                )


                # =================================================
                # FINAL DATA CHECK
                # =================================================

                if len(values) < 20:

                    st.error(
                        "Too few valid observations remain "
                        "after cleaning."
                    )

                    return


                # =================================================
                # TRAIN / TEST SPLIT
                # =================================================

                split_point = int(
                    len(values) * 0.80
                )


                if split_point <= lookback:

                    st.error(
                        "The training portion is too small for "
                        "the selected lookback period."
                    )

                    return


                train_values = values[
                    :split_point
                ]


                # =================================================
                # SCALE
                # =================================================

                scaler = MinMaxScaler()


                # IMPORTANT:
                # Fit only on training data to prevent leakage.
                scaler.fit(
                    train_values
                )


                scaled_values = (
                    scaler
                    .transform(
                        values
                    )
                    .flatten()
                )


                # =================================================
                # CREATE SEQUENCES
                # =================================================

                X, y = create_sequences(
                    scaled_values,
                    lookback
                )


                if (
                    X is None
                    or
                    y is None
                    or
                    len(X) == 0
                ):

                    st.error(
                        "No LSTM sequences could be generated."
                    )

                    return


                indexes = np.arange(
                    lookback,
                    len(values)
                )


                # Protect against an unexpected sequence helper.
                sequence_count = min(
                    len(X),
                    len(y),
                    len(indexes)
                )


                X = X[
                    :sequence_count
                ]

                y = y[
                    :sequence_count
                ]

                indexes = indexes[
                    :sequence_count
                ]


                train_mask = (
                    indexes < split_point
                )


                test_mask = (
                    indexes >= split_point
                )


                X_train = X[
                    train_mask
                ]

                y_train = y[
                    train_mask
                ]


                X_test = X[
                    test_mask
                ]

                y_test = y[
                    test_mask
                ]


                # =================================================
                # SEQUENCE VALIDATION
                # =================================================

                if (
                    len(X_train) < 10
                    or
                    len(X_test) < 3
                ):

                    st.error(
                        "Not enough training/test sequences were "
                        "created.\n\nTry reducing the lookback "
                        "period or use more historical observations."
                    )

                    return


                # =================================================
                # RESHAPE
                # =================================================

                X_train = X_train.reshape(
                    X_train.shape[0],
                    X_train.shape[1],
                    1
                )


                X_test = X_test.reshape(
                    X_test.shape[0],
                    X_test.shape[1],
                    1
                )


                # =================================================
                # BUILD LSTM
                # =================================================

                model = build_lstm_model(
                    lookback
                )


                # =================================================
                # CALLBACKS
                # =================================================

                early_stop = EarlyStopping(
                    monitor="val_loss",
                    patience=12,
                    restore_best_weights=True
                )


                reduce_lr = ReduceLROnPlateau(
                    monitor="val_loss",
                    factor=0.5,
                    patience=5,
                    min_lr=0.00001
                )


                # =================================================
                # TRAIN
                # =================================================

                history = model.fit(
                    X_train,
                    y_train,
                    epochs=epochs,
                    batch_size=8,
                    validation_split=0.20,
                    callbacks=[
                        early_stop,
                        reduce_lr
                    ],
                    shuffle=False,
                    verbose=0
                )


                epochs_used = len(
                    history.history.get(
                        "loss",
                        []
                    )
                )


                # =================================================
                # TEST PREDICTIONS
                # =================================================

                pred_scaled = model.predict(
                    X_test,
                    verbose=0
                )


                predicted = (
                    scaler
                    .inverse_transform(
                        pred_scaled.reshape(
                            -1,
                            1
                        )
                    )
                    .flatten()
                )


                actual = (
                    scaler
                    .inverse_transform(
                        y_test.reshape(
                            -1,
                            1
                        )
                    )
                    .flatten()
                )


                # =================================================
                # LSTM METRICS
                # =================================================

                (
                    mae,
                    rmse,
                    mape,
                    r2
                ) = evaluate_model(
                    actual,
                    predicted
                )


                # =================================================
                # TEST DATES
                # =================================================

                test_indexes = indexes[
                    test_mask
                ]


                test_dates = (
                    time_series[
                        date_column
                    ]
                    .iloc[
                        test_indexes
                    ]
                    .reset_index(
                        drop=True
                    )
                )


                comparison_df = pd.DataFrame(
                    {
                        date_column:
                            test_dates,

                        "Actual":
                            actual,

                        "Predicted":
                            predicted
                    }
                )


                # =================================================
                # TRAINING HISTORY
                # =================================================

                training_loss = history.history.get(
                    "loss",
                    []
                )


                validation_loss = history.history.get(
                    "val_loss",
                    []
                )


                loss_df = pd.DataFrame(
                    {
                        "Training Loss":
                            training_loss,

                        "Validation Loss":
                            validation_loss
                    }
                )


                # =================================================
                # FUTURE FORECAST
                # =================================================

                future_predictions = (
                    generate_future_forecast(
                        model,
                        scaler,
                        scaled_values,
                        lookback,
                        forecast_periods
                    )
                )


                future_predictions = np.asarray(
                    future_predictions,
                    dtype=float
                ).flatten()


                if len(
                    future_predictions
                ) != forecast_periods:

                    st.error(
                        "The forecasting model returned an "
                        "unexpected number of future predictions."
                    )

                    return


                # =================================================
                # FUTURE DATES
                # =================================================

                last_date = pd.to_datetime(
                    time_series[
                        date_column
                    ].iloc[-1]
                )


                future_dates = create_future_dates(
                    last_date,
                    forecast_periods,
                    frequency_label
                )


                future_df = pd.DataFrame(
                    {
                        "Forecast Date":
                            future_dates,

                        "Forecast":
                            future_predictions
                    }
                )


                # =================================================
                # HISTORICAL + FUTURE CHART
                # =================================================

                historical_chart = (
                    time_series[
                        [
                            date_column,
                            forecast_target
                        ]
                    ]
                    .rename(
                        columns={
                            forecast_target:
                                "Historical"
                        }
                    )
                )


                future_chart = pd.DataFrame(
                    {
                        date_column:
                            future_dates,

                        "Forecast":
                            future_predictions
                    }
                )


                combined_df = pd.merge(
                    historical_chart,
                    future_chart,
                    on=date_column,
                    how="outer"
                )


                combined_df = (
                    combined_df
                    .sort_values(
                        date_column
                    )
                    .reset_index(
                        drop=True
                    )
                )


                # =================================================
                # FORECAST CHANGE
                # =================================================

                current_value = safe_float(
                    time_series[
                        forecast_target
                    ].iloc[-1]
                )


                final_forecast = safe_float(
                    future_predictions[-1]
                )


                if (
                    current_value is not None
                    and
                    final_forecast is not None
                    and
                    current_value != 0
                ):

                    percentage_change = (
                        (
                            final_forecast
                            -
                            current_value
                        )
                        /
                        abs(
                            current_value
                        )
                    ) * 100

                else:

                    percentage_change = None


                # =================================================
                # MODEL COMPARISON
                # =================================================

                rows = []


                # -------------------------------------------------
                # LSTM
                # -------------------------------------------------

                rows.append(
                    {
                        "Model":
                            "LSTM",

                        "MAE":
                            mae,

                        "RMSE":
                            rmse,

                        "MAPE (%)":
                            mape,

                        "R2":
                            r2
                    }
                )


                # -------------------------------------------------
                # NAIVE FORECAST
                # -------------------------------------------------

                if len(actual) >= 2:

                    naive_actual = actual[
                        1:
                    ]

                    naive_predictions = actual[
                        :-1
                    ]


                    (
                        naive_mae,
                        naive_rmse,
                        naive_mape,
                        naive_r2
                    ) = evaluate_model(
                        naive_actual,
                        naive_predictions
                    )


                    rows.append(
                        {
                            "Model":
                                "Naive Forecast",

                            "MAE":
                                naive_mae,

                            "RMSE":
                                naive_rmse,

                            "MAPE (%)":
                                naive_mape,

                            "R2":
                                naive_r2
                        }
                    )


                # -------------------------------------------------
                # SEASONAL NAIVE
                # -------------------------------------------------

                seasonal_period = (
                    52
                    if frequency_label == "Weekly"
                    else 12
                )


                historical_values = (
                    time_series[
                        forecast_target
                    ]
                    .to_numpy(
                        dtype=float
                    )
                )


                test_start = int(
                    test_indexes[0]
                )


                seasonal_actual = []
                seasonal_predictions = []


                for i in range(
                    test_start,
                    len(
                        historical_values
                    )
                ):

                    previous_season = (
                        i
                        -
                        seasonal_period
                    )


                    if previous_season >= 0:

                        actual_value = (
                            historical_values[
                                i
                            ]
                        )

                        seasonal_value = (
                            historical_values[
                                previous_season
                            ]
                        )


                        if (
                            np.isfinite(
                                actual_value
                            )
                            and
                            np.isfinite(
                                seasonal_value
                            )
                        ):

                            seasonal_actual.append(
                                actual_value
                            )

                            seasonal_predictions.append(
                                seasonal_value
                            )


                if len(
                    seasonal_actual
                ) >= 3:

                    (
                        seasonal_mae,
                        seasonal_rmse,
                        seasonal_mape,
                        seasonal_r2
                    ) = evaluate_model(
                        np.asarray(
                            seasonal_actual
                        ),
                        np.asarray(
                            seasonal_predictions
                        )
                    )


                    rows.append(
                        {
                            "Model":
                                "Seasonal Naive",

                            "MAE":
                                seasonal_mae,

                            "RMSE":
                                seasonal_rmse,

                            "MAPE (%)":
                                seasonal_mape,

                            "R2":
                                seasonal_r2
                        }
                    )


                # =================================================
                # MODEL COMPARISON TABLE
                # =================================================

                model_comparison = (
                    build_model_comparison(
                        rows
                    )
                )


                if model_comparison.empty:

                    st.error(
                        "Model comparison could not be generated."
                    )

                    return


                best_model = (
                    model_comparison
                    .iloc[0][
                        "Model"
                    ]
                )


                best_mape_value = (
                    model_comparison
                    .iloc[0][
                        "MAPE (%)"
                    ]
                )


                best_mape = safe_float(
                    best_mape_value
                )


                # =================================================
                # SAVE OUTPUT FILES
                # =================================================

                os.makedirs(
                    "models",
                    exist_ok=True
                )


                os.makedirs(
                    "outputs/forecasts",
                    exist_ok=True
                )


                os.makedirs(
                    "outputs/metrics",
                    exist_ok=True
                )


                model.save(
                    "models/lstm_model.keras"
                )


                future_df.to_csv(
                    "outputs/forecasts/latest_forecast.csv",
                    index=False
                )


                model_comparison.to_csv(
                    "outputs/metrics/model_comparison.csv",
                    index=False
                )


                # =================================================
                # SESSION STATE
                # =================================================

                st.session_state.mae = (
                    safe_float(
                        mae
                    )
                )

                st.session_state.rmse = (
                    safe_float(
                        rmse
                    )
                )

                st.session_state.mape = (
                    safe_float(
                        mape
                    )
                )

                st.session_state.r2 = (
                    safe_float(
                        r2
                    )
                )


                st.session_state.comparison_df = (
                    comparison_df
                )

                st.session_state.loss_df = (
                    loss_df
                )

                st.session_state.future_df = (
                    future_df
                )

                st.session_state.combined_df = (
                    combined_df
                )

                st.session_state.model_comparison = (
                    model_comparison
                )


                st.session_state.best_model = (
                    best_model
                )

                st.session_state.best_mape = (
                    best_mape
                )

                st.session_state.percentage_change = (
                    percentage_change
                )

                st.session_state.epochs_used = (
                    epochs_used
                )

                st.session_state.forecast_frequency = (
                    frequency_label
                )

                st.session_state.forecast_target_used = (
                    forecast_target
                )


                st.session_state.lstm_trained = True


            st.success(
                "✅ LSTM training and model comparison "
                "completed successfully."
            )


        except Exception as e:

            # Prevent partially completed/old model results
            # from being interpreted as a successful run.
            clear_forecast_results()

            st.error(
                "Model training failed."
            )

            st.exception(e)


    # ========================================================
    # RESULTS CHECK
    # ========================================================

    if not st.session_state.get(
        "lstm_trained",
        False
    ):

        return


    st.divider()

    st.header(
        "📊 Forecasting Results"
    )


    # ========================================================
    # RESULT METRICS
    # ========================================================

    r1, r2, r3, r4 = st.columns(4)


    mae = st.session_state.get(
        "mae"
    )

    rmse = st.session_state.get(
        "rmse"
    )

    mape = st.session_state.get(
        "mape"
    )

    r2_value = st.session_state.get(
        "r2"
    )


    with r1:

        st.metric(
            "MAE",
            (
                f"{mae:,.2f}"
                if mae is not None
                else "N/A"
            )
        )


    with r2:

        st.metric(
            "RMSE",
            (
                f"{rmse:,.2f}"
                if rmse is not None
                else "N/A"
            )
        )


    with r3:

        st.metric(
            "MAPE",
            (
                f"{mape:.2f}%"
                if mape is not None
                else "N/A"
            )
        )


    with r4:

        st.metric(
            "R²",
            (
                f"{r2_value:.3f}"
                if r2_value is not None
                else "N/A"
            )
        )


    # ========================================================
    # TRAINING INFORMATION
    # ========================================================

    epochs_used = st.session_state.get(
        "epochs_used"
    )


    if epochs_used is not None:

        st.caption(
            f"LSTM training completed after "
            f"{epochs_used} epoch(s)."
        )


    # ========================================================
    # ACTUAL VS PREDICTED
    # ========================================================

    comparison_df = st.session_state.get(
        "comparison_df"
    )


    if (
        isinstance(
            comparison_df,
            pd.DataFrame
        )
        and
        not comparison_df.empty
    ):

        st.subheader(
            "📈 Actual vs Predicted"
        )


        chart_date_column = (
            date_column
            if date_column in comparison_df.columns
            else comparison_df.columns[0]
        )


        st.line_chart(
            comparison_df
            .set_index(
                chart_date_column
            )[
                [
                    "Actual",
                    "Predicted"
                ]
            ],
            use_container_width=True
        )


    # ========================================================
    # TRAINING LOSS
    # ========================================================

    loss_df = st.session_state.get(
        "loss_df"
    )


    if (
        isinstance(
            loss_df,
            pd.DataFrame
        )
        and
        not loss_df.empty
    ):

        st.subheader(
            "📉 Training vs Validation Loss"
        )


        st.line_chart(
            loss_df,
            use_container_width=True
        )


    # ========================================================
    # MODEL COMPARISON
    # ========================================================

    model_comparison = (
        st.session_state.get(
            "model_comparison"
        )
    )


    if (
        isinstance(
            model_comparison,
            pd.DataFrame
        )
        and
        not model_comparison.empty
    ):

        st.subheader(
            "🧪 Forecasting Model Comparison"
        )


        display_comparison = (
            model_comparison.copy()
        )


        st.dataframe(
            display_comparison.style.format(
                {
                    "MAE":
                        "{:,.2f}",

                    "RMSE":
                        "{:,.2f}",

                    "MAPE (%)":
                        "{:.2f}",

                    "R2":
                        "{:.3f}"
                },
                na_rep="N/A"
            ),
            use_container_width=True,
            hide_index=True
        )


        best_model = st.session_state.get(
            "best_model"
        )


        best_mape = st.session_state.get(
            "best_mape"
        )


        if best_model:

            if best_mape is not None:

                st.success(
                    f"🏆 Best tested model: "
                    f"**{best_model}** — "
                    f"MAPE: **{best_mape:.2f}%**"
                )

            else:

                st.success(
                    f"🏆 Best tested model: "
                    f"**{best_model}**"
                )


        if (
            best_model
            and
            best_model != "LSTM"
        ):

            st.warning(
                "The LSTM was not the strongest model on the "
                "historical test period. The future LSTM forecast "
                "should therefore be interpreted cautiously.\n\n"
                "This comparison demonstrates that a complex "
                "deep-learning model does not automatically "
                "outperform simpler forecasting baselines."
            )


    # ========================================================
    # HISTORICAL + FORECAST
    # ========================================================

    combined_df = st.session_state.get(
        "combined_df"
    )


    if (
        isinstance(
            combined_df,
            pd.DataFrame
        )
        and
        not combined_df.empty
    ):

        st.subheader(
            "🔮 Historical Data + Future Forecast"
        )


        chart_date_column = (
            date_column
            if date_column in combined_df.columns
            else combined_df.columns[0]
        )


        chart_df = (
            combined_df
            .set_index(
                chart_date_column
            )
        )


        chart_columns = [
            column
            for column in [
                "Historical",
                "Forecast"
            ]
            if column in chart_df.columns
        ]


        if chart_columns:

            st.line_chart(
                chart_df[
                    chart_columns
                ],
                use_container_width=True
            )


    # ========================================================
    # FUTURE FORECAST TABLE
    # ========================================================

    future_df = st.session_state.get(
        "future_df"
    )


    if (
        isinstance(
            future_df,
            pd.DataFrame
        )
        and
        not future_df.empty
    ):

        st.subheader(
            "📅 Future Forecast"
        )


        st.dataframe(
            future_df,
            use_container_width=True,
            hide_index=True
        )


        forecast_csv = (
            future_df
            .to_csv(
                index=False
            )
            .encode(
                "utf-8"
            )
        )


        st.download_button(
            "⬇️ Download Forecast CSV",
            data=forecast_csv,
            file_name="retailpulse_forecast.csv",
            mime="text/csv",
            use_container_width=False,
            key="download_forecast_csv"
        )


    # ========================================================
    # FORECAST DIRECTION
    # ========================================================

    forecast_change = st.session_state.get(
        "percentage_change"
    )


    if forecast_change is not None:

        st.subheader(
            "📌 Forecast Direction"
        )


        f1, f2 = st.columns(2)


        with f1:

            st.metric(
                "Projected Change",
                f"{forecast_change:+.2f}%"
            )


        with f2:

            if forecast_change > 10:

                st.success(
                    "Demand is forecast to increase noticeably. "
                    "Review inventory availability, supplier "
                    "capacity and staffing requirements."
                )

            elif forecast_change > 0:

                st.info(
                    "Demand is forecast to increase moderately. "
                    "Maintain adequate inventory while monitoring "
                    "actual demand."
                )

            elif forecast_change < -10:

                st.warning(
                    "Demand is forecast to decline noticeably. "
                    "Review purchasing levels and avoid unnecessary "
                    "inventory accumulation."
                )

            elif forecast_change < 0:

                st.warning(
                    "Demand is forecast to decline moderately. "
                    "Consider conservative replenishment until "
                    "the trend becomes clearer."
                )

            else:

                st.info(
                    "The forecast indicates relatively stable demand."
                )


    # ========================================================
    # FORECAST DETAILS
    # ========================================================

    result_frequency = st.session_state.get(
        "forecast_frequency"
    )

    result_target = st.session_state.get(
        "forecast_target_used"
    )


    if (
        result_frequency
        or
        result_target
    ):

        st.subheader(
            "ℹ️ Forecast Details"
        )


        detail1, detail2 = st.columns(2)


        with detail1:

            st.metric(
                "Forecast Target",
                result_target or "N/A"
            )


        with detail2:

            st.metric(
                "Forecast Frequency",
                result_frequency or "N/A"
            )


    # ========================================================
    # DISCLAIMER
    # ========================================================

    st.divider()


    st.caption(
        "Forecasts are estimates based on historical patterns. "
        "They should support business decisions rather than be "
        "treated as guaranteed future outcomes."
    )