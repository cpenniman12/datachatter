-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create table_metadata table if it doesn't exist
CREATE TABLE IF NOT EXISTS table_metadata (
    id SERIAL PRIMARY KEY,
    table_name TEXT NOT NULL,
    table_description TEXT,
    embedding VECTOR(1536)
);

-- Create column_metadata table if it doesn't exist
CREATE TABLE IF NOT EXISTS column_metadata (
    id SERIAL PRIMARY KEY,
    table_name TEXT NOT NULL,
    column_name TEXT NOT NULL,
    column_description TEXT,
    embedding VECTOR(1536)
);

-- Sample data for testing
INSERT INTO table_metadata (table_name, table_description) VALUES
   ('customers', 'Contains all customer information'),
   ('products', 'Information about products sold by TechCorp'),
   ('purchases', 'Record of all customer purchases'),
   ('customer_support', 'Customer support tickets and interactions');

INSERT INTO column_metadata (table_name, column_name, column_description) VALUES
   ('customers', 'customer_id', 'Unique identifier for each customer'),
   ('customers', 'name', 'Customer''s full name'),
   ('customers', 'email', 'Customer''s email address'),
   ('products', 'product_id', 'Unique identifier for each product'),
   ('products', 'product_name', 'Name of the product'),
   ('products', 'price', 'Current price of the product'); 