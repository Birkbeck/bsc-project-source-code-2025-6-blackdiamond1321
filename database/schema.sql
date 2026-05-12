# FinTrack database schema


CREATE DATABASE IF NOT EXISTS fintrack
CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE fintrack;

# users: registered FinTrack accounts

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    security_question VARCHAR(255) NOT NULL,
    security_answer VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

# transactions: income or expenses

CREATE TABLE IF NOT EXISTS transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    type VARCHAR(10) NOT NULL,
    description VARCHAR(255) NOT NULL,
    amount FLOAT NOT NULL,
    category VARCHAR(50) NOT NULL,
    method VARCHAR(50) NOT NULL,
    date VARCHAR(10) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
) ENGINE=InnoDB;

# budgets: monthly spending limit per category

CREATE TABLE IF NOT EXISTS budgets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    category VARCHAR(50) NOT NULL,
    monthly_limit FLOAT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE KEY unique_user_category (user_id, category)
) ENGINE=InnoDB;


# loans: money the user has lent to a third party

CREATE TABLE IF NOT EXISTS loans (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    borrower VARCHAR(255) NOT NULL,
    principal FLOAT NOT NULL,
    interest_rate FLOAT DEFAULT 0,
    currency VARCHAR(3) DEFAULT 'GBP',
    borrowed_at VARCHAR(10) NOT NULL,
    paid_at VARCHAR(10) DEFAULT '',
    is_paid BOOLEAN DEFAULT FALSE,
    amount_paid FLOAT DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(id)
) ENGINE=InnoDB;


# payments: repayments against a loan

CREATE TABLE IF NOT EXISTS payments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    loan_id INT NOT NULL,
    amount FLOAT NOT NULL,
    currency VARCHAR(3) NOT NULL,
    loan_currency VARCHAR(3) NOT NULL,
    exchange_rate FLOAT DEFAULT 1.0,
    paid_at VARCHAR(10) NOT NULL,
    FOREIGN KEY (loan_id) REFERENCES loans(id)
) ENGINE=InnoDB;


# payment sources: user-owned payment methods

CREATE TABLE IF NOT EXISTS payment_sources (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    name VARCHAR(32) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
) ENGINE=InnoDB;
