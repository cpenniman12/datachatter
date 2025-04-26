-- Insert metadata for tables
INSERT INTO table_metadata (table_name, table_description) VALUES
    ('companies', 'Basic information about companies including sector, industry, and key details'),
    ('company_financials', 'Quarterly and annual financial data for companies including revenue and profits'),
    ('stock_prices', 'Daily stock price data for companies'),
    ('analyst_estimates', 'Wall Street analyst recommendations and price targets'),
    ('supply_chain', 'Information about supplier relationships between companies');

-- Insert metadata for columns
INSERT INTO column_metadata (table_name, column_name, column_description) VALUES
    -- Companies table
    ('companies', 'company_id', 'Primary key and unique identifier for each company'),
    ('companies', 'ticker', 'Stock market ticker symbol'),
    ('companies', 'company_name', 'Full legal name of the company'),
    ('companies', 'sector', 'Economic sector the company operates in'),
    ('companies', 'industry', 'Specific industry within the sector'),
    ('companies', 'founded_date', 'Date when the company was founded'),
    ('companies', 'headquarters', 'Location of company headquarters'),
    ('companies', 'employee_count', 'Number of employees at the company'),
    ('companies', 'ceo_name', 'Name of the current CEO'),
    
    -- Company financials table
    ('company_financials', 'financial_id', 'Primary key for financial records'),
    ('company_financials', 'company_id', 'Foreign key linking to companies table'),
    ('company_financials', 'fiscal_year', 'Year of the financial reporting period'),
    ('company_financials', 'fiscal_quarter', 'Quarter of the financial reporting period (1-4)'),
    ('company_financials', 'revenue', 'Total sales during the reported period'),
    ('company_financials', 'gross_profit', 'Revenue minus cost of goods sold'),
    ('company_financials', 'operating_income', 'Profit from operations before interest and taxes'),
    ('company_financials', 'net_income', 'Profit after all expenses and taxes'),
    ('company_financials', 'eps', 'Earnings per share'),
    ('company_financials', 'total_assets', 'Total value of assets owned by the company'),
    ('company_financials', 'total_liabilities', 'Total debts and obligations owed by the company'),
    ('company_financials', 'cash_and_equivalents', 'Cash and liquid assets available to the company'),
    ('company_financials', 'report_date', 'Date when the financial report was published'),
    
    -- Stock prices table
    ('stock_prices', 'price_id', 'Primary key for stock price records'),
    ('stock_prices', 'company_id', 'Foreign key linking to companies table'),
    ('stock_prices', 'price_date', 'Date of the stock price information'),
    ('stock_prices', 'open_price', 'Stock price at market open'),
    ('stock_prices', 'high_price', 'Highest stock price during the trading day'),
    ('stock_prices', 'low_price', 'Lowest stock price during the trading day'),
    ('stock_prices', 'close_price', 'Stock closing price for the day'),
    ('stock_prices', 'volume', 'Number of shares traded'),
    ('stock_prices', 'adj_close', 'Adjusted closing price accounting for corporate actions'),
    
    -- Analyst estimates table
    ('analyst_estimates', 'estimate_id', 'Primary key for analyst estimate records'),
    ('analyst_estimates', 'company_id', 'Foreign key linking to companies table'),
    ('analyst_estimates', 'analyst_firm', 'Name of the firm providing the analysis'),
    ('analyst_estimates', 'target_price', 'Analyst''s 12-month price target'),
    ('analyst_estimates', 'recommendation', 'Analyst''s recommendation (Buy, Sell, Hold, etc.)'),
    ('analyst_estimates', 'estimated_eps_next_quarter', 'Projected earnings per share for next quarter'),
    ('analyst_estimates', 'estimated_revenue_next_quarter', 'Projected revenue for next quarter'),
    ('analyst_estimates', 'estimate_date', 'Date when the estimate was published'),
    
    -- Supply chain table
    ('supply_chain', 'relationship_id', 'Primary key for supply chain relationship records'),
    ('supply_chain', 'company_id', 'Foreign key linking to companies table (the buyer)'),
    ('supply_chain', 'supplier_id', 'Foreign key linking to companies table (the supplier)'),
    ('supply_chain', 'component', 'Component or service provided by the supplier'),
    ('supply_chain', 'annual_value', 'Annual contract value in dollars'),
    ('supply_chain', 'contract_start_date', 'Start date of the supplier contract'),
    ('supply_chain', 'contract_end_date', 'End date of the supplier contract'),
    ('supply_chain', 'risk_level', 'Risk assessment level of the supply relationship'); 