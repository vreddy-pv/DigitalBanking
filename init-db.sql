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

CREATE DATABASE customer_db;
CREATE USER customer_user WITH ENCRYPTED PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE customer_db TO customer_user;
\c customer_db
GRANT ALL PRIVILEGES ON SCHEMA public TO customer_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO customer_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO customer_user;

-- Read-only analytics user for analytics-service (CQRS read side)
CREATE USER analytics_user WITH ENCRYPTED PASSWORD 'password';
GRANT CONNECT ON DATABASE transaction_db TO analytics_user;
GRANT CONNECT ON DATABASE ledger_db TO analytics_user;
\c transaction_db
GRANT USAGE ON SCHEMA public TO analytics_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO analytics_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO analytics_user;
\c ledger_db
GRANT USAGE ON SCHEMA public TO analytics_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO analytics_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO analytics_user;
