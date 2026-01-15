import mysql.connector
import csv
import os
from dotenv import load_dotenv

# Load environment variables from backend/.env file
load_dotenv(os.path.join(os.path.dirname(__file__), 'backend', '.env'))

# Get database credentials from environment variables
MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
MYSQL_USER = os.getenv('MYSQL_USER', 'root')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'ecopackai_data')

conn = mysql.connector.connect(
    host=MYSQL_HOST,
    user=MYSQL_USER,
    password=MYSQL_PASSWORD,
    database=MYSQL_DATABASE
)

cursor = conn.cursor()

script_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(script_dir, 'data')

print("="*60)
print("DATABASE LOADING")
print("="*60)

print("\nClearing existing data...")
cursor.execute("DELETE FROM materials")
cursor.execute("DELETE FROM product_categories")
print("Existing data cleared")

print("\nLoading materials data...")
materials_file = os.path.join(data_dir, 'materials_data_100_records.csv')
with open(materials_file, 'r') as file:
    csv_reader = csv.DictReader(file)
    for row in csv_reader:
        cursor.execute("""
            INSERT INTO materials (
                material_id, material_name, material_type, strength_mpa, 
                weight_capacity_kg, biodegradability_score, co2_emission_score, 
                recyclability_percent, cost_per_kg
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            row['material_id'], row['material_name'], row['material_type'],
            row['strength_mpa'], row['weight_capacity_kg'], 
            row['biodegradability_score'], row['co2_emission_score'],
            row['recyclability_percent'], row['cost_per_kg']
        ))

print(f"Loaded {cursor.rowcount} materials successfully")


print("\nLoading product categories data...")
categories_file = os.path.join(data_dir, 'product_categories_100_records.csv')
with open(categories_file, 'r') as file:
    csv_reader = csv.DictReader(file)
    for row in csv_reader:
        cursor.execute("""
            INSERT INTO product_categories (
                category_id, category_name, protection_level, 
                temperature_sensitive, moisture_sensitive
            ) VALUES (%s, %s, %s, %s, %s)
        """, (
            row['category_id'], row['category_name'], row['protection_level'],
            row['temperature_sensitive'], row['moisture_sensitive']
        ))

print(f"Loaded {cursor.rowcount} categories successfully")


conn.commit()
print("\nDatabase transaction committed")


cursor.execute("SELECT COUNT(*) FROM materials")
materials_count = cursor.fetchone()[0]
print(f"\nVerification:")
print(f"  Total materials in database: {materials_count}")


cursor.execute("SELECT COUNT(*) FROM product_categories")
categories_count = cursor.fetchone()[0]
print(f"  Total product categories in database: {categories_count}")


cursor.close()
conn.close()

print("\n" + "="*60)
print("DATA LOADING COMPLETED SUCCESSFULLY")
print("="*60)
print(f"\nDatabase: ecopackai_data")
print(f"Materials loaded: {materials_count}")
print(f"Categories loaded: {categories_count}")
print("\nRun 'python view_data.py' to view the loaded data")