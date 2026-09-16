from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from waste_management.ml.data import load_production_data
from waste_management.ml.features import create_features


# -----------------------------------------
# TRAIN MODEL
# -----------------------------------------

def train_model():

    # -------------------------------------
    # LOAD DATA
    # -------------------------------------

    df = load_production_data()

    if df.empty:
        raise ValueError(
            "No production data available."
        )

    # -------------------------------------
    # CREATE FEATURES
    # -------------------------------------

    df = create_features(df)

    # -------------------------------------
    # FEATURES
    # -------------------------------------

    categorical_features = [
        "food_id"
    ]

    numerical_features = [
        "day_of_week",
        "month",
        "previous_day_sales",
        "seven_day_average_sales",
        "fourteen_day_average_sales",
    ]

    features = (
        categorical_features
        + numerical_features
    )

    target = "sold_quantity"

    # -------------------------------------
    # REMOVE MISSING VALUES
    # -------------------------------------

    df = df.dropna(
        subset=features + [target]
    )

    # -------------------------------------
    # SORT BY DATE
    # -------------------------------------

    df = df.sort_values(
        "record_date"
    ).reset_index(
        drop=True
    )

    # -------------------------------------
    # TRAIN / TEST SPLIT
    # -------------------------------------

    split_index = int(
        len(df) * 0.8
    )

    train_df = df.iloc[
        :split_index
    ]

    test_df = df.iloc[
        split_index:
    ]

    # -------------------------------------
    # X / Y
    # -------------------------------------

    X_train = train_df[features]

    y_train = train_df[target]

    X_test = test_df[features]

    y_test = test_df[target]

    # -------------------------------------
    # PREPROCESSING
    # -------------------------------------

    preprocessor = ColumnTransformer(

        transformers=[

            (
                "food",
                OneHotEncoder(
                    handle_unknown="ignore"
                ),
                categorical_features
            ),

            (
                "numeric",
                "passthrough",
                numerical_features
            ),

        ]
    )

    # -------------------------------------
    # RANDOM FOREST
    # -------------------------------------

    model = RandomForestRegressor(

        n_estimators=300,

        max_depth=12,

        min_samples_leaf=2,

        random_state=42,

        n_jobs=-1

    )

    # -------------------------------------
    # PIPELINE
    # -------------------------------------

    pipeline = Pipeline(

        steps=[

            (
                "preprocessor",
                preprocessor
            ),

            (
                "model",
                model
            ),

        ]

    )

    # -------------------------------------
    # TRAIN
    # -------------------------------------

    pipeline.fit(
        X_train,
        y_train
    )

    # -------------------------------------
    # PREDICT
    # -------------------------------------

    predictions = pipeline.predict(
        X_test
    )

    # -------------------------------------
    # EVALUATION
    # -------------------------------------

    mae = mean_absolute_error(
        y_test,
        predictions
    )

    rmse = mean_squared_error(
        y_test,
        predictions
    ) ** 0.5

    r2 = r2_score(
        y_test,
        predictions
    )

    # -------------------------------------
    # RESULTS
    # -------------------------------------

    return {

        "model": pipeline,

        "mae": round(
            mae,
            2
        ),

        "rmse": round(
            rmse,
            2
        ),

        "r2": round(
            r2,
            2
        ),

        "train_size":
            len(train_df),

        "test_size":
            len(test_df),

        "test_data":
            test_df,

        "predictions":
            predictions,

        "features":
            features,

    }