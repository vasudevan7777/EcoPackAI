from flask import Flask, request, jsonify
from flask_cors import CORS
from functools import wraps
import os
from datetime import datetime
 
from config import Config
from database import DatabaseManager
from ml_engine import MaterialRecommendationEngine
from utils import validate_product_input, calculate_environmental_score
import os

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)
CORS(app)  # Enable CORS for frontend integration

# Initialize components
db_manager = DatabaseManager(app.config)
ml_engine = MaterialRecommendationEngine()

# =============================================================================
# AUTHENTICATION & SECURITY
# =============================================================================

def require_api_key(f):
    """Decorator to require API key for secure endpoints"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        
        # In production, validate against database or environment variable
        valid_api_key = app.config.get('API_KEY', 'ecopackai_secure_key_2025')
        
        if not api_key or api_key != valid_api_key:
            return jsonify({
                'success': False,
                'error': 'Unauthorized: Invalid or missing API key',
                'timestamp': datetime.utcnow().isoformat()
            }), 401
        
        return f(*args, **kwargs)
    return decorated_function


# =============================================================================
# HEALTH CHECK & STATUS
# =============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Check API health status"""
    try:
        # Test database connection
        db_status = db_manager.test_connection()
        
        # Test ML models
        ml_status = ml_engine.check_models_loaded()
        
        return jsonify({
            'success': True,
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'services': {
                'database': 'connected' if db_status else 'disconnected',
                'ml_models': 'loaded' if ml_status else 'not_loaded',
                'api_version': '1.0.0'
            }
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500


# =============================================================================
# PRODUCT INPUT HANDLING
# =============================================================================

@app.route('/api/products', methods=['POST'])
@require_api_key
def create_product():
    """
    Handle product input and store in database
    
    Request Body:
    {
        "product_name": "Electronics Device",
        "category": "Electronics",
        "weight": 0.5,
        "dimensions": {"length": 15, "width": 10, "height": 5},
        "fragility": "high",
        "temperature_sensitive": true,
        "moisture_sensitive": true
    }
    """
    try:
        data = request.get_json()
        
        # Validate input
        is_valid, error_message = validate_product_input(data)
        if not is_valid:
            return jsonify({
                'success': False,
                'error': error_message,
                'timestamp': datetime.utcnow().isoformat()
            }), 400
        
        # Store product in database
        product_id = db_manager.insert_product(data)
        
        return jsonify({
            'success': True,
            'message': 'Product created successfully',
            'data': {
                'product_id': product_id,
                'product_name': data.get('product_name')
            },
            'timestamp': datetime.utcnow().isoformat()
        }), 201
    
    except Exception as e:
        app.logger.error(f"Error creating product: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'details': str(e) if app.debug else None,
            'timestamp': datetime.utcnow().isoformat()
        }), 500


@app.route('/api/products/<int:product_id>', methods=['GET'])
@require_api_key
def get_product(product_id):
    """Retrieve product details by ID"""
    try:
        product = db_manager.get_product_by_id(product_id)
        
        if not product:
            return jsonify({
                'success': False,
                'error': 'Product not found',
                'timestamp': datetime.utcnow().isoformat()
            }), 404
        
        return jsonify({
            'success': True,
            'data': product,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500


# =============================================================================
# AI MATERIAL RECOMMENDATION
# =============================================================================

@app.route('/api/recommendations', methods=['POST'])
@require_api_key
def get_recommendations():
    """
    Get AI-powered material recommendations for a product
    
    Request Body:
    {
        "product_requirements": {
            "strength_required": 30,
            "weight_capacity": 5,
            "biodegradability_preference": "high",
            "budget_constraint": 100,
            "recyclability_preference": "high"
        },
        "top_n": 5
    }
    """
    try:
        data = request.get_json()
        requirements = data.get('product_requirements', {})
        top_n = data.get('top_n', 5)
        
        # Get recommendations from ML engine
        recommendations = ml_engine.get_recommendations(requirements, top_n=top_n)
        
        if not recommendations:
            return jsonify({
                'success': False,
                'error': 'No suitable materials found',
                'timestamp': datetime.utcnow().isoformat()
            }), 404
        
        # Store for analytics
        if recommendations:
            top = recommendations[0]
            db_manager.store_recommendation({
                'material_name': top.get('material_name'),
                'material_type': top.get('material_type'),
                'suitability_score': top.get('suitability_score'),
                'cost_per_kg': top.get('actual_cost_per_kg'),
                'co2_emission': top.get('actual_co2_emission'),
                'category': requirements.get('category', 'N/A'),
                'priority': requirements.get('priority', 'balanced')
            })
        
        return jsonify({
            'success': True,
            'message': f'Top {len(recommendations)} materials recommended',
            'data': {
                'recommendations': recommendations,
                'total_found': len(recommendations)
            },
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    
    except Exception as e:
        app.logger.error(f"Error getting recommendations: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to generate recommendations',
            'details': str(e) if app.debug else None,
            'timestamp': datetime.utcnow().isoformat()
        }), 500


@app.route('/api/recommendations/predict', methods=['POST'])
@require_api_key
def predict_material_metrics():
    """
    Predict cost and CO2 emissions for specific material features
    
    Request Body:
    {
        "features": {
            "strength_mpa": 35.47,
            "weight_capacity_kg": 4.82,
            "biodegradability_score": 90,
            "recyclability_percent": 82,
            "material_type": "Paper"
        }
    }
    """
    try:
        data = request.get_json()
        features = data.get('features', {})
        
        # Predict using ML models
        predictions = ml_engine.predict_metrics(features)
        
        return jsonify({
            'success': True,
            'data': {
                'predicted_cost_per_kg': round(predictions['cost'], 2),
                'predicted_co2_emission': round(predictions['co2'], 3),
                'cost_category': predictions['cost_category'],
                'co2_category': predictions['co2_category']
            },
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    
    except Exception as e:
        app.logger.error(f"Error predicting metrics: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Prediction failed',
            'details': str(e) if app.debug else None,
            'timestamp': datetime.utcnow().isoformat()
        }), 500


# =============================================================================
# ENVIRONMENTAL SCORE COMPUTATION
# =============================================================================

@app.route('/api/environmental-score', methods=['POST'])
@require_api_key
def compute_environmental_score():
    """
    Calculate comprehensive environmental impact score
    
    Request Body:
    {
        "material_id": 3,
        "quantity_kg": 10,
        "transport_distance_km": 500,
        "lifecycle_years": 2
    }
    """
    try:
        data = request.get_json()
        material_id = data.get('material_id')
        
        # Get material data from database
        material = db_manager.get_material_by_id(material_id)
        
        if not material:
            return jsonify({
                'success': False,
                'error': 'Material not found',
                'timestamp': datetime.utcnow().isoformat()
            }), 404
        
        # Calculate environmental score
        score_data = calculate_environmental_score(
            material=material,
            quantity_kg=data.get('quantity_kg', 1),
            transport_distance_km=data.get('transport_distance_km', 0),
            lifecycle_years=data.get('lifecycle_years', 1)
        )
        
        return jsonify({
            'success': True,
            'data': score_data,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    
    except Exception as e:
        app.logger.error(f"Error computing environmental score: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Score calculation failed',
            'details': str(e) if app.debug else None,
            'timestamp': datetime.utcnow().isoformat()
        }), 500


# =============================================================================
# MATERIALS DATABASE QUERIES
# =============================================================================

@app.route('/api/materials', methods=['GET'])
@require_api_key
def get_all_materials():
    """Get all available materials with optional filtering"""
    try:
        # Get query parameters
        material_type = request.args.get('type')
        min_recyclability = request.args.get('min_recyclability', type=int)
        max_cost = request.args.get('max_cost', type=float)
        limit = request.args.get('limit', 50, type=int)
        
        # Fetch materials from database
        materials = db_manager.get_materials(
            material_type=material_type,
            min_recyclability=min_recyclability,
            max_cost=max_cost,
            limit=limit
        )
        
        return jsonify({
            'success': True,
            'data': {
                'materials': materials,
                'count': len(materials)
            },
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500


@app.route('/api/materials/<int:material_id>', methods=['GET'])
@require_api_key
def get_material(material_id):
    """Get detailed information about a specific material"""
    try:
        material = db_manager.get_material_by_id(material_id)
        
        if not material:
            return jsonify({
                'success': False,
                'error': 'Material not found',
                'timestamp': datetime.utcnow().isoformat()
            }), 404
        
        return jsonify({
            'success': True,
            'data': material,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500


# =============================================================================
# STATISTICS & ANALYTICS
# =============================================================================

@app.route('/api/statistics/materials', methods=['GET'])
@require_api_key
def get_material_statistics():
    """Get statistical analysis of materials database"""
    try:
        stats = db_manager.get_material_statistics()
        
        return jsonify({
            'success': True,
            'data': stats,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500


@app.route('/api/analytics', methods=['GET'])
@require_api_key
def get_analytics():
    """Get analytics data"""
    try:
        recs = db_manager.get_all_recommendations()
        
        if not recs:
            return jsonify({
                'success': True,
                'data': {'total_requests': 0, 'co2_saved': 0, 'cost_saved': 0, 'recommendations': []}
            }), 200
        
        total = len(recs)
        # Convert to float to avoid Decimal type issues
        avg_co2 = sum(float(r.get('co2_emission', 0)) for r in recs) / total
        avg_cost = sum(float(r.get('cost_per_kg', 0)) for r in recs) / total
        co2_saved = (3.0 - avg_co2) * total
        cost_saved = (100.0 - avg_cost) * total
        co2_pct = ((3.0 - avg_co2) / 3.0) * 100
        
        materials = {}
        for r in recs:
            mat = r.get('material_type', 'Unknown')
            materials[mat] = materials.get(mat, 0) + 1
        
        return jsonify({
            'success': True,
            'data': {
                'total_requests': total,
                'co2_saved': round(co2_saved, 2),
                'cost_saved': round(cost_saved, 2),
                'co2_reduction_pct': round(co2_pct, 2),
                'avg_co2': round(avg_co2, 2),
                'avg_cost': round(avg_cost, 2),
                'material_usage': materials,
                'recommendations': recs[-50:]
            }
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# =============================================================================
# ERROR HANDLERS
# =============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found',
        'timestamp': datetime.utcnow().isoformat()
    }), 404


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'success': False,
        'error': 'Method not allowed',
        'timestamp': datetime.utcnow().isoformat()
    }), 405


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error',
        'timestamp': datetime.utcnow().isoformat()
    }), 500


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)


'''
if __name__ == '__main__':
    print("="*60)
    print("🚀 ECOPACKAI BACKEND API SERVER")
    print("="*60)
    print(f"Environment: {app.config['ENV']}")
    print(f"Debug Mode: {app.config['DEBUG']}")
    print(f"Host: {app.config['HOST']}")
    print(f"Port: {app.config['PORT']}")
    print("="*60)
    
    app.run(
        host=app.config['HOST'],
        port=app.config['PORT'],
        debug=app.config['DEBUG']
    )
'''