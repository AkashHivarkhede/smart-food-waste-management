import pandas as pd

from waste_management.models import ProductionRecord


def load_production_data():

    records = (
        ProductionRecord.objects
        .select_related("food")
        .values(
            "food_id",
            "food__food_name",
            "record_date",
            "prepared_quantity",
            "sold_quantity",
            "remaining_quantity",
            "wasted_quantity",
        )
    )

    df = pd.DataFrame(records)

    if df.empty:
        return df

    # Convert date column
    df["record_date"] = pd.to_datetime(
        df["record_date"]
    )

    return df