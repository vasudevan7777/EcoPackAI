-- Create Database
CREATE DATABASE IF NOT EXISTS ecopackai_data;
USE ecopackai_data;

-- Create Materials Table
CREATE TABLE IF NOT EXISTS materials (
    material_id INT AUTO_INCREMENT PRIMARY KEY,
    material_name VARCHAR(100) NOT NULL,
    material_type VARCHAR(50),
    strength_mpa DECIMAL(10, 2),
    weight_capacity_kg DECIMAL(10, 2),
    biodegradability_score INT,
    co2_emission_score DECIMAL(10, 2),
    recyclability_percent INT,
    cost_per_kg DECIMAL(10, 2)
);

-- Create Product Categories Table
CREATE TABLE IF NOT EXISTS product_categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL,
    protection_level VARCHAR(20),
    temperature_sensitive VARCHAR(10),
    moisture_sensitive VARCHAR(10)
);