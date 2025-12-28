import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import joblib
import warnings
import os
warnings.filterwarnings('ignore')

class ModelTraining:
    
    def __init__(self, module3_path=None):
        if module3_path is None:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(script_dir)
            module3_path = os.path.join(project_root, 'module_3')
        self.module3_path = module3_path
        self.X_train = None
        self.X_test = None
        self.y_cost_train = None
        self.y_cost_test = None
        self.y_co2_train = None
        self.y_co2_test = None
        self.cost_model = None
        self.co2_model = None
        self.cost_metrics = {}
        self.co2_metrics = {}
        
    def load_data(self):
        self.X_train = pd.read_csv(f'{self.module3_path}/ml_X_train.csv')
        self.X_test = pd.read_csv(f'{self.module3_path}/ml_X_test.csv')
        self.y_cost_train = pd.read_csv(f'{self.module3_path}/ml_y_cost_train.csv')['cost_per_kg']
        self.y_cost_test = pd.read_csv(f'{self.module3_path}/ml_y_cost_test.csv')['cost_per_kg']
        self.y_co2_train = pd.read_csv(f'{self.module3_path}/ml_y_co2_train.csv')['co2_emission_score']
        self.y_co2_test = pd.read_csv(f'{self.module3_path}/ml_y_co2_test.csv')['co2_emission_score']
        
    def train_cost_model(self):
        self.cost_model = RandomForestRegressor(
            n_estimators=50,
            max_depth=3,
            min_samples_split=3,
            min_samples_leaf=2,
            random_state=42
        )
        self.cost_model.fit(self.X_train, self.y_cost_train)
        
    def train_co2_model(self):
        self.co2_model = XGBRegressor(
            n_estimators=50,
            max_depth=3,
            learning_rate=0.05,
            random_state=42,
            reg_alpha=0.1,
            reg_lambda=1.0
        )
        self.co2_model.fit(self.X_train, self.y_co2_train)
        
    def evaluate_cost_model(self):
        y_pred = self.cost_model.predict(self.X_test)
        
        rmse = np.sqrt(mean_squared_error(self.y_cost_test, y_pred))
        mae = mean_absolute_error(self.y_cost_test, y_pred)
        r2 = r2_score(self.y_cost_test, y_pred)
        
        self.cost_metrics = {
            'RMSE': rmse,
            'MAE': mae,
            'R2_Score': r2
        }
        
        return self.cost_metrics
        
    def evaluate_co2_model(self):
        y_pred = self.co2_model.predict(self.X_test)
        
        rmse = np.sqrt(mean_squared_error(self.y_co2_test, y_pred))
        mae = mean_absolute_error(self.y_co2_test, y_pred)
        r2 = r2_score(self.y_co2_test, y_pred)
        
        self.co2_metrics = {
            'RMSE': rmse,
            'MAE': mae,
            'R2_Score': r2
        }
        
        return self.co2_metrics
        
    def create_material_ranking(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        data_path = os.path.join(project_root, 'data', 'materials_data_processed.csv')
        
        data = pd.read_csv(data_path)
        scaler = joblib.load(f'{self.module3_path}/ml_scaler.pkl')
        
        with open(f'{self.module3_path}/ml_feature_names.txt', 'r') as f:
            features = [line.strip() for line in f.readlines()]
        
        X = data[features]
        X_scaled = scaler.transform(X)
        
        cost_pred = self.cost_model.predict(X_scaled)
        co2_pred = self.co2_model.predict(X_scaled)
        
        ranking_df = pd.DataFrame({
            'material_id': data['material_id'],
            'material_name': data['material_name'],
            'predicted_cost': cost_pred,
            'predicted_co2': co2_pred,
            'actual_cost': data['cost_per_kg'],
            'actual_co2': data['co2_emission_score']
        })
        
        ranking_df['cost_rank'] = ranking_df['predicted_cost'].rank()
        ranking_df['co2_rank'] = ranking_df['predicted_co2'].rank()
        ranking_df['combined_score'] = (ranking_df['cost_rank'] + ranking_df['co2_rank']) / 2
        ranking_df['overall_rank'] = ranking_df['combined_score'].rank()
        
        ranking_df = ranking_df.sort_values('overall_rank')
        
        return ranking_df
        
    def save_models(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        joblib.dump(self.cost_model, os.path.join(script_dir, 'cost_model.pkl'))
        joblib.dump(self.co2_model, os.path.join(script_dir, 'co2_model.pkl'))
        
    def save_metrics(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        metrics_df = pd.DataFrame({
            'Model': ['Random Forest (Cost)', 'XGBoost (CO2)'],
            'RMSE': [self.cost_metrics['RMSE'], self.co2_metrics['RMSE']],
            'MAE': [self.cost_metrics['MAE'], self.co2_metrics['MAE']],
            'R2_Score': [self.cost_metrics['R2_Score'], self.co2_metrics['R2_Score']]
        })
        metrics_df.to_csv(os.path.join(script_dir, 'model_metrics.csv'), index=False)


def main():
    print("="*60)
    print("AI MODEL TRAINING")
    print("="*60)
    
    trainer = ModelTraining()
    
    print("\nLoading training and testing datasets...")
    trainer.load_data()
    print("Data loaded successfully")
    
    print("\nTraining Random Forest model for cost prediction...")
    trainer.train_cost_model()
    print("Cost model training completed")
    
    print("\nTraining XGBoost model for CO2 prediction...")
    trainer.train_co2_model()
    print("CO2 model training completed")
    
    print("\nEvaluating model performance...")
    cost_metrics = trainer.evaluate_cost_model()
    co2_metrics = trainer.evaluate_co2_model()
    
    print("\n" + "="*60)
    print("MODEL PERFORMANCE METRICS")
    print("="*60)
    print("\nCost Prediction Model (Random Forest):")
    print("  RMSE: ${:.2f}".format(cost_metrics['RMSE']))
    print("  MAE: ${:.2f}".format(cost_metrics['MAE']))
    print("  R² Score: {:.3f} ({:.1f}% variance explained)".format(
        cost_metrics['R2_Score'], cost_metrics['R2_Score']*100))
    
    print("\nCO2 Prediction Model (XGBoost):")
    print("  RMSE: {:.3f}".format(co2_metrics['RMSE']))
    print("  MAE: {:.3f}".format(co2_metrics['MAE']))
    print("  R² Score: {:.3f} ({:.1f}% variance explained)".format(
        co2_metrics['R2_Score'], co2_metrics['R2_Score']*100))
    
    print("\nGenerating material rankings based on cost and CO2...")
    ranking_df = trainer.create_material_ranking()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ranking_df.to_csv(os.path.join(script_dir, 'material_rankings.csv'), index=False)
    print("Material rankings saved successfully")
    
    print("\nSaving trained models...")
    trainer.save_models()
    print("Models saved: cost_model.pkl, co2_model.pkl")
    
    trainer.save_metrics()
    print("Metrics saved: model_metrics.csv")
    
    print("\n" + "="*60)
    print("TRAINING COMPLETED SUCCESSFULLY")
    print("="*60)
    print("\nTop 3 recommended materials:")
    top_3 = ranking_df.head(3)
    for idx, row in top_3.iterrows():
        print(f"  {int(row['overall_rank'])}. {row['material_name']}")
        
if __name__ == "__main__":
    main()
