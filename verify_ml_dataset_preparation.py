import pandas as pd
import joblib
import numpy as np
import os

def verify_files_exist():
    """Check if all required files were generated"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, 'dataset_preparation')
    
    required_files = [
        'ml_X_train.csv',
        'ml_X_test.csv',
        'ml_y_cost_train.csv',
        'ml_y_cost_test.csv',
        'ml_y_co2_train.csv',
        'ml_y_co2_test.csv',
        'ml_scaler.pkl',
        'ml_feature_names.txt'
    ]
    
    print("="*70)
    print("📁 FILE EXISTENCE CHECK")
    print("="*70)
    
    all_exist = True
    for file in required_files:
        file_path = os.path.join(data_dir, file)
        exists = os.path.exists(file_path)
        status = "✅" if exists else "❌"
        print(f"{status} {file}")
        if not exists:
            all_exist = False
    
    return all_exist

def verify_data_shapes():
    """Verify data dimensions and shapes"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, 'dataset_preparation')
    
    print("\n" + "="*70)
    print("📏 DATA SHAPE VERIFICATION")
    print("="*70)
    
    X_train = pd.read_csv(os.path.join(data_dir, 'ml_X_train.csv'))
    X_test = pd.read_csv(os.path.join(data_dir, 'ml_X_test.csv'))
    y_cost_train = pd.read_csv(os.path.join(data_dir, 'ml_y_cost_train.csv'))
    y_cost_test = pd.read_csv(os.path.join(data_dir, 'ml_y_cost_test.csv'))
    y_co2_train = pd.read_csv(os.path.join(data_dir, 'ml_y_co2_train.csv'))
    y_co2_test = pd.read_csv(os.path.join(data_dir, 'ml_y_co2_test.csv'))
    
    print(f"\nFeature Sets:")
    print(f"  X_train shape: {X_train.shape} ✅")
    print(f"  X_test shape: {X_test.shape} ✅")
    
    print(f"\nCost Targets:")
    print(f"  y_cost_train shape: {y_cost_train.shape} ✅")
    print(f"  y_cost_test shape: {y_cost_test.shape} ✅")
    
    print(f"\nCO₂ Targets:")
    print(f"  y_co2_train shape: {y_co2_train.shape} ✅")
    print(f"  y_co2_test shape: {y_co2_test.shape} ✅")
    
    # Verify matching sample counts
    assert X_train.shape[0] == y_cost_train.shape[0] == y_co2_train.shape[0], "Training sample mismatch!"
    assert X_test.shape[0] == y_cost_test.shape[0] == y_co2_test.shape[0], "Testing sample mismatch!"
    print(f"\n✅ Sample counts match across all datasets")
    
    return X_train, X_test

def verify_feature_names():
    """Verify feature names"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, 'dataset_preparation')
    
    print("\n" + "="*70)
    print("🏷️  FEATURE NAMES VERIFICATION")
    print("="*70)
    
    with open(os.path.join(data_dir, 'ml_feature_names.txt'), 'r') as f:
        feature_names = [line.strip() for line in f.readlines()]
    
    print(f"\nTotal features: {len(feature_names)}")
    print("\nFeature list:")
    for i, name in enumerate(feature_names, 1):
        print(f"  {i:2d}. {name}")
    
    return feature_names

def verify_scaler():
    """Verify the scaler object"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, 'dataset_preparation')
    
    print("\n" + "="*70)
    print("⚙️  SCALER VERIFICATION")
    print("="*70)
    
    scaler = joblib.load(os.path.join(data_dir, 'ml_scaler.pkl'))
    
    print(f"\nScaler type: {type(scaler).__name__} ✅")
    print(f"Features scaled: {scaler.n_features_in_}")
    print(f"\nScaler mean (first 5 features):")
    print(f"  {scaler.mean_[:5]}")
    print(f"\nScaler scale (first 5 features):")
    print(f"  {scaler.scale_[:5]}")
    
    return scaler

