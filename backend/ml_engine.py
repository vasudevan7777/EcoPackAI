"""
ML Recommendation Engine
Handles AI-powered material recommendations using trained models
"""

import joblib
import pandas as pd
import numpy as np
import os
import logging
from typing import Dict, List, Any


class MaterialRecommendationEngine:
    """AI-powered material recommendation system"""
    
    def __init__(self):
        """Initialize ML models and scaler"""
        self.logger = logging.getLogger(__name__)
        self.cost_model = None
        self.co2_model = None
        self.scaler = None
        self.feature_names = None
        
        self._load_models()
    
    def _load_models(self):
        """Load trained ML models and preprocessing objects"""
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
            # Load models
            cost_model_path = os.path.join(base_dir, 'cost_model.pkl')
            co2_model_path = os.path.join(base_dir, 'co2_model.pkl')
            scaler_path = os.path.join(base_dir, 'dataset_preparation', 'ml_scaler.pkl')
            features_path = os.path.join(base_dir, 'dataset_preparation', 'ml_feature_names.txt')
            
            self.cost_model = joblib.load(cost_model_path)
            self.co2_model = joblib.load(co2_model_path)
            self.scaler = joblib.load(scaler_path)
            
            # Load feature names
            with open(features_path, 'r') as f:
                self.feature_names = [line.strip() for line in f.readlines()]
            
            self.logger.info("ML models loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Error loading ML models: {e}")
            raise
    
    def check_models_loaded(self):
        """Check if all models are properly loaded"""
        return all([
            self.cost_model is not None,
            self.co2_model is not None,
            self.scaler is not None,
            self.feature_names is not None
        ])
    
    def predict_metrics(self, features: Dict[str, Any]) -> Dict[str, float]:
        """
        Predict cost and CO2 emissions for given material features
        
        Args:
            features: Dictionary with material properties
        
        Returns:
            Dictionary with predictions
        """
        try:
            # Prepare features for prediction
            X = self._prepare_features(features)
            
            # Scale features
            X_scaled = self.scaler.transform(X)
            
            # Make predictions
            predicted_cost = self.cost_model.predict(X_scaled)[0]
            predicted_co2 = self.co2_model.predict(X_scaled)[0]
            
            # Categorize predictions
            cost_category = self._categorize_cost(predicted_cost)
            co2_category = self._categorize_co2(predicted_co2)
            
            return {
                'cost': float(predicted_cost),
                'co2': float(predicted_co2),
                'cost_category': cost_category,
                'co2_category': co2_category
            }
        
        except Exception as e:
            self.logger.error(f"Prediction error: {e}")
            raise
    
    def get_recommendations(self, requirements: Dict[str, Any], 
                          top_n: int = 5) -> List[Dict[str, Any]]:
        """
        Get top N material recommendations based on requirements
        
        Args:
            requirements: Product requirements dictionary
            top_n: Number of recommendations to return
        
        Returns:
            List of recommended materials with scores
        """
        try:
            # Load materials from database or file
            materials = self._load_all_materials()
            
            if not materials:
                return []
            
            # Score each material based on requirements
            scored_materials = []
            
            for material in materials:
                score = self._calculate_suitability_score(material, requirements)
                
                # Predict cost and CO2
                predictions = self.predict_metrics({
                    'strength_mpa': material['strength_mpa'],
                    'weight_capacity_kg': material['weight_capacity_kg'],
                    'biodegradability_score': material['biodegradability_score'],
                    'recyclability_percent': material['recyclability_percent'],
                    'material_type': material['material_type']
                })
                
                scored_materials.append({
                    'material_id': material['material_id'],
                    'material_name': material['material_name'],
                    'material_type': material['material_type'],
                    'suitability_score': round(score, 2),
                    'actual_cost_per_kg': float(material['cost_per_kg']),
                    'actual_co2_emission': float(material['co2_emission_score']),
                    'predicted_cost': round(predictions['cost'], 2),
                    'predicted_co2': round(predictions['co2'], 3),
                    'cost_category': predictions['cost_category'],
                    'co2_category': predictions['co2_category'],
                    'strength_mpa': float(material['strength_mpa']),
                    'weight_capacity_kg': float(material['weight_capacity_kg']),
                    'biodegradability_score': int(material['biodegradability_score']),
                    'recyclability_percent': int(material['recyclability_percent']),
                    'recommendation_reason': self._generate_recommendation_reason(
                        material, requirements, score
                    )
                })
            
            # Sort by suitability score (descending)
            scored_materials.sort(key=lambda x: x['suitability_score'], reverse=True)
            
            # Return top N
            return scored_materials[:top_n]
        
        except Exception as e:
            self.logger.error(f"Recommendation error: {e}")
            return []
    
    def _prepare_features(self, features: Dict[str, Any]) -> pd.DataFrame:
        """Prepare features for ML model prediction"""
        # Material type encoding
        material_type_map = {
            'Bio': 0, 'Bioplastic': 1, 'Composite': 2, 'Fiber': 3,
            'Glass': 4, 'Metal': 5, 'Paper': 6, 'Plastic': 7
        }
        
        strength = features.get('strength_mpa', 40)
        weight_capacity = features.get('weight_capacity_kg', 4)
        biodeg = features.get('biodegradability_score', 70)
        recycl = features.get('recyclability_percent', 70)
        co2 = features.get('co2_emission_score', 1.7)
        material_type = features.get('material_type', 'Paper')
        
        material_type_encoded = material_type_map.get(material_type, 6)
        
        # Calculate derived features
        max_co2 = 4.2
        co2_impact_index = (max_co2 - co2) / max_co2 * 100
        
        max_cost = 150
        cost_efficiency_index = (max_cost - features.get('cost_per_kg', 90)) / max_cost * 100
        
        biodeg_norm = (biodeg / 100 * 40)
        recycl_norm = (recycl / 100 * 40)
        strength_norm = ((strength - 20) / (80 - 20) * 20)
        material_suitability = biodeg_norm + recycl_norm + strength_norm
        
        # Normalized features (simplified - in production, use proper scaler)
        strength_norm_val = (strength - 40) / 10
        weight_norm_val = (weight_capacity - 4) / 1.5
        biodeg_norm_val = (biodeg - 73) / 14
        co2_norm_val = (co2 - 1.7) / 0.6
        recycl_norm_val = (recycl - 69) / 9
        
        feature_dict = {
            'strength_mpa': strength,
            'weight_capacity_kg': weight_capacity,
            'biodegradability_score': biodeg,
            'recyclability_percent': recycl,
            'co2_emission_score': co2,
            'material_type_encoded': material_type_encoded,
            'co2_impact_index': co2_impact_index,
            'cost_efficiency_index': cost_efficiency_index,
            'material_suitability_score': material_suitability,
            'strength_mpa_normalized': strength_norm_val,
            'weight_capacity_kg_normalized': weight_norm_val,
            'biodegradability_score_normalized': biodeg_norm_val,
            'co2_emission_score_normalized': co2_norm_val,
            'recyclability_percent_normalized': recycl_norm_val
        }
        
        return pd.DataFrame([feature_dict])[self.feature_names]
    
    def _calculate_suitability_score(self, material: Dict, 
                                    requirements: Dict) -> float:
        """Calculate how well a material matches requirements - improved scoring"""
        score = 0.0  # Start from 0 and add points
        
        # Strength requirement (0-25 points) - More forgiving for high requirements
        if 'strength_required' in requirements:
            strength_ratio = material['strength_mpa'] / max(requirements['strength_required'], 1)
            if strength_ratio < 0.7:
                score += 0  # Significantly insufficient
            elif strength_ratio < 0.85:
                score += 8  # Somewhat insufficient
            elif strength_ratio < 1.0:
                score += 15  # Close to requirement
            elif strength_ratio < 1.3:
                score += 23  # Meets requirement well
            else:
                score += 25  # Exceeds requirement
        else:
            score += 15  # No specific requirement
        
        # Weight capacity requirement (0-20 points)
        if 'weight_capacity' in requirements:
            capacity_ratio = material['weight_capacity_kg'] / max(requirements['weight_capacity'], 0.1)
            if capacity_ratio < 0.9:
                score += 0  # Insufficient capacity
            elif capacity_ratio < 1.2:
                score += 15  # Adequate capacity
            else:
                score += 20  # Excellent capacity
        else:
            score += 15
        
        # Cost efficiency (0-25 points) - More granular scoring
        if 'budget_constraint' in requirements:
            cost = material['cost_per_kg']
            budget = requirements['budget_constraint']
            
            if cost <= budget * 0.6:
                score += 25  # Excellent value
            elif cost <= budget * 0.8:
                score += 20  # Good value
            elif cost <= budget:
                score += 15  # Within budget
            elif cost <= budget * 1.2:
                score += 8   # Slightly over budget
            elif cost <= budget * 1.5:
                score += 3   # Moderately over budget
            else:
                score += 0   # Too expensive
        else:
            # No budget constraint - reward lower cost
            if material['cost_per_kg'] < 70:
                score += 20
            elif material['cost_per_kg'] < 100:
                score += 15
            else:
                score += 10
        
        # Biodegradability (0-15 points) - More nuanced
        biodeg = material['biodegradability_score']
        if requirements.get('biodegradability_preference') == 'high':
            score += (biodeg / 100) * 15
        elif requirements.get('biodegradability_preference') == 'medium':
            score += (biodeg / 100) * 10
        else:
            score += (biodeg / 100) * 5
        
        # Recyclability (0-15 points) - More nuanced
        recycl = material['recyclability_percent']
        if requirements.get('recyclability_preference') == 'high':
            score += (recycl / 100) * 15
        elif requirements.get('recyclability_preference') == 'medium':
            score += (recycl / 100) * 10
        else:
            score += (recycl / 100) * 5
        
        # CO2 emissions (0-20 points) - More granular scoring
        co2 = material['co2_emission_score']
        if co2 < 1.0:
            score += 20  # Excellent
        elif co2 < 1.5:
            score += 17  # Very good
        elif co2 < 2.0:
            score += 14  # Good
        elif co2 < 2.5:
            score += 10  # Moderate
        elif co2 < 3.0:
            score += 6   # Fair
        elif co2 < 3.5:
            score += 3   # Poor
        else:
            score += 0   # Very poor
        
        # Category-specific adjustments (bonus points based on material type)
        category = requirements.get('category', '')
        material_type = material.get('material_type', '')
        
        # Food & Beverage: prefer Paper, Bio, Fiber
        if category in ['Food & Beverage', 'Food']:
            if material_type in ['Paper', 'Bio', 'Fiber']:
                score += 5
            elif material_type in ['Plastic', 'Metal']:
                score -= 3
        
        # Electronics: prefer protective materials with low moisture
        elif category == 'Electronics':
            if material_type in ['Plastic', 'Composite']:
                score += 5
            if material['recyclability_percent'] > 70:
                score += 3
            # Penalize highly biodegradable materials for electronics
            if biodeg > 85:
                score -= 2
        
        # Cosmetics: prefer attractive, sustainable materials
        elif category == 'Cosmetics':
            if material_type in ['Glass', 'Bio', 'Bioplastic']:
                score += 5
            if recycl > 75:
                score += 2
        
        # Pharmaceuticals: prefer protective, sterile materials
        elif category == 'Pharmaceuticals':
            if material_type in ['Glass', 'Plastic', 'Bioplastic']:
                score += 5
            if material['strength_mpa'] > 40:
                score += 3
        
        # Industrial: prefer strength and durability
        elif category == 'Industrial':
            if material_type in ['Metal', 'Composite', 'Plastic']:
                score += 5
            if material['strength_mpa'] > 50:
                score += 5
            # Less emphasis on biodegradability for industrial
            if biodeg < 50:
                score += 2
        
        # Moisture sensitivity adjustment
        if requirements.get('moisture_sensitive') and material_type in ['Paper', 'Fiber']:
            score -= 8  # Paper-based materials not ideal for moisture-sensitive products
        
        # Temperature sensitivity
        if requirements.get('temperature_sensitive'):
            if material_type in ['Bio', 'Fiber']:
                score -= 3  # Natural materials may be less stable
            elif material_type in ['Plastic', 'Metal', 'Glass']:
                score += 2  # More stable materials
        
        # Priority-based final adjustments
        priority = requirements.get('priority', '')
        if priority == 'Cost':
            # Extra weight on cost for Cost priority
            if cost < budget * 0.7:
                score += 5
        elif priority == 'Sustainability':
            # Extra weight on environmental factors
            if biodeg > 80 and recycl > 75:
                score += 5
            if co2 < 1.3:
                score += 3
        elif priority == 'Performance':
            # Extra weight on strength and durability
            if material['strength_mpa'] > 50:
                score += 5
            if material['weight_capacity_kg'] > 5:
                score += 3
        
        return round(max(0, min(100, score)), 2)
    
    def _generate_recommendation_reason(self, material: Dict, 
                                       requirements: Dict, score: float) -> str:
        """Generate human-readable recommendation reason"""
        reasons = []
        
        if score >= 80:
            reasons.append("Excellent match for your requirements")
        elif score >= 60:
            reasons.append("Good match with minor compromises")
        else:
            reasons.append("Acceptable alternative option")
        
        if material['biodegradability_score'] >= 80:
            reasons.append("highly biodegradable")
        
        if material['recyclability_percent'] >= 80:
            reasons.append("excellent recyclability")
        
        if material['co2_emission_score'] < 1.5:
            reasons.append("low carbon footprint")
        
        if material['cost_per_kg'] < 80:
            reasons.append("cost-effective")
        
        return "; ".join(reasons)
    
    def _load_all_materials(self) -> List[Dict]:
        """Load all materials from processed data"""
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            data_path = os.path.join(base_dir, 'data', 'materials_data_100_records.csv')
            
            df = pd.read_csv(data_path)
            materials = df.to_dict('records')
            
            return materials
        
        except Exception as e:
            self.logger.error(f"Error loading materials: {e}")
            return []
    
    def _categorize_cost(self, cost: float) -> str:
        """Categorize cost into Low/Medium/High"""
        if cost < 70:
            return 'Low'
        elif cost < 110:
            return 'Medium'
        else:
            return 'High'
    
    def _categorize_co2(self, co2: float) -> str:
        """Categorize CO2 emissions into Low/Medium/High"""
        if co2 < 1.5:
            return 'Low'
        elif co2 < 2.5:
            return 'Medium'
        else:
            return 'High'
