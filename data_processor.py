import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
import matplotlib.pyplot as plt
import seaborn as sns

# Load your expanded datasets
materials_df = pd.read_csv('data/materials_data.csv')
categories_df = pd.read_csv('data/product_categories.csv')

print(f"Materials shape: {materials_df.shape}")  # Should be (100, 9)
print(f"Categories shape: {categories_df.shape}")  # Should be (100, 5)

# data quality checks
# Check for missing values
print("Missing values:")
print(materials_df.isnull().sum())  # Should be 0 for all

# Check for duplicates
print(f"Duplicates: {materials_df.duplicated().sum()}")  # Should be 0

# Data types
print(materials_df.dtypes)

#stastistics analysis
# Calculate statistics for numerical features
numerical_cols = ['strength_mpa', 'weight_capacity_kg', 'biodegradability_score',
                  'co2_emission_score', 'recyclability_percent', 'cost_per_kg']

# Create statistics table
stats = {}
for col in numerical_cols:
    stats[col] = {
        'mean': materials_df[col].mean(),
        'std': materials_df[col].std(),
        'min': materials_df[col].min(),
        'Q1': materials_df[col].quantile(0.25),
        'Q2(Median)': materials_df[col].quantile(0.50),
        'Q3': materials_df[col].quantile(0.75),
        'max': materials_df[col].max(),
        'IQR': materials_df[col].quantile(0.75) - materials_df[col].quantile(0.25)
    }

stats_df = pd.DataFrame(stats).T
print("\n=== STATISTICAL SUMMARY ===")
print(stats_df.round(2))

#Outlier detection 

# Detect outliers using IQR method
def detect_outliers(df, col):
    Q1 = df[col].quantile(0.25)
    Q3 = df[col].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
    return outliers

# Check all columns
print("\n=== OUTLIER DETECTION ===")
for col in numerical_cols:
    outliers = detect_outliers(materials_df, col)
    print(f"{col}: {len(outliers)} outliers detected")

#Normalize features
# Use StandardScaler for normalization
scaler = StandardScaler()
normalized_data = scaler.fit_transform(materials_df[numerical_cols])

# Add normalized columns
for i, col in enumerate(numerical_cols):
    materials_df[f'{col}_normalized'] = normalized_data[:, i]

print("\nNormalized features added (mean~0, std~1)")

# Encode Categorical Features
# Label encoding for material_type
le = LabelEncoder()
materials_df['material_type_encoded'] = le.fit_transform(materials_df['material_type'])

# Show mapping
type_mapping = dict(zip(le.classes_, le.transform(le.classes_)))
print("\nMaterial Type Encoding:")
print(type_mapping)

# One-hot encoding (alternative)
material_type_dummies = pd.get_dummies(materials_df['material_type'], prefix='type')
print(f"\nOne-hot encoded features: {material_type_dummies.columns.tolist()}")

#Feature Engineering
#CO₂ Impact Index (0-100)
max_co2 = materials_df['co2_emission_score'].max()
materials_df['co2_impact_index'] = (
    (max_co2 - materials_df['co2_emission_score']) / max_co2 * 100
).round(2)

print(f"\nCO₂ Impact Index:")
print(f"  Mean: {materials_df['co2_impact_index'].mean():.2f}")
print(f"  Range: {materials_df['co2_impact_index'].min():.2f} - {materials_df['co2_impact_index'].max():.2f}")

#Cost Efficiency Index (0-100)
max_cost = materials_df['cost_per_kg'].max()
materials_df['cost_efficiency_index'] = (
    (max_cost - materials_df['cost_per_kg']) / max_cost * 100
).round(2)

print(f"\nCost Efficiency Index:")
print(f"  Mean: {materials_df['cost_efficiency_index'].mean():.2f}")

#Material Suitability Score (0-100)
# Weighted combination of biodegradability, recyclability, and strength
biodeg_norm = (materials_df['biodegradability_score'] / 100 * 40)
recycl_norm = (materials_df['recyclability_percent'] / 100 * 40)
strength_norm = ((materials_df['strength_mpa'] - materials_df['strength_mpa'].min()) /
                 (materials_df['strength_mpa'].max() - materials_df['strength_mpa'].min()) * 20)

materials_df['material_suitability_score'] = (biodeg_norm + recycl_norm + strength_norm).round(2)

print(f"\nMaterial Suitability Score:")
print(f"  Mean: {materials_df['material_suitability_score'].mean():.2f}")
print(f"  Formula: 40% biodegradability + 40% recyclability + 20% strength")

# Save cleaned and processed data
materials_df.to_csv('materials_data_processed.csv', index=False)
print("\n✅ Saved processed data")

#Visualizations

# Set style
sns.set_style("whitegrid")

# 1. Distribution plots
fig, axes = plt.subplots(2, 3, figsize=(16, 10))
axes = axes.ravel()
for idx, col in enumerate(numerical_cols):
    axes[idx].hist(materials_df[col], bins=20, color='skyblue', edgecolor='black')
    axes[idx].set_title(f'{col}\nMean: {materials_df[col].mean():.2f}')
    axes[idx].set_xlabel(col)
    axes[idx].set_ylabel('Frequency')
plt.tight_layout()
plt.savefig('distribution_plots.png', dpi=300)
print("✅ Saved distribution_plots.png")

# 2. Correlation heatmap
plt.figure(figsize=(12, 10))
correlation = materials_df[numerical_cols].corr()
sns.heatmap(correlation, annot=True, fmt='.2f', cmap='coolwarm', center=0)
plt.title('Feature Correlation Matrix')
plt.tight_layout()
plt.savefig('correlation_heatmap.png', dpi=300)
print("✅ Saved correlation_heatmap.png")

# 3. Box plots for outliers
fig, axes = plt.subplots(2, 3, figsize=(16, 10))
axes = axes.ravel()
for idx, col in enumerate(numerical_cols):
    axes[idx].boxplot(materials_df[col], vert=True)
    axes[idx].set_title(f'{col} - Outlier Detection')
    axes[idx].set_ylabel(col)
plt.tight_layout()
plt.savefig('boxplots_outliers.png', dpi=300)
print("✅ Saved boxplots_outliers.png")

# 4. Material type analysis
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
materials_df['material_type'].value_counts().plot(kind='bar', ax=axes[0], color='lightcoral')
axes[0].set_title('Count by Material Type')
axes[0].set_ylabel('Count')

materials_df.groupby('material_type')['cost_per_kg'].mean().plot(kind='bar', ax=axes[1], color='lightgreen')
axes[1].set_title('Average Cost by Material Type')
axes[1].set_ylabel('Cost ($/kg)')
plt.tight_layout()
plt.savefig('material_type_analysis.png', dpi=300)
print("✅ Saved material_type_analysis.png")