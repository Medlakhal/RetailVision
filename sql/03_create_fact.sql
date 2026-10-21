-- Create fact table

SET search_path TO retailvision;

CREATE TABLE IF NOT EXISTS fact_ventes (
    sales_key INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    date_key INT NOT NULL,
    customer_key INT NOT NULL,
    product_key INT NOT NULL,
    seller_key INT NOT NULL,
    customer_geo_key INT NOT NULL,
    seller_geo_key INT NOT NULL,

    order_id VARCHAR(50) NOT NULL,
    order_item_id INT NOT NULL,
    order_status VARCHAR(30) NOT NULL,

    price NUMERIC(12, 2) NOT NULL,
    freight_value NUMERIC(12, 2) NOT NULL,
    sales_amount NUMERIC(12, 2) NOT NULL,

    CONSTRAINT fk_sales_date
        FOREIGN KEY (date_key)
        REFERENCES retailvision.dim_date (date_key),

    CONSTRAINT fk_sales_customer
        FOREIGN KEY (customer_key)
        REFERENCES retailvision.dim_client (customer_key),

    CONSTRAINT fk_sales_product
        FOREIGN KEY (product_key)
        REFERENCES retailvision.dim_produit (product_key),

    CONSTRAINT fk_sales_seller
        FOREIGN KEY (seller_key)
        REFERENCES retailvision.dim_vendeur (seller_key),

    CONSTRAINT fk_sales_customer_geo
        FOREIGN KEY (customer_geo_key)
        REFERENCES retailvision.dim_geography (geography_key),

    CONSTRAINT fk_sales_seller_geo
        FOREIGN KEY (seller_geo_key)
        REFERENCES retailvision.dim_geography (geography_key),

    CONSTRAINT uq_sales_order_item
        UNIQUE (order_id, order_item_id)
);