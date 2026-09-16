from datetime import date, timedelta
import random

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from waste_management.models import (
    FoodItem,
    ProductionRecord,
    WasteRecord,
)


class Command(BaseCommand):

    help = "Generate realistic historical data for ML training"

    def handle(self, *args, **kwargs):

        foods = list(
            FoodItem.objects.filter(
                is_available=True
            )
        )

        if not foods:
            self.stdout.write(
                self.style.ERROR(
                    "No food items found."
                )
            )
            return

        user = (
            User.objects
            .filter(is_active=True)
            .first()
        )

        if not user:
            self.stdout.write(
                self.style.ERROR(
                    "No active user found."
                )
            )
            return

        # -----------------------------------------
        # FOOD-SPECIFIC BASE DEMAND
        # -----------------------------------------

        base_demands = {}

        for index, food in enumerate(foods):

            # Give every food a different
            # normal demand level.

            base_demands[food.id] = (
                60 + (index * 8)
            )

        # -----------------------------------------
        # DATE RANGE
        # -----------------------------------------

        end_date = date.today()

        start_date = (
            end_date - timedelta(days=365)
        )

        current_date = start_date

        created_count = 0

        # -----------------------------------------
        # GENERATE DATA
        # -----------------------------------------

        while current_date <= end_date:

            day_of_week = current_date.weekday()

            month = current_date.month

            for food in foods:

                base_demand = base_demands[
                    food.id
                ]

                # ---------------------------------
                # WEEKDAY EFFECT
                # ---------------------------------

                if day_of_week == 0:
                    # Monday
                    demand_factor = 0.90

                elif day_of_week == 1:
                    # Tuesday
                    demand_factor = 0.95

                elif day_of_week == 2:
                    # Wednesday
                    demand_factor = 1.00

                elif day_of_week == 3:
                    # Thursday
                    demand_factor = 1.05

                elif day_of_week == 4:
                    # Friday
                    demand_factor = 1.15

                elif day_of_week == 5:
                    # Saturday
                    demand_factor = 1.30

                else:
                    # Sunday
                    demand_factor = 1.20

                # ---------------------------------
                # MONTH / SEASON EFFECT
                # ---------------------------------

                if month in [4, 5, 6]:
                    seasonal_factor = 0.95

                elif month in [10, 11, 12]:
                    seasonal_factor = 1.08

                else:
                    seasonal_factor = 1.00

                # ---------------------------------
                # RANDOM DAILY VARIATION
                # ---------------------------------

                random_variation = random.uniform(
                    0.90,
                    1.10
                )

                expected_demand = (
                    base_demand
                    * demand_factor
                    * seasonal_factor
                    * random_variation
                )

                sold_quantity = max(
                    1,
                    round(expected_demand)
                )

                # ---------------------------------
                # PREPARE EXTRA FOOD
                # ---------------------------------

                extra_quantity = random.randint(
                    5,
                    15
                )

                prepared_quantity = (
                    sold_quantity
                    + extra_quantity
                )

                # ---------------------------------
                # REMAINING
                # ---------------------------------

                remaining_quantity = random.randint(
                    0,
                    min(
                        8,
                        extra_quantity
                    )
                )

                # ---------------------------------
                # WASTE
                # ---------------------------------

                wasted_quantity = (
                    prepared_quantity
                    - sold_quantity
                    - remaining_quantity
                )

                # ---------------------------------
                # CREATE PRODUCTION
                # ---------------------------------

                record = ProductionRecord.objects.create(

                    food=food,

                    record_date=current_date,

                    prepared_quantity=prepared_quantity,

                    sold_quantity=sold_quantity,

                    remaining_quantity=remaining_quantity,

                    wasted_quantity=wasted_quantity,

                    recorded_by=user

                )

                # ---------------------------------
                # CREATE WASTE RECORD
                # ---------------------------------

                if wasted_quantity > 0:

                    reason = random.choice([
                        "Overproduction",
                        "Spoilage",
                        "Damaged",
                        "Expired",
                        "Other",
                    ])

                    waste_cost = (
                        wasted_quantity
                        * food.cost_per_unit
                    )

                    WasteRecord.objects.create(

                        production_record=record,

                        wasted_quantity=wasted_quantity,

                        waste_cost=waste_cost,

                        reason=reason

                    )

                created_count += 1

            current_date += timedelta(days=1)

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully created "
                f"{created_count} realistic ML records."
            )
        )