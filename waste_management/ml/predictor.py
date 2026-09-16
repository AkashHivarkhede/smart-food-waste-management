import pandas as pd

from waste_management.ml.data import load_production_data
from waste_management.ml.features import create_features
from waste_management.ml.model import train_model


def predict_demand(food_id, target_date):

    # -----------------------------------------
    # LOAD HISTORICAL DATA
    # -----------------------------------------

    df = load_production_data()

    if df.empty:
        raise ValueError(
            "No production data available."
        )

    # -----------------------------------------
    # CREATE FEATURES
    # -----------------------------------------

    feature_df = create_features(df)

    # -----------------------------------------
    # TRAIN MODEL
    # -----------------------------------------

    results = train_model()

    model = results["model"]

    # -----------------------------------------
    # FOOD HISTORY
    # -----------------------------------------

    food_history = feature_df[
        feature_df["food_id"] == food_id
    ].copy()

    if food_history.empty:
        raise ValueError(
            "No historical data available "
            "for this food."
        )

    # -----------------------------------------
    # TARGET DATE
    # -----------------------------------------

    target_date = pd.Timestamp(
        target_date
    )

    # -----------------------------------------
    # SORT HISTORY
    # -----------------------------------------

    food_history = food_history.sort_values(
        "record_date"
    )

    # -----------------------------------------
    # PREVIOUS DAY SALES
    # -----------------------------------------

    previous_day_sales = (
        food_history.iloc[-1]["sold_quantity"]
    )

    # -----------------------------------------
    # 7 DAY AVERAGE
    # -----------------------------------------

    seven_day_average = (
        food_history
        .tail(7)["sold_quantity"]
        .mean()
    )

    # -----------------------------------------
    # 14 DAY AVERAGE
    # -----------------------------------------

    fourteen_day_average = (
        food_history
        .tail(14)["sold_quantity"]
        .mean()
    )

    # -----------------------------------------
    # CREATE PREDICTION DATA
    # -----------------------------------------

    prediction_data = pd.DataFrame({

        "food_id": [
            food_id
        ],

        "day_of_week": [
            target_date.dayofweek
        ],

        "month": [
            target_date.month
        ],

        "previous_day_sales": [
            previous_day_sales
        ],

        "seven_day_average_sales": [
            seven_day_average
        ],

        "fourteen_day_average_sales": [
            fourteen_day_average
        ],

    })

    # -----------------------------------------
    # PREDICT SALES
    # -----------------------------------------

    prediction = model.predict(
        prediction_data
    )[0]

    prediction = max(
        0,
        round(prediction)
    )

    # -----------------------------------------
    # HISTORICAL WASTE ANALYSIS
    # -----------------------------------------

    raw_food_history = df[
        df["food_id"] == food_id
    ].copy()

    total_prepared = (
        raw_food_history[
            "prepared_quantity"
        ].sum()
    )

    total_waste = (
        raw_food_history[
            "wasted_quantity"
        ].sum()
    )

    # -----------------------------------------
    # WASTE RATE
    # -----------------------------------------

    if total_prepared > 0:

        waste_rate = (
            total_waste
            / total_prepared
        )

    else:

        waste_rate = 0

    # -----------------------------------------
    # BASE SAFETY BUFFER
    # -----------------------------------------

    base_buffer_percentage = 0.10

    # -----------------------------------------
    # REDUCE BUFFER FOR HIGH WASTE
    # -----------------------------------------

    waste_adjustment = min(
        waste_rate,
        0.50
    )

    adjusted_buffer_percentage = (
        base_buffer_percentage
        * (1 - waste_adjustment)
    )

    # -----------------------------------------
    # SAFETY BUFFER
    # -----------------------------------------

    safety_buffer = max(
        1,
        round(
            prediction
            * adjusted_buffer_percentage
        )
    )

    # -----------------------------------------
    # RECOMMENDED PREPARATION
    # -----------------------------------------

    recommended_quantity = (
        prediction
        + safety_buffer
    )

    # -----------------------------------------
    # RESULT
    # -----------------------------------------

    return {

        "food_id":
            food_id,

        "target_date":
            target_date.date(),

        "predicted_sales":
            prediction,

        "waste_rate":
            round(
                waste_rate * 100,
                2
            ),

        "safety_buffer":
            safety_buffer,

        "recommended_quantity":
            recommended_quantity,

    }