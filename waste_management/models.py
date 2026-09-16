from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator


class FoodItem(models.Model):

    CATEGORY_CHOICES = [
        ('Breakfast', 'Breakfast'),
        ('Main Course', 'Main Course'),
        ('Snacks', 'Snacks'),
        ('Dessert', 'Dessert'),
        ('Beverage', 'Beverage'),
        ('Other', 'Other'),
    ]

    food_name = models.CharField(
        max_length=100
    )

    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES
    )

    cost_per_unit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    selling_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    is_available = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.food_name



class ProductionRecord(models.Model):

    food = models.ForeignKey(
        FoodItem,
        on_delete=models.CASCADE,
        related_name='production_records'
    )

    record_date = models.DateField()

    prepared_quantity = models.PositiveIntegerField()

    sold_quantity = models.PositiveIntegerField()

    remaining_quantity = models.PositiveIntegerField(
        default=0
    )

    wasted_quantity = models.PositiveIntegerField(
        default=0
    )

    recorded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='production_records'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def calculate_waste(self):

        self.wasted_quantity = (
            self.prepared_quantity
            - self.sold_quantity
            - self.remaining_quantity
        )

        return self.wasted_quantity

    def __str__(self):

        return (
            f"{self.food.food_name} - "
            f"{self.record_date}"
        )


class WasteRecord(models.Model):

    REASON_CHOICES = [
        ('Overproduction', 'Overproduction'),
        ('Spoilage', 'Spoilage'),
        ('Damaged', 'Damaged'),
        ('Expired', 'Expired'),
        ('Other', 'Other'),
    ]

    production_record = models.OneToOneField(
        ProductionRecord,
        on_delete=models.CASCADE,
        related_name='waste_record'
    )

    wasted_quantity = models.PositiveIntegerField()

    waste_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    reason = models.CharField(
        max_length=50,
        choices=REASON_CHOICES
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return (
            f"Waste - "
            f"{self.production_record.food.food_name}"
        )



class SurplusFood(models.Model):

    STATUS_CHOICES = [
        ('Available', 'Available'),
        ('Donated', 'Donated'),
        ('Consumed', 'Consumed'),
        ('Disposed', 'Disposed'),
    ]

    food = models.ForeignKey(
        FoodItem,
        on_delete=models.CASCADE,
        related_name='surplus_records'
    )

    quantity = models.PositiveIntegerField()

    surplus_date = models.DateField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Available'
    )

    notes = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return (
            f"{self.food.food_name} - "
            f"{self.quantity}"
        )


class Donation(models.Model):

    surplus_food = models.ForeignKey(
        SurplusFood,
        on_delete=models.CASCADE,
        related_name='donations'
    )

    quantity = models.PositiveIntegerField()

    recipient = models.CharField(
        max_length=150
    )

    donation_date = models.DateField()

    notes = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return (
            f"Donation to {self.recipient}"
        )