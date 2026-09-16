from django import forms
from .models import (
    FoodItem,
    ProductionRecord,
    WasteRecord
)

class FoodItemForm(forms.ModelForm):

    class Meta:
        model = FoodItem

        fields = [
            'food_name',
            'category',
            'cost_per_unit',
            'selling_price',
            'is_available'
        ]

        widgets = {

            'food_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter food name'
                }
            ),

            'category': forms.Select(
                attrs={
                    'class': 'form-control'
                }
            ),

            'cost_per_unit': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Cost per unit',
                    'step': '0.01'
                }
            ),

            'selling_price': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Selling price',
                    'step': '0.01'
                }
            ),

            'is_available': forms.CheckboxInput(
                attrs={
                    'class': 'form-checkbox'
                }
            ),
        }

    def clean_food_name(self):

        food_name = self.cleaned_data['food_name']

        if len(food_name.strip()) < 2:
            raise forms.ValidationError(
                "Food name must contain at least 2 characters."
            )

        return food_name.strip()

    def clean(self):

        cleaned_data = super().clean()

        cost = cleaned_data.get('cost_per_unit')
        selling_price = cleaned_data.get('selling_price')

        if cost is not None and selling_price is not None:

            if selling_price < cost:

                raise forms.ValidationError(
                    "Selling price should not be lower "
                    "than the cost per unit."
                )

        return 


class ProductionRecordForm(forms.ModelForm):

    waste_reason = forms.ChoiceField(
    choices=WasteRecord.REASON_CHOICES,
    widget=forms.Select(
        attrs={
            'class': 'form-control'
        }
    ),
    required=False
    )

    class Meta:

        model = ProductionRecord

        fields = [
            'food',
            'record_date',
            'prepared_quantity',
            'sold_quantity',
            'remaining_quantity'
        ]

        widgets = {

            'food': forms.Select(
                attrs={
                    'class': 'form-control'
                }
            ),

            'record_date': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date'
                }
            ),

            'prepared_quantity': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'min': '1'
                }
            ),

            'sold_quantity': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'min': '0'
                }
            ),

            'remaining_quantity': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'min': '0'
                }
            ),
        }

    def clean(self):

        cleaned_data = super().clean()

        prepared = cleaned_data.get(
            'prepared_quantity'
        )

        sold = cleaned_data.get(
            'sold_quantity'
        )

        remaining = cleaned_data.get(
            'remaining_quantity'
        )

        if (
            prepared is not None
            and sold is not None
            and remaining is not None
        ):

            if sold + remaining > prepared:

                raise forms.ValidationError(
                    "Sold quantity + remaining quantity "
                    "cannot be greater than prepared quantity."
                )

        return cleaned_data