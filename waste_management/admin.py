from django.contrib import admin

from .models import (
    FoodItem,
    ProductionRecord,
    WasteRecord,
    SurplusFood,
    Donation
)


@admin.register(FoodItem)
class FoodItemAdmin(admin.ModelAdmin):

    list_display = (
        'food_name',
        'category',
        'cost_per_unit',
        'selling_price',
        'is_available',
        'created_at'
    )

    list_filter = (
        'category',
        'is_available'
    )

    search_fields = (
        'food_name',
    )


@admin.register(ProductionRecord)
class ProductionRecordAdmin(admin.ModelAdmin):

    list_display = (
        'food',
        'record_date',
        'prepared_quantity',
        'sold_quantity',
        'remaining_quantity',
        'wasted_quantity',
        'recorded_by'
    )

    list_filter = (
        'record_date',
        'food'
    )


@admin.register(WasteRecord)
class WasteRecordAdmin(admin.ModelAdmin):

    list_display = (
        'production_record',
        'wasted_quantity',
        'waste_cost',
        'reason',
        'created_at'
    )

    list_filter = (
        'reason',
    )


@admin.register(SurplusFood)
class SurplusFoodAdmin(admin.ModelAdmin):

    list_display = (
        'food',
        'quantity',
        'surplus_date',
        'status'
    )

    list_filter = (
        'status',
        'surplus_date'
    )


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):

    list_display = (
        'surplus_food',
        'quantity',
        'recipient',
        'donation_date'
    )

    list_filter = (
        'donation_date',
    )