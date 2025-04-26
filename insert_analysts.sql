-- Insert analyst estimates (1000 records)
DO $$
DECLARE
    company_count INTEGER;
    company_id INTEGER;
    analyst_firms TEXT[] := ARRAY['Morgan Stanley', 'Goldman Sachs', 'JP Morgan', 'Bank of America', 'Citigroup', 'Wells Fargo', 'UBS', 'Credit Suisse', 'Deutsche Bank', 'Barclays'];
    recommendations TEXT[] := ARRAY['Buy', 'Sell', 'Hold', 'Overweight', 'Underweight'];
    base_price NUMERIC(10,2);
    current_price NUMERIC(10,2);
    i INTEGER;
BEGIN
    SELECT COUNT(*) INTO company_count FROM companies;
    
    FOR i IN 1..1000 LOOP
        -- Select random company
        company_id := floor(random() * company_count + 1);
        
        -- Default price if no price found
        current_price := (random() * 990 + 10)::NUMERIC(10,2);
        
        -- Insert analyst estimate
        INSERT INTO analyst_estimates (
            company_id, analyst_firm, target_price, recommendation,
            estimated_eps_next_quarter, estimated_revenue_next_quarter, estimate_date
        )
        VALUES (
            company_id,
            analyst_firms[floor(random() * array_length(analyst_firms, 1) + 1)],
            current_price * (1 + (random() * 0.4 - 0.2)), -- Target price +/- 20% from current
            recommendations[floor(random() * array_length(recommendations, 1) + 1)],
            (random() * 5)::NUMERIC(10,2), -- Estimated EPS
            (random() * 5000000000 + 10000000)::NUMERIC(15,2), -- Estimated revenue
            (TIMESTAMP '2023-01-01' + (random() * (TIMESTAMP '2023-12-31' - TIMESTAMP '2023-01-01')))::DATE -- Estimate date
        );
    END LOOP;
END $$; 