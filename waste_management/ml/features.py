import pandas as pd


def create_features(df):

    df = df.copy()

    # -----------------------------------------
    # DAILY FOOD DEMAND
    # -----------------------------------------

    df = (
        df.groupby(
            [
                "food_id",
                "food__food_name",
                "record_date"
            ],
            as_index=False
        )
        .agg(
            sold_quantity=(
                "sold_quantity",
                "sum"
            ),

            prepared_quantity=(
                "prepared_quantity",
                "sum"
            ),

            remaining_quantity=(
                "remaining_quantity",
                "sum"
            ),

            wasted_quantity=(
                "wasted_quantity",
                "sum"
            )
        )
    )

    # -----------------------------------------
    # SORT
    # -----------------------------------------

    df = df.sort_values(
        [
            "food_id",
            "record_date"
        ]
    ).reset_index(drop=True)

    # -----------------------------------------
    # CALENDAR FEATURES
    # -----------------------------------------

    df["day_of_week"] = (
        df["record_date"].dt.dayofweek
    )

    df["month"] = (
        df["record_date"].dt.month
    )

    # -----------------------------------------
    # PREVIOUS DAY SALES
    # -----------------------------------------

    df["previous_day_sales"] = (
        df.groupby("food_id")[
            "sold_quantity"
        ]
        .shift(1)
    )

    # -----------------------------------------
    # 7 DAY AVERAGE
    # -----------------------------------------

    df["seven_day_average_sales"] = (
        df.groupby("food_id")[
            "sold_quantity"
        ]
        .transform(
            lambda x:
            x.shift(1)
            .rolling(
                window=7,
                min_periods=1
            )
            .mean()
        )
    )

    # -----------------------------------------
    # 14 DAY AVERAGE
    # -----------------------------------------

    df["fourteen_day_average_sales"] = (
        df.groupby("food_id")[
            "sold_quantity"
        ]
        .transform(
            lambda x:
            x.shift(1)
            .rolling(
                window=14,
                min_periods=1
            )
            .mean()
        )
    )

    # -----------------------------------------
    # REMOVE ROWS WITHOUT HISTORY
    # -----------------------------------------

    df = df.dropna(
        subset=[
            "previous_day_sales",
            "seven_day_average_sales",
            "fourteen_day_average_sales"
        ]
    )

    return df