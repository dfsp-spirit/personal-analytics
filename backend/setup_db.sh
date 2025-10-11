#!/bin/bash
sudo -u postgres psql << EOF
CREATE DATABASE personal_analytics;
CREATE USER analytics_user WITH PASSWORD 'personal_analytics_password';
GRANT ALL PRIVILEGES ON DATABASE personal_analytics TO analytics_user;
\c personal_analytics
GRANT CREATE ON SCHEMA public TO analytics_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO analytics_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO analytics_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO analytics_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO analytics_user;
EOF
echo "Database setup complete!"