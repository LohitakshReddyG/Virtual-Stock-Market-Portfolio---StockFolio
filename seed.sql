USE stockdbms;

-- Seed stocks (ticker, company name, sector, placeholder price)
INSERT INTO stocks (stock_name, company_name, sector, current_price) VALUES
('AAPL',        'Apple Inc.',                       'Technology',         0.00),
('TSLA',        'Tesla Inc.',                        'Automotive/Energy',  0.00),
('GOOGL',       'Alphabet Inc.',                     'Technology',         0.00),
('MSFT',        'Microsoft Corporation',             'Technology',         0.00),
('AMZN',        'Amazon.com Inc.',                   'E-Commerce',         0.00),
('NFLX',        'Netflix Inc.',                      'Entertainment',      0.00),
('META',        'Meta Platforms Inc.',               'Social Media',       0.00),
('NVDA',        'NVIDIA Corporation',                'Semiconductors',     0.00),
('RELIANCE.NS', 'Reliance Industries Ltd.',          'Conglomerate',       0.00),
('TCS.NS',      'Tata Consultancy Services Ltd.',    'IT Services',        0.00);
