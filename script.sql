DROP DATABASE IF EXISTS transaction_handler;
CREATE DATABASE transaction_handler;
USE transaction_handler;

-- 1. Master Category List
CREATE TABLE categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE
);

-- 2. Transaction Ledger (With Status Column)
CREATE TABLE transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    merchant VARCHAR(255),
    amount DECIMAL(10, 2),
    txn_date DATE,
    category VARCHAR(255),
    explanation TEXT,
    status VARCHAR(50) DEFAULT 'Auto-AI', -- This was missing
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO categories (name) VALUES ('Uncategorized');


select * from categories;