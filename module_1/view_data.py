import mysql.connector
from tabulate import tabulate


password = "vasu3107"  
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password=password,
    database="ecopackai_data"
)

cursor = conn.cursor()

print("="*60)
print("MODULE 1: DATABASE VIEW")
print("="*60)

print("\n=== MATERIALS TABLE (First 10 records) ===")
cursor.execute("SELECT * FROM materials LIMIT 10")
materials = cursor.fetchall()
columns = [desc[0] for desc in cursor.description]
print(tabulate(materials, headers=columns, tablefmt="grid"))

cursor.execute("SELECT COUNT(*) FROM materials")
total_materials = cursor.fetchone()[0]
print(f"\nTotal materials in database: {total_materials}")


print("\n" + "="*60)
print("\n=== PRODUCT CATEGORIES TABLE ===")
cursor.execute("SELECT * FROM product_categories")
categories = cursor.fetchall()
columns = [desc[0] for desc in cursor.description]
print(tabulate(categories, headers=columns, tablefmt="grid"))

cursor.execute("SELECT COUNT(*) FROM product_categories")
total_categories = cursor.fetchone()[0]
print(f"\nTotal categories in database: {total_categories}")

print("\n" + "="*60)
print("DATABASE VIEW COMPLETED")
print("="*60)

cursor.close()
conn.close()