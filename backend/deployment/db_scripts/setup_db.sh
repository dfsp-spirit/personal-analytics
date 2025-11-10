#!/bin/bash
#
# Script to set up PostgreSQL database and user based on .env file.
#
# This script will create the database and database user, but the postgresql server must be
# running and accessible.
# Note that it does NOT create any tables or relations in the database. The backend application
# will create the required tables automatically when it is started for the first time.
#
# This is a development setup script and is not intended for production use. It assumes that:
#  1) you are developing on your local machine, and not using Docker
#  2) you have sudo access to the postgres user
#  3) the database server is running on the same machine
#  4) peer authentication is enabled in postgres for local connections
#
# Usage: ./setup_db.sh

echo "=== Database setup for personal-analytics ==="
echo "NOTE: This script is for development use only. It is not intended for production use."


if [ ! -f ".env" ]; then
    echo "ERROR: .env file not found. You need to create it first from the '.env.example' template file."
    exit 1
fi

source ".env"   # Loads environment variables DATABASE_NAME, DATABASE_USER, DATABASE_PASSWORD

# After sourcing the .env file, validate required variables
if [ -z "$PA_DATABASE_NAME" ] || [ -z "$PA_DATABASE_USER" ] || [ -z "$PA_DATABASE_PASSWORD" ]; then
    echo "ERROR: Missing required database configuration in '.env' file."
    echo "Please ensure PA_DATABASE_NAME, PA_DATABASE_USER, and PA_DATABASE_PASSWORD are set."
    exit 1
fi

echo "Loaded env vars from '.env' file:"
echo " PA_DATABASE_NAME='$PA_DATABASE_NAME'"
echo " PA_DATABASE_USER='$PA_DATABASE_USER'"
echo " PA_DATABASE_PASSWORD='(hidden)'"
## End of env file handling

# Define SQL commands once
SQL_COMMANDS=$(cat << SQL_EOF
CREATE DATABASE ${PA_DATABASE_NAME};
-- Revoke all default privileges from PUBLIC in this database
REVOKE ALL ON DATABASE ${PA_DATABASE_NAME} FROM PUBLIC;

CREATE USER ${PA_DATABASE_USER} WITH
    PASSWORD '${PA_DATABASE_PASSWORD}'
    NOCREATEDB
    NOCREATEROLE
    NOSUPERUSER
    NOREPLICATION;

GRANT CONNECT ON DATABASE ${PA_DATABASE_NAME} TO ${PA_DATABASE_USER};
\c ${PA_DATABASE_NAME}

-- Lock down the public schema completely
REVOKE ALL ON SCHEMA public FROM PUBLIC;
GRANT USAGE, CREATE ON SCHEMA public TO ${PA_DATABASE_USER};

-- Your app privileges (these are perfect)
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO ${PA_DATABASE_USER};
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO ${PA_DATABASE_USER};
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO ${PA_DATABASE_USER};
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO ${PA_DATABASE_USER};
SQL_EOF
)

echo "Setting up PostgreSQL database '${PA_DATABASE_NAME}' and user '${PA_DATABASE_USER}'..."

    sudo -u postgres psql -p ${PA_DATABASE_PORT} << EOF
$SQL_COMMANDS
EOF
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to set up database or user. Please check the error messages above."
    exit 1
fi

echo "Database setup complete. Check for errors above."