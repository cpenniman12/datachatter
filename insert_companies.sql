-- Generate dummy company data (100 records)
DO $$
DECLARE
    sectors TEXT[] := ARRAY['Technology', 'Healthcare', 'Financial Services', 'Consumer Goods', 'Industrial', 'Energy', 'Utilities', 'Materials', 'Real Estate', 'Communication Services'];
    tech_industries TEXT[] := ARRAY['Software', 'Hardware', 'Semiconductors', 'IT Services', 'Internet'];
    healthcare_industries TEXT[] := ARRAY['Pharmaceuticals', 'Biotechnology', 'Medical Devices', 'Healthcare Services', 'Health Insurance'];
    financial_industries TEXT[] := ARRAY['Banking', 'Insurance', 'Asset Management', 'Financial Technology', 'Investment Banking'];
    consumer_industries TEXT[] := ARRAY['Retail', 'Food & Beverage', 'Apparel', 'Personal Products', 'Consumer Electronics'];
    industrial_industries TEXT[] := ARRAY['Aerospace & Defense', 'Machinery', 'Transportation', 'Construction', 'Manufacturing'];
    ticker_prefix TEXT;
    company_name TEXT;
    sector TEXT;
    industry TEXT;
    founded_date DATE;
    headquarters TEXT[] := ARRAY['New York, NY', 'San Francisco, CA', 'Chicago, IL', 'Boston, MA', 'Seattle, WA', 'Austin, TX', 'Los Angeles, CA', 'Denver, CO', 'Atlanta, GA', 'Dallas, TX'];
    ceo_names TEXT[] := ARRAY['John Smith', 'Sarah Johnson', 'Michael Chen', 'Emily Davis', 'Robert Wilson', 'Jennifer Brown', 'David Rodriguez', 'Lisa Wong', 'James Miller', 'Patricia Thompson'];
    i INTEGER;
    industry_array TEXT[];
BEGIN
    FOR i IN 1..100 LOOP
        -- Generate ticker (e.g., AAPL, MSFT)
        ticker_prefix := chr(floor(random() * 26 + 65)::int) || 
                        chr(floor(random() * 26 + 65)::int) || 
                        chr(floor(random() * 26 + 65)::int) || 
                        chr(floor(random() * 26 + 65)::int);
        
        -- Generate company name
        company_name := 'Company ' || ticker_prefix;
        
        -- Select random sector
        sector := sectors[floor(random() * array_length(sectors, 1) + 1)];
        
        -- Select industry based on sector
        CASE sector
            WHEN 'Technology' THEN industry_array := tech_industries;
            WHEN 'Healthcare' THEN industry_array := healthcare_industries;
            WHEN 'Financial Services' THEN industry_array := financial_industries;
            WHEN 'Consumer Goods' THEN industry_array := consumer_industries;
            WHEN 'Industrial' THEN industry_array := industrial_industries;
            ELSE industry_array := ARRAY['Other'];
        END CASE;
        
        industry := industry_array[floor(random() * array_length(industry_array, 1) + 1)];
        
        -- Generate founded date between 1950 and 2020
        founded_date := (TIMESTAMP '1950-01-01' + (random() * (TIMESTAMP '2020-01-01' - TIMESTAMP '1950-01-01')))::DATE;
        
        -- Insert company
        INSERT INTO companies (ticker, company_name, sector, industry, founded_date, headquarters, employee_count, ceo_name)
        VALUES (
            ticker_prefix, 
            company_name, 
            sector, 
            industry, 
            founded_date,
            headquarters[floor(random() * array_length(headquarters, 1) + 1)],
            floor(random() * 100000 + 100),
            ceo_names[floor(random() * array_length(ceo_names, 1) + 1)]
        );
    END LOOP;
END $$; 