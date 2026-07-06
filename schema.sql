-- =========================================
-- CREATE DATABASE
-- =========================================

CREATE DATABASE IF NOT EXISTS stockdbms;
USE stockdbms;

-- =========================================
-- USERS TABLE
-- =========================================

CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    balance DECIMAL(12,2) DEFAULT 100000.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =========================================
-- USER PHONE TABLE
-- =========================================

CREATE TABLE IF NOT EXISTS user_phone (
    phone_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    phone_num VARCHAR(15),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- =========================================
-- STOCKS TABLE
-- =========================================

CREATE TABLE IF NOT EXISTS stocks (
    stock_id INT AUTO_INCREMENT PRIMARY KEY,
    stock_name VARCHAR(20) NOT NULL,        -- ticker symbol e.g. AAPL
    company_name VARCHAR(100),              -- full company name
    sector VARCHAR(100),
    current_price DECIMAL(10,2) DEFAULT 0.00,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- =========================================
-- PRICE HISTORY TABLE
-- =========================================

CREATE TABLE IF NOT EXISTS price_history (
    price_id INT AUTO_INCREMENT PRIMARY KEY,
    stock_id INT,
    price DECIMAL(10,2),
    recorded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (stock_id) REFERENCES stocks(stock_id) ON DELETE CASCADE
);

-- =========================================
-- PORTFOLIO TABLE
-- =========================================

CREATE TABLE IF NOT EXISTS portfolio (
    portfolio_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNIQUE,
    total_invested DECIMAL(12,2) DEFAULT 0.00,
    avg_buy_price DECIMAL(12,2) DEFAULT 0.00,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- =========================================
-- PORTFOLIO STOCK TABLE
-- =========================================

CREATE TABLE IF NOT EXISTS portfolio_stock (
    portfolio_id INT,
    stock_id INT,
    shares_owned INT DEFAULT 0,
    avg_buy_price DECIMAL(10,2) DEFAULT 0.00,
    total_invested DECIMAL(12,2) DEFAULT 0.00,
    PRIMARY KEY (portfolio_id, stock_id),
    FOREIGN KEY (portfolio_id) REFERENCES portfolio(portfolio_id) ON DELETE CASCADE,
    FOREIGN KEY (stock_id) REFERENCES stocks(stock_id) ON DELETE CASCADE
);

-- =========================================
-- TRANSACTIONS TABLE
-- =========================================

CREATE TABLE IF NOT EXISTS transactions (
    transaction_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    stock_id INT,
    quantity INT NOT NULL,
    price_per_share DECIMAL(10,2) NOT NULL,
    total_amount DECIMAL(12,2) NOT NULL,
    transaction_type ENUM('BUY','SELL') NOT NULL,
    transaction_date DATE DEFAULT (CURRENT_DATE),
    transaction_time TIME DEFAULT (CURRENT_TIME),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (stock_id) REFERENCES stocks(stock_id) ON DELETE CASCADE
);

-- =========================================
-- INDEXES (FOR PERFORMANCE)
-- =========================================

CREATE INDEX idx_user_email ON users(email);
CREATE INDEX idx_stock_name ON stocks(stock_name);
CREATE INDEX idx_transaction_user ON transactions(user_id);
CREATE INDEX idx_transaction_stock ON transactions(stock_id);
CREATE INDEX idx_price_history_stock ON price_history(stock_id);
