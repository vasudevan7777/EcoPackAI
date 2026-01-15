"""
Database Manager for MySQL operations
Handles all database connections and queries
"""

import mysql.connector
from mysql.connector import Error
from contextlib import contextmanager
import logging


class DatabaseManager:
    """Manages MySQL database connections and operations"""
    
    def __init__(self, config):
        """
        Initialize database manager with configuration
        
        Args:
            config: Flask configuration object
        """
        self.config = {
            'host': config.get('MYSQL_HOST'),
            'port': config.get('MYSQL_PORT'),
            'user': config.get('MYSQL_USER'),
            'password': config.get('MYSQL_PASSWORD'),
            'database': config.get('MYSQL_DATABASE')
        }
        self.logger = logging.getLogger(__name__)
    
    @contextmanager
    def get_connection(self):
        """
        Context manager for database connections
        Automatically handles connection closing
        """
        connection = None
        try:
            connection = mysql.connector.connect(**self.config)
            yield connection
        except Error as e:
            self.logger.error(f"Database connection error: {e}")
            raise
        finally:
            if connection and connection.is_connected():
                connection.close()
    
    def test_connection(self):
        """Test database connectivity"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
                cursor.close()
                return True
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False
    
    # =========================================================================
    # PRODUCT OPERATIONS
    # =========================================================================
    
    def insert_product(self, product_data):
        """
        Insert a new product into database
        
        Args:
            product_data: Dictionary with product information
        
        Returns:
            int: Product ID
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Create products table if not exists
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS products (
                        product_id INT AUTO_INCREMENT PRIMARY KEY,
                        product_name VARCHAR(255) NOT NULL,
                        category VARCHAR(100),
                        weight DECIMAL(10, 3),
                        dimensions JSON,
                        fragility VARCHAR(50),
                        temperature_sensitive BOOLEAN,
                        moisture_sensitive BOOLEAN,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Insert product
                query = """
                    INSERT INTO products 
                    (product_name, category, weight, dimensions, fragility, 
                     temperature_sensitive, moisture_sensitive)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                
                import json
                values = (
                    product_data.get('product_name'),
                    product_data.get('category'),
                    product_data.get('weight'),
                    json.dumps(product_data.get('dimensions', {})),
                    product_data.get('fragility'),
                    product_data.get('temperature_sensitive', False),
                    product_data.get('moisture_sensitive', False)
                )
                
                cursor.execute(query, values)
                conn.commit()
                
                product_id = cursor.lastrowid
                cursor.close()
                
                return product_id
        
        except Exception as e:
            self.logger.error(f"Error inserting product: {e}")
            raise
    
    def get_product_by_id(self, product_id):
        """Get product details by ID"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor(dictionary=True)
                
                query = "SELECT * FROM products WHERE product_id = %s"
                cursor.execute(query, (product_id,))
                
                product = cursor.fetchone()
                cursor.close()
                
                if product and product.get('dimensions'):
                    import json
                    product['dimensions'] = json.loads(product['dimensions'])
                
                return product
        
        except Exception as e:
            self.logger.error(f"Error fetching product: {e}")
            return None
    
    # =========================================================================
    # MATERIAL OPERATIONS
    # =========================================================================
    
    def get_materials(self, material_type=None, min_recyclability=None, 
                     max_cost=None, limit=50):
        """
        Get materials with optional filtering
        
        Args:
            material_type: Filter by material type
            min_recyclability: Minimum recyclability percentage
            max_cost: Maximum cost per kg
            limit: Maximum number of results
        
        Returns:
            list: List of material dictionaries
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor(dictionary=True)
                
                query = "SELECT * FROM materials WHERE 1=1"
                params = []
                
                if material_type:
                    query += " AND material_type = %s"
                    params.append(material_type)
                
                if min_recyclability:
                    query += " AND recyclability_percent >= %s"
                    params.append(min_recyclability)
                
                if max_cost:
                    query += " AND cost_per_kg <= %s"
                    params.append(max_cost)
                
                query += " ORDER BY material_id LIMIT %s"
                params.append(limit)
                
                cursor.execute(query, params)
                materials = cursor.fetchall()
                cursor.close()
                
                return materials
        
        except Exception as e:
            self.logger.error(f"Error fetching materials: {e}")
            return []
    
    def get_material_by_id(self, material_id):
        """Get material details by ID"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor(dictionary=True)
                
                query = "SELECT * FROM materials WHERE material_id = %s"
                cursor.execute(query, (material_id,))
                
                material = cursor.fetchone()
                cursor.close()
                
                return material
        
        except Exception as e:
            self.logger.error(f"Error fetching material: {e}")
            return None
    
    def get_all_materials(self):
        """Get all materials from database"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor(dictionary=True)
                
                query = "SELECT * FROM materials ORDER BY material_id"
                cursor.execute(query)
                
                materials = cursor.fetchall()
                cursor.close()
                
                return materials
        
        except Exception as e:
            self.logger.error(f"Error fetching all materials: {e}")
            return []
    
    # =========================================================================
    # STATISTICS
    # =========================================================================
    
    def get_material_statistics(self):
        """Get statistical information about materials"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor(dictionary=True)
                
                stats = {}
                
                # Total count
                cursor.execute("SELECT COUNT(*) as total FROM materials")
                stats['total_materials'] = cursor.fetchone()['total']
                
                # By material type
                cursor.execute("""
                    SELECT material_type, COUNT(*) as count 
                    FROM materials 
                    GROUP BY material_type
                """)
                stats['by_type'] = cursor.fetchall()
                
                # Average metrics
                cursor.execute("""
                    SELECT 
                        AVG(cost_per_kg) as avg_cost,
                        AVG(co2_emission_score) as avg_co2,
                        AVG(recyclability_percent) as avg_recyclability,
                        AVG(biodegradability_score) as avg_biodegradability
                    FROM materials
                """)
                stats['averages'] = cursor.fetchone()
                
                # Min/Max values
                cursor.execute("""
                    SELECT 
                        MIN(cost_per_kg) as min_cost,
                        MAX(cost_per_kg) as max_cost,
                        MIN(co2_emission_score) as min_co2,
                        MAX(co2_emission_score) as max_co2
                    FROM materials
                """)
                stats['ranges'] = cursor.fetchone()
                
                cursor.close()
                
                return stats
        
        except Exception as e:
            self.logger.error(f"Error fetching statistics: {e}")
            return {}
    
    # =========================================================================
    # CATEGORY OPERATIONS
    # =========================================================================
    
    def get_category_by_name(self, category_name):
        """Get category details by name"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor(dictionary=True)
                
                query = """
                    SELECT * FROM product_categories 
                    WHERE category_name = %s
                """
                cursor.execute(query, (category_name,))
                
                category = cursor.fetchone()
                cursor.close()
                
                return category
        
        except Exception as e:
            self.logger.error(f"Error fetching category: {e}")
            return None
    
    def store_recommendation(self, data):
        """Store recommendation"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS recommendations (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        material_name VARCHAR(255), material_type VARCHAR(100),
                        suitability_score DECIMAL(5,2), cost_per_kg DECIMAL(10,2),
                        co2_emission DECIMAL(10,3), category VARCHAR(100),
                        priority VARCHAR(50), created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                cursor.execute("""
                    INSERT INTO recommendations 
                    (material_name, material_type, suitability_score, cost_per_kg, co2_emission, category, priority)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    data.get('material_name'), data.get('material_type'),
                    data.get('suitability_score'), data.get('cost_per_kg'),
                    data.get('co2_emission'), data.get('category'), data.get('priority')
                ))
                conn.commit()
                cursor.close()
                return cursor.lastrowid
        except Exception as e:
            self.logger.error(f"Error: {e}")
            return None
    
    def get_all_recommendations(self):
        """Get all recommendations"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT * FROM recommendations ORDER BY created_at DESC")
                recs = cursor.fetchall()
                cursor.close()
                return recs
        except Exception as e:
            self.logger.error(f"Error: {e}")
            return []