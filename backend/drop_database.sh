#!/bin/bash

echo "Dropping database: personal_analytics"

# Source environment variables if .env exists
if [ -f .env ]; then
    source .env
    echo "Using database name from .env: $DATABASE_NAME"
    DB_NAME=$DATABASE_NAME
else
    DB_NAME="personal_analytics"
    echo "Using default database name: $DB_NAME"
fi

echo "WARNING: This will permanently delete the postgresql database '$DB_NAME' and all its data!"
read -p "Are you sure you want to continue? (y/N): " confirm

if [[ $confirm != [yY] && $confirm != [yY][eE][sS] ]]; then
    echo "Operation cancelled."
    exit 0
fi

echo "Dropping database..."
sudo -u postgres psql << EOF
DROP DATABASE IF EXISTS $DB_NAME;
\echo "Database '$DB_NAME' dropped successfully"
EOF

echo "Database drop complete!"