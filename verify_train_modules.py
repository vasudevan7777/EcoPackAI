import pandas as pd
import joblib
import os

def verify_module4():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    required_files = [
        'train_models.py',
        'cost_model.pkl',
        'co2_model.pkl',
        'model_metrics.csv',
        'material_rankings.csv'
    ]
    
    print("="*60)
    print("MODEL TRAINING VERIFICATION")
    print("="*60)
    
    print("\n1. File Verification:")
    for file in required_files:
        file_path = os.path.join(script_dir, file)
        exists = os.path.exists(file_path)
        status = "✓" if exists else "✗"
        print(f"   {status} {file}")
    
    print("\n2. Model Verification:")
    cost_model = joblib.load(os.path.join(script_dir, 'cost_model.pkl'))
    co2_model = joblib.load(os.path.join(script_dir, 'co2_model.pkl'))
    print(f"   ✓ Cost Model: {type(cost_model).__name__}")
    print(f"   ✓ CO2 Model: {type(co2_model).__name__}")
    
    print("\n3. Metrics Verification:")
    metrics = pd.read_csv(os.path.join(script_dir, 'model_metrics.csv'))
    print(metrics.to_string(index=False))
    
    print("\n4. Rankings Verification:")
    rankings = pd.read_csv(os.path.join(script_dir, 'material_rankings.csv'))
    print(f"   Total materials ranked: {len(rankings)}")
    print(f"   Top 3 recommended materials:")
    for idx, row in rankings.head(3).iterrows():
        print(f"      {int(row['overall_rank'])}. {row['material_name']}")
    
    print("\n" + "="*60)
    print("Verification completed")
    print("="*60)

if __name__ == "__main__":
    verify_module4()
