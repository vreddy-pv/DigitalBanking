-- Create databases for each service
CREATE DATABASE auth_db;
CREATE DATABASE account_db;
CREATE DATABASE transaction_db;
CREATE DATABASE ledger_db;
CREATE DATABASE notification_db;

-- Create notification_user for notification service
CREATE USER notification_user WITH ENCRYPTED PASSWORD 'password';

-- Grant privileges on databases
GRANT ALL PRIVILEGES ON DATABASE auth_db TO postgres;
GRANT ALL PRIVILEGES ON DATABASE account_db TO postgres;
GRANT ALL PRIVILEGES ON DATABASE transaction_db TO postgres;
GRANT ALL PRIVILEGES ON DATABASE ledger_db TO postgres;
GRANT ALL PRIVILEGES ON DATABASE notification_db TO notification_user;

-- Grant schema privileges for notification_user
GRANT ALL PRIVILEGES ON SCHEMA public TO notification_user;

-- Grant table creation privileges
ALTER DEFAULT PRIVILEGES FOR USER notification_user IN SCHEMA public GRANT ALL ON TABLES TO notification_user;
ALTER DEFAULT PRIVILEGES FOR USER notification_user IN SCHEMA public GRANT ALL ON SEQUENCES TO notification_user;
