-- RetailVision Data Warehouse

-- Create dimension tables

SET search_path TO retailvision;

-- Dimension: Date
CREATE TABLE IF NOT EXISTS dim_date (
    date_key INT PRIMARY KEY,
    full_date DATE NOT NULL UNIQUE,
    day INT NOT NULL,
    day_name VARCHAR(20) NOT NULL,
    week INT NOT NULL,
    month INT NOT NULL,
    month_name VARCHAR(20) NOT NULL,
    quarter INT NOT NULL,
    year INT NOT NULL,
    is_weekend BOOLEAN NOT NULL
);

-- Dimension: Client
CREATE TABLE IF NOT EXISTS dim_client (
    customer_key INT PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL,
    customer_unique_id VARCHAR(50) NOT NULL
);

-- Dimension: Produit
CREATE TABLE IF NOT EXISTS dim_produit (
    product_key INT PRIMARY KEY,
    product_id VARCHAR(50) NOT NULL UNIQUE,
    product_category_name VARCHAR(100),
    product_name_length INT,
    product_description_length INT,
    product_photos_qty INT,
    product_weight_g INT,
    product_length_cm INT,
    product_height_cm INT,
    product_width_cm INT
);

-- Dimension: Vendeur
CREATE TABLE IF NOT EXISTS dim_vendeur (
    seller_key INT PRIMARY KEY,
    seller_id VARCHAR(50) NOT NULL UNIQUE
);

-- Dimension: Geography
CREATE TABLE IF NOT EXISTS dim_geography (
    geography_key INT PRIMARY KEY,
    zip_code_prefix INT NOT NULL,
    city VARCHAR(100),
    state VARCHAR(50),
    region VARCHAR(100),
    latitude DECIMAL(10, 7),
    longitude DECIMAL(10, 7)
);

-- Dimension: Paiement
CREATE TABLE IF NOT EXISTS dim_paiement (
    payment_type_key INT PRIMARY KEY,
    payment_type VARCHAR(50) NOT NULL UNIQUE,
    payment_description VARCHAR(100)
);