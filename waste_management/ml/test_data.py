import os
import django

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "food_waste.settings"
)

django.setup()


from data import load_production_data


df = load_production_data()


print("\n========== DATASET ==========\n")

print(df.head())

print("\n========== SHAPE ==========\n")

print(df.shape)

print("\n========== COLUMNS ==========\n")

print(df.columns.tolist())

print("\n========== DATA TYPES ==========\n")

print(df.dtypes)

print("\n========== MISSING VALUES ==========\n")

print(df.isnull().sum())

print("\n========== STATISTICS ==========\n")

print(df.describe())