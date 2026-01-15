"""
Utility functions for validation and calculations
"""

from typing import Dict, Tuple, Any
import re


def validate_product_input(data: Dict) -> Tuple[bool, str]:
    """
    Validate product input data
    
    Args:
        data: Product data dictionary
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Required fields
    required_fields = ['product_name', 'category']
    
    for field in required_fields:
        if field not in data or not data[field]:
            return False, f"Missing required field: {field}"
    
    # Validate product name
    product_name = data.get('product_name', '')
    if len(product_name) < 3:
        return False, "Product name must be at least 3 characters"
    if len(product_name) > 255:
        return False, "Product name is too long (max 255 characters)"
    
    # Validate weight if provided
    if 'weight' in data:
        try:
            weight = float(data['weight'])
            if weight <= 0:
                return False, "Weight must be positive"
            if weight > 10000:
                return False, "Weight is unrealistically high"
        except (ValueError, TypeError):
            return False, "Invalid weight value"
    
    # Validate dimensions if provided
    if 'dimensions' in data:
        dims = data['dimensions']
        if not isinstance(dims, dict):
            return False, "Dimensions must be an object"
        
        for key in ['length', 'width', 'height']:
            if key in dims:
                try:
                    val = float(dims[key])
                    if val <= 0:
                        return False, f"Dimension {key} must be positive"
                except (ValueError, TypeError):
                    return False, f"Invalid dimension value for {key}"
    
    # Validate fragility
    if 'fragility' in data:
        valid_fragility = ['low', 'medium', 'high']
        if data['fragility'] not in valid_fragility:
            return False, f"Fragility must be one of: {', '.join(valid_fragility)}"
    
    # Validate boolean fields
    for field in ['temperature_sensitive', 'moisture_sensitive']:
        if field in data:
            if not isinstance(data[field], bool):
                return False, f"{field} must be a boolean value"
    
    return True, ""


def calculate_environmental_score(material: Dict, quantity_kg: float = 1,
                                 transport_distance_km: float = 0,
                                 lifecycle_years: int = 1) -> Dict[str, Any]:
    """
    Calculate comprehensive environmental impact score
    
    Args:
        material: Material data dictionary
        quantity_kg: Quantity in kilograms
        transport_distance_km: Transportation distance
        lifecycle_years: Expected lifecycle in years
    
    Returns:
        Dictionary with environmental impact metrics
    """
    # Base emissions from material
    material_co2 = float(material['co2_emission_score']) * quantity_kg
    
    # Transport emissions (approximate: 0.05 kg CO2 per kg per 100 km)
    transport_co2 = (quantity_kg * transport_distance_km * 0.05) / 100
    
    # Total CO2 emissions
    total_co2 = material_co2 + transport_co2
    
    # Biodegradability factor (0-100 scale)
    biodeg_score = int(material['biodegradability_score'])
    
    # Recyclability factor (0-100 scale)
    recycl_score = int(material['recyclability_percent'])
    
    # Calculate lifecycle impact
    annual_co2 = total_co2 / max(lifecycle_years, 1)
    
    # Calculate overall environmental score (0-100, higher is better)
    # Weighted: 40% recyclability, 30% biodegradability, 30% low CO2
    co2_score = max(0, 100 - (material_co2 * 20))  # Normalize CO2 to 0-100
    environmental_score = (
        recycl_score * 0.4 +
        biodeg_score * 0.3 +
        co2_score * 0.3
    )
    
    # Categorize environmental impact
    if environmental_score >= 80:
        category = "Excellent"
        recommendation = "Highly sustainable choice"
    elif environmental_score >= 60:
        category = "Good"
        recommendation = "Environmentally friendly option"
    elif environmental_score >= 40:
        category = "Moderate"
        recommendation = "Consider alternatives if available"
    else:
        category = "Poor"
        recommendation = "Not recommended for sustainability goals"
    
    return {
        'material_name': material['material_name'],
        'material_id': material['material_id'],
        'quantity_kg': quantity_kg,
        'environmental_score': round(environmental_score, 2),
        'category': category,
        'recommendation': recommendation,
        'detailed_metrics': {
            'total_co2_emissions_kg': round(total_co2, 3),
            'material_co2_kg': round(material_co2, 3),
            'transport_co2_kg': round(transport_co2, 3),
            'annual_co2_kg': round(annual_co2, 3),
            'biodegradability_score': biodeg_score,
            'recyclability_score': recycl_score,
            'transport_distance_km': transport_distance_km,
            'lifecycle_years': lifecycle_years
        },
        'sustainability_indicators': {
            'carbon_footprint': _categorize_value(material_co2, [1, 2, 3]),
            'recyclability': _categorize_value(recycl_score, [50, 70, 85]),
            'biodegradability': _categorize_value(biodeg_score, [50, 70, 85]),
            'overall_sustainability': category
        }
    }


def _categorize_value(value: float, thresholds: list) -> str:
    """Helper to categorize a value based on thresholds"""
    if value < thresholds[0]:
        return "Excellent"
    elif value < thresholds[1]:
        return "Good"
    elif value < thresholds[2]:
        return "Moderate"
    else:
        return "Poor"


def validate_api_key(api_key: str) -> bool:
    """
    Validate API key format
    
    Args:
        api_key: API key string
    
    Returns:
        bool: True if valid format
    """
    if not api_key:
        return False
    
    # Check minimum length
    if len(api_key) < 20:
        return False
    
    # Check for alphanumeric and underscores only
    if not re.match(r'^[a-zA-Z0-9_]+$', api_key):
        return False
    
    return True


def sanitize_string(input_string: str, max_length: int = 255) -> str:
    """
    Sanitize string input to prevent injection attacks
    
    Args:
        input_string: String to sanitize
        max_length: Maximum allowed length
    
    Returns:
        Sanitized string
    """
    if not input_string:
        return ""
    
    # Remove any null bytes
    sanitized = input_string.replace('\x00', '')
    
    # Trim to max length
    sanitized = sanitized[:max_length]
    
    # Strip leading/trailing whitespace
    sanitized = sanitized.strip()
    
    return sanitized


def format_error_response(error_message: str, status_code: int = 400) -> Dict:
    """
    Format standardized error response
    
    Args:
        error_message: Error message
        status_code: HTTP status code
    
    Returns:
        Error response dictionary
    """
    from datetime import datetime
    
    return {
        'success': False,
        'error': error_message,
        'status_code': status_code,
        'timestamp': datetime.utcnow().isoformat()
    }


def format_success_response(data: Any, message: str = None) -> Dict:
    """
    Format standardized success response
    
    Args:
        data: Response data
        message: Optional success message
    
    Returns:
        Success response dictionary
    """
    from datetime import datetime
    
    response = {
        'success': True,
        'data': data,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    if message:
        response['message'] = message
    
    return response


def calculate_packaging_requirements(product_data: Dict) -> Dict:
    """
    Calculate packaging material requirements based on product specifications
    
    Args:
        product_data: Product specifications
    
    Returns:
        Dictionary with packaging requirements
    """
    weight = product_data.get('weight', 1)
    dimensions = product_data.get('dimensions', {})
    fragility = product_data.get('fragility', 'medium')
    
    # Calculate volume (if dimensions provided)
    volume = 0
    if all(k in dimensions for k in ['length', 'width', 'height']):
        volume = (dimensions['length'] * 
                 dimensions['width'] * 
                 dimensions['height']) / 1000  # Convert to liters
    
    # Determine strength requirement based on weight and fragility
    strength_map = {
        'low': 20,
        'medium': 40,
        'high': 60
    }
    base_strength = strength_map.get(fragility, 40)
    required_strength = base_strength + (weight * 2)
    
    # Determine weight capacity requirement
    required_capacity = weight * 1.5  # 50% safety margin
    
    # Protection level
    protection_level = 'high' if fragility == 'high' else 'medium' if fragility == 'medium' else 'low'
    
    return {
        'required_strength_mpa': round(required_strength, 2),
        'required_weight_capacity_kg': round(required_capacity, 2),
        'protection_level': protection_level,
        'estimated_volume_liters': round(volume, 2) if volume > 0 else None,
        'recommended_material_types': _get_recommended_types(fragility, weight)
    }


def _get_recommended_types(fragility: str, weight: float) -> list:
    """Get recommended material types based on product characteristics"""
    if fragility == 'high':
        return ['Bio', 'Paper', 'Composite']
    elif weight > 5:
        return ['Plastic', 'Composite', 'Fiber']
    else:
        return ['Paper', 'Bio', 'Bioplastic']