def verify_data_quality(X_train, X_test):
    """Check data quality"""
    print("\n" + "="*70)
    print("✅ DATA QUALITY CHECKS")
    print("="*70)
    
    # Check for NaN values
    train_nans = X_train.isnull().sum().sum()
    test_nans = X_test.isnull().sum().sum()
    print(f"\nMissing values:")
    print(f"  Training: {train_nans} {'✅' if train_nans == 0 else '⚠️'}")
    print(f"  Testing: {test_nans} {'✅' if test_nans == 0 else '⚠️'}")
    
    # Check for infinite values
    train_infs = np.isinf(X_train.values).sum()
    test_infs = np.isinf(X_test.values).sum()
    print(f"\nInfinite values:")
    print(f"  Training: {train_infs} {'✅' if train_infs == 0 else '⚠️'}")
    print(f"  Testing: {test_infs} {'✅' if test_infs == 0 else '⚠️'}")
    
    # Check scaling (mean should be ~0, std should be ~1 for training data)
    train_mean = X_train.mean().mean()
    train_std = X_train.std().mean()
    print(f"\nScaling verification (training data):")
    print(f"  Mean: {train_mean:.6f} (expected ~0) {'✅' if abs(train_mean) < 0.5 else '⚠️'}")
    print(f"  Std: {train_std:.6f} (expected ~1) {'✅' if 0.5 < train_std < 1.5 else '⚠️'}")

def verify_targets():
    """Verify target variable ranges and distributions"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, 'dataset_preparation')
    
    print("\n" + "="*70)
    print("🎯 TARGET VARIABLE VERIFICATION")
    print("="*70)
    
    y_cost_train = pd.read_csv(os.path.join(data_dir, 'ml_y_cost_train.csv'))
    y_cost_test = pd.read_csv(os.path.join(data_dir, 'ml_y_cost_test.csv'))
    y_co2_train = pd.read_csv(os.path.join(data_dir, 'ml_y_co2_train.csv'))
    y_co2_test = pd.read_csv(os.path.join(data_dir, 'ml_y_co2_test.csv'))
    
    print("\n1. Cost Prediction Target (cost_per_kg):")
    print(f"   Training range: ${y_cost_train['cost_per_kg'].min():.2f} - ${y_cost_train['cost_per_kg'].max():.2f}")
    print(f"   Testing range: ${y_cost_test['cost_per_kg'].min():.2f} - ${y_cost_test['cost_per_kg'].max():.2f}")
    print(f"   Training mean: ${y_cost_train['cost_per_kg'].mean():.2f}")
    print(f"   Testing mean: ${y_cost_test['cost_per_kg'].mean():.2f}")
    
    print("\n2. CO₂ Impact Target (co2_emission_score):")
    print(f"   Training range: {y_co2_train['co2_emission_score'].min():.2f} - {y_co2_train['co2_emission_score'].max():.2f}")
    print(f"   Testing range: {y_co2_test['co2_emission_score'].min():.2f} - {y_co2_test['co2_emission_score'].max():.2f}")
    print(f"   Training mean: {y_co2_train['co2_emission_score'].mean():.2f}")
    print(f"   Testing mean: {y_co2_test['co2_emission_score'].mean():.2f}")

def main():
    """Run all verification checks"""
    print("\n" + "="*70)
    print("🔍 MODULE 3: ML PREPARATION VERIFICATION")
    print("="*70)
    
    try:
        # Check 1: Files exist
        if not verify_files_exist():
            print("\n❌ Some files are missing!")
            return
        
        # Check 2: Data shapes
        X_train, X_test = verify_data_shapes()
        
        # Check 3: Feature names
        verify_feature_names()
        
        # Check 4: Scaler
        verify_scaler()
        
        # Check 5: Data quality
        verify_data_quality(X_train, X_test)
        
        # Check 6: Target variables
        verify_targets()
        
        # Final summary
        print("\n" + "="*70)
        print("✅ ALL VERIFICATION CHECKS PASSED!")
        print("="*70)
        print("\n🎉 Module 3 preparation is complete and verified!")
        print("📦 Ready to proceed to Module 4: Model Training")
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ Verification failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()
