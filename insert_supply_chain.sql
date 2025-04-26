-- Insert supply chain relationships (1000 records)
DO $$
DECLARE
    company_count INTEGER;
    company_id INTEGER;
    supplier_id INTEGER;
    components TEXT[] := ARRAY['Processors', 'Memory', 'Batteries', 'Displays', 'Raw Materials', 'Software', 'Services', 'Logistics', 'Manufacturing', 'Components'];
    risk_levels TEXT[] := ARRAY['Low', 'Medium', 'High'];
    i INTEGER;
BEGIN
    SELECT COUNT(*) INTO company_count FROM companies;
    
    FOR i IN 1..1000 LOOP
        -- Select random company and supplier
        company_id := floor(random() * company_count + 1);
        supplier_id := floor(random() * company_count + 1);
        
        -- Ensure company and supplier are different
        WHILE supplier_id = company_id LOOP
            supplier_id := floor(random() * company_count + 1);
        END LOOP;
        
        -- Insert supply chain relationship
        INSERT INTO supply_chain (
            company_id, supplier_id, component, annual_value,
            contract_start_date, contract_end_date, risk_level
        )
        VALUES (
            company_id,
            supplier_id,
            components[floor(random() * array_length(components, 1) + 1)],
            (random() * 100000000 + 1000000)::NUMERIC(15,2), -- Annual value
            (TIMESTAMP '2020-01-01' + (random() * (TIMESTAMP '2023-01-01' - TIMESTAMP '2020-01-01')))::DATE, -- Start date
            (TIMESTAMP '2023-01-01' + (random() * (TIMESTAMP '2026-01-01' - TIMESTAMP '2023-01-01')))::DATE, -- End date
            risk_levels[floor(random() * array_length(risk_levels, 1) + 1)]
        );
    END LOOP;
END $$; 