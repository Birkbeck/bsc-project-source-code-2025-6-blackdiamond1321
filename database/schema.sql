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