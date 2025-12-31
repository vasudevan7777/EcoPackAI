import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib
import warnings
import os
warnings.filterwarnings('ignore')

class MLDatasetPreparation:
    
    def __init__(self, data_path=None):
        if data_path is None:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            data_path = os.path.join(script_dir, 'data', 'materials_data_processed.csv')
        self.data = pd.read_csv(data_path)
        self.X_train = None
        self.X_test = None
        self.y_cost_train = None
        self.y_cost_test = None
        self.y_co2_train = None
        self.y_co2_test = None
        self.scaler = None
        
    def select_features(self):
        feature_columns = [
            'strength_mpa',
            'weight_capacity_kg',
            'biodegradability_score',
            'recyclability_percent',
            'co2_emission_score',
            'material_type_encoded',
            'co2_impact_index',
            'cost_efficiency_index',
            'material_suitability_score',
            'strength_mpa_normalized',
            'weight_capacity_kg_normalized',
            'biodegradability_score_normalized',
            'co2_emission_score_normalized',
            'recyclability_percent_normalized'
        ]
        
        available_features = [col for col in feature_columns if col in self.data.columns]
        self.feature_columns = available_features
        self.X = self.data[self.feature_columns].copy()
        return self.X
    
    def generate_target_variables(self):
        self.y_cost = self.data['cost_per_kg'].copy()
        self.y_co2 = self.data['co2_emission_score'].copy()
        return self.y_cost, self.y_co2
    
    def split_data(self, test_size=0.2, random_state=42):
        self.X_train, self.X_test, self.y_cost_train, self.y_cost_test = train_test_split(
            self.X, self.y_cost, test_size=test_size, random_state=random_state
        )
        
        _, _, self.y_co2_train, self.y_co2_test = train_test_split(
            self.X, self.y_co2, test_size=test_size, random_state=random_state
        )
        
        return (self.X_train, self.X_test, 
                self.y_cost_train, self.y_cost_test,
                self.y_co2_train, self.y_co2_test)
    
    def create_data_pipeline(self):
        self.scaler = StandardScaler()
        self.scaler.fit(self.X_train)
        
        X_train_scaled = self.scaler.transform(self.X_train)
        X_test_scaled = self.scaler.transform(self.X_test)
        
        self.X_train_scaled = pd.DataFrame(
            X_train_scaled, 
            columns=self.feature_columns,
            index=self.X_train.index
        )
        self.X_test_scaled = pd.DataFrame(
            X_test_scaled,
            columns=self.feature_columns,
            index=self.X_test.index
        )
        
        return self.X_train_scaled, self.X_test_scaled
    
    def save_prepared_data(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(script_dir, 'dataset_preparation')
        os.makedirs(output_dir, exist_ok=True)
        
        self.X_train_scaled.to_csv(os.path.join(output_dir, 'ml_X_train.csv'), index=False)
        self.X_test_scaled.to_csv(os.path.join(output_dir, 'ml_X_test.csv'), index=False)
        
        pd.DataFrame({'cost_per_kg': self.y_cost_train}).to_csv(os.path.join(output_dir, 'ml_y_cost_train.csv'), index=False)
        pd.DataFrame({'cost_per_kg': self.y_cost_test}).to_csv(os.path.join(output_dir, 'ml_y_cost_test.csv'), index=False)
        
        pd.DataFrame({'co2_emission_score': self.y_co2_train}).to_csv(os.path.join(output_dir, 'ml_y_co2_train.csv'), index=False)
        pd.DataFrame({'co2_emission_score': self.y_co2_test}).to_csv(os.path.join(output_dir, 'ml_y_co2_test.csv'), index=False)
        
        joblib.dump(self.scaler, os.path.join(output_dir, 'ml_scaler.pkl'))
        
        with open(os.path.join(output_dir, 'ml_feature_names.txt'), 'w') as f:
            f.write('\n'.join(self.feature_columns))


def main():
    print("="*60)
    print("ML DATASET PREPARATION")
    print("="*60)
    
    print("\nInitializing dataset preparation...")
    ml_prep = MLDatasetPreparation()
    print(f"Loaded dataset: {ml_prep.data.shape[0]} samples, {ml_prep.data.shape[1]} features")
    
    print("\nSelecting features for ML models...")
    ml_prep.select_features()
    print(f"Selected {len(ml_prep.feature_columns)} features for training")
    
    print("\nGenerating target variables...")
    ml_prep.generate_target_variables()
    print(f"  - Cost prediction target: cost_per_kg")
    print(f"    Range: ${ml_prep.y_cost.min():.2f} - ${ml_prep.y_cost.max():.2f}")
    print(f"  - CO2 prediction target: co2_emission_score")
    print(f"    Range: {ml_prep.y_co2.min():.2f} - {ml_prep.y_co2.max():.2f}")
    
    print("\nSplitting data into training and testing sets...")
    ml_prep.split_data(test_size=0.2, random_state=42)
    print(f"  Training samples: {len(ml_prep.X_train)} (80%)")
    print(f"  Testing samples: {len(ml_prep.X_test)} (20%)")
    
    print("\nApplying data scaling (StandardScaler)...")
    ml_prep.create_data_pipeline()
    print(f"  Features scaled to mean=0, std=1")
    print(f"  Scaler fitted on training data only")
    
    print("\nSaving prepared datasets...")
    ml_prep.save_prepared_data()
    print("  ✓ ml_X_train.csv (training features)")
    print("  ✓ ml_X_test.csv (testing features)")
    print("  ✓ ml_y_cost_train.csv (training cost targets)")
    print("  ✓ ml_y_cost_test.csv (testing cost targets)")
    print("  ✓ ml_y_co2_train.csv (training CO2 targets)")
    print("  ✓ ml_y_co2_test.csv (testing CO2 targets)")
    print("  ✓ ml_scaler.pkl (scaling pipeline)")
    print("  ✓ ml_feature_names.txt (feature list)")
    
    print("\n" + "="*60)
    print("DATA PREPARATION COMPLETED SUCCESSFULLY")
    print("="*60)
    print(f"\nTotal files generated: 8")
    
if __name__ == "__main__":
    main()
    