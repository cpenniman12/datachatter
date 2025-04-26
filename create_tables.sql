-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS table_metadata (
    id SERIAL PRIMARY KEY,
    table_name TEXT NOT NULL,
    table_description TEXT,
    embedding VECTOR(1536)
);

CREATE TABLE IF NOT EXISTS column_metadata (
    id SERIAL PRIMARY KEY,
    table_name TEXT NOT NULL,
    column_name TEXT NOT NULL,
    column_description TEXT,
    embedding VECTOR(1536)
);

-- Create companies table
CREATE TABLE companies (
    company_id SERIAL PRIMARY KEY,
    ticker TEXT NOT NULL,
    company_name TEXT NOT NULL,
    sector TEXT NOT NULL,
    industry TEXT NOT NULL,
    founded_date DATE,
    headquarters TEXT,
    employee_count INTEGER,
    ceo_name TEXT
);

-- Create company_financials table
CREATE TABLE company_financials (
    financial_id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES companies(company_id),
    fiscal_year INTEGER NOT NULL,
    fiscal_quarter INTEGER NOT NULL,
    revenue NUMERIC(15,2),
    gross_profit NUMERIC(15,2),
    operating_income NUMERIC(15,2),
    net_income NUMERIC(15,2),
    eps NUMERIC(10,2),
    total_assets NUMERIC(15,2),
    total_liabilities NUMERIC(15,2),
    cash_and_equivalents NUMERIC(15,2),
    report_date DATE
);

-- Create stock_prices table
CREATE TABLE stock_prices (
    price_id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES companies(company_id),
    price_date DATE NOT NULL,
    open_price NUMERIC(10,2),
    high_price NUMERIC(10,2),
    low_price NUMERIC(10,2),
    close_price NUMERIC(10,2),
    volume BIGINT,
    adj_close NUMERIC(10,2)
);

-- Create analyst_estimates table
CREATE TABLE analyst_estimates (
    estimate_id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES companies(company_id),
    analyst_firm TEXT NOT NULL,
    target_price NUMERIC(10,2),
    recommendation TEXT CHECK (recommendation IN ('Buy', 'Sell', 'Hold', 'Overweight', 'Underweight')),
    estimated_eps_next_quarter NUMERIC(10,2),
    estimated_revenue_next_quarter NUMERIC(15,2),
    estimate_date DATE NOT NULL
);

-- Create supply_chain table
CREATE TABLE supply_chain (
    relationship_id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES companies(company_id),
    supplier_id INTEGER REFERENCES companies(company_id),
    component TEXT NOT NULL,
    annual_value NUMERIC(15,2),
    contract_start_date DATE,
    contract_end_date DATE,
    risk_level TEXT CHECK (risk_level IN ('Low', 'Medium', 'High'))
); 