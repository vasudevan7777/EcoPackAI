"""
Configuration settings for EcoPackAI Flask Backend
"""

import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Base configuration"""
    
    # Flask settings
    ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = os.getenv('FLASK_DEBUG', 'True') == 'True'
    SECRET_KEY = os.getenv('SECRET_KEY', 'ecopackai_secret_key_change_in_production')
    
    # Server settings
    HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    PORT = int(os.getenv('FLASK_PORT', 5000))
    
    # MySQL Database settings
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'vasu3107')
    MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'ecopackai_data')
    
    # API Security
    API_KEY = os.getenv('API_KEY', 'ecopackai_secure_key_2025')
    
    # CORS settings
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
    
    # ML Models path
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    MODELS_PATH = os.path.join(BASE_DIR, '')
    COST_MODEL = os.path.join(MODELS_PATH, 'cost_model.pkl')
    CO2_MODEL = os.path.join(MODELS_PATH, 'co2_model.pkl')
    SCALER_PATH = os.path.join(BASE_DIR, 'dataset_preparation', 'ml_scaler.pkl')
    FEATURE_NAMES_PATH = os.path.join(BASE_DIR, 'dataset_preparation', 'ml_feature_names.txt')
    
    # Pagination
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.path.join(BASE_DIR, 'backend', 'logs', 'ecopackai.log')
    
    @staticmethod
    def init_app(app):
        """Initialize application"""
        pass


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    ENV = 'development'


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    ENV = 'production'
    
    # Override with stronger security in production
    API_KEY = os.getenv('API_KEY')  # Must be set in environment
    SECRET_KEY = os.getenv('SECRET_KEY')  # Must be set in environment


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    MYSQL_DATABASE = 'ecopackai_test'


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
