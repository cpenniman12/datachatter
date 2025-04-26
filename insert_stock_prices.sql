-- Insert stock prices (1000 records)
DO $$
DECLARE
    company_count INTEGER;
    company_id INTEGER;
    base_price NUMERIC(10,2);
    opening_price NUMERIC(10,2);
    price_date DATE;
    price_change NUMERIC(10,2);
    i INTEGER;
BEGIN
    SELECT COUNT(*) INTO company_count FROM companies;
    
    FOR i IN 1..1000 LOOP
        -- Select random company
        company_id := floor(random() * company_count + 1);
        
        -- Generate random base price between $10 and $1000
        base_price := (random() * 990 + 10)::NUMERIC(10,2);
        
        -- Generate random date between 2021-01-01 and 2023-12-31
        price_date := (TIMESTAMP '2021-01-01' + (random() * (TIMESTAMP '2023-12-31' - TIMESTAMP '2021-01-01')))::DATE;
        
        -- Daily price variation
        price_change := (random() * 0.1 - 0.05) * base_price; -- -5% to +5%
        opening_price := base_price + price_change;
        
        -- Ensure prices are not negative
        IF opening_price < 1 THEN
            opening_price := 1;
        END IF;
        
        -- Insert stock price
        INSERT INTO stock_prices (
            company_id, price_date, open_price, high_price, 
            low_price, close_price, volume, adj_close
        )
        VALUES (
            company_id,
            price_date,
            opening_price,
            opening_price * (1 + random() * 0.05), -- High price up to 5% above open
            opening_price * (1 - random() * 0.05), -- Low price up to 5% below open
            opening_price * (1 + (random() * 0.08 - 0.04)), -- Close price -4% to +4% from open
            floor(random() * 10000000 + 100000), -- Volume
            opening_price * (1 + (random() * 0.08 - 0.04)) -- Adjusted close same as close for simplicity
        );
    END LOOP;
END $$; 