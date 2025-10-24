#!/bin/bash
#
# Drop (delete) the PostgreSQL database used by the personal-analytics web app.
#
# This is a development setup script and is not intended for production use. It assumes that:
#  1) you are developing on your local machine, and not using Docker
#  2) you have sudo access to the postgres user
#  3) the database server is running on the same machine
#  4) peer authentication is enabled in postgres for local connections
#
# Usage: ./drop_database.sh

echo "=== Drop database of the personal-analytics web app, deleting all analytics data ==="
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

echo "Dropping database..."

echo "WARNING: This will permanently delete the postgresql database '$DATABASE_NAME' on localhost and all its data!"
read -p "Are you sure you want to continue? (y/N): " confirm

if [[ $confirm != [yY] && $confirm != [yY][eE][sS] ]]; then
    echo "Operation cancelled."
    exit 0
fi

echo "Dropping database '$DATABASE_NAME'..."
sudo -u postgres psql << EOF
DROP DATABASE IF EXISTS $DATABASE_NAME;
\echo "Database '$DATABASE_NAME' dropped successfully"
EOF

echo "Database drop complete!"