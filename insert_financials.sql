-- Insert financials (1000 records - 10 quarters for 100 companies)
DO $$
DECLARE
    company_count INTEGER;
    company_id INTEGER;
    fiscal_year INTEGER;
    fiscal_quarter INTEGER;
    revenue NUMERIC;
    i INTEGER;
BEGIN
    SELECT COUNT(*) INTO company_count FROM companies;
    
    FOR i IN 1..1000 LOOP
        -- Select random company
        company_id := floor(random() * company_count + 1);
        
        -- Generate financials for a random quarter from 2018 to 2023
        fiscal_year := floor(random() * 5 + 2018);
        fiscal_quarter := floor(random() * 4 + 1);
        
        -- Generate random revenue between $10M and $10B
        revenue := (random() * 9990000000 + 10000000)::NUMERIC(15,2);
        
        -- Insert with derived financials
        INSERT INTO company_financials (
            company_id, fiscal_year, fiscal_quarter, revenue, 
            gross_profit, operating_income, net_income, eps, 
            total_assets, total_liabilities, cash_and_equivalents, report_date
        )
        VALUES (
            company_id, 
            fiscal_year, 
            fiscal_quarter, 
            revenue,
            revenue * (random() * 0.4 + 0.3), -- Gross profit 30-70% of revenue
            revenue * (random() * 0.3 + 0.1), -- Operating income 10-40% of revenue
            revenue * (random() * 0.2 + 0.05), -- Net income 5-25% of revenue
            (revenue * (random() * 0.2 + 0.05) / (random() * 500000000 + 100000000))::NUMERIC(10,2), -- EPS
            revenue * (random() * 5 + 2), -- Total assets
            revenue * (random() * 3 + 1), -- Total liabilities
            revenue * (random() * 0.3 + 0.05), -- Cash
            (TIMESTAMP '2018-01-01' + (interval '1 day' * floor(random() * 1825)))::DATE -- Report date
        );
    END LOOP;
END $$; 