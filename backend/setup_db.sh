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
# If you have a the database server running on a different machine (including a docker container with port mapping to localhost), you will
# need to adapt the 'psql' command to connect to the remote server, host, port, and authentication method. Peer authentication will not work in that case.
# In that case, the .env file in this directory may not be the correct one to use. Use the env file that is used by the backend application. For docker,
# that is the .env file in the parent directory (the root of the project/repo).

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
if [ -z "$DATABASE_NAME" ] || [ -z "$DATABASE_USER" ] || [ -z "$DATABASE_PASSWORD" ]; then
    echo "ERROR: Missing required database configuration in '.env' file."
    echo "Please ensure DATABASE_NAME, DATABASE_USER, and DATABASE_PASSWORD are set."
    exit 1
fi

echo "Loaded env vars from '.env' file:"
echo " DATABASE_NAME='$DATABASE_NAME'"
echo " DATABASE_USER='$DATABASE_USER'"
echo " DATABASE_PASSWORD='(hidden)'"
## End of env file handling

# Define SQL commands once
SQL_COMMANDS=$(cat << SQL_EOF
CREATE DATABASE ${DATABASE_NAME};
CREATE USER ${DATABASE_USER} WITH PASSWORD '${DATABASE_PASSWORD}';
GRANT ALL PRIVILEGES ON DATABASE ${DATABASE_NAME} TO ${DATABASE_USER};
\c ${DATABASE_NAME}
GRANT CREATE ON SCHEMA public TO ${DATABASE_USER};
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO ${DATABASE_USER};
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO ${DATABASE_USER};
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO ${DATABASE_USER};
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO ${DATABASE_USER};
SQL_EOF
)

echo "Setting up PostgreSQL database '${DATABASE_NAME}' and user '${DATABASE_USER}'..."

    sudo -u postgres psql -p ${DATABASE_PORT} << EOF
$SQL_COMMANDS
EOF
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to set up database or user. Please check the error messages above."
    exit 1
fi

echo "Database setup complete. Check for errors above."