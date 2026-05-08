-- Create databases for each service
CREATE DATABASE auth_db;
CREATE DATABASE account_db;
CREATE DATABASE transaction_db;
CREATE DATABASE ledger_db;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE auth_db TO postgres;
GRANT ALL PRIVILEGES ON DATABASE account_db TO postgres;
GRANT ALL PRIVILEGES ON DATABASE transaction_db TO postgres;
GRANT ALL PRIVILEGES ON DATABASE ledger_db TO postgres;
