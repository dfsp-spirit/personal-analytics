#!/bin/bash
#
# Drop (delete) the PostgreSQL database used by the personal-analytics web app.
#
# This script works for both bare metal and Docker deployments, as long as the .env file is correctly configured.

echo "=== Drop database of the personal-analytics web app, deleting all analytics data ==="

## Env file handling
if [ $# -eq 0 ]; then
    echo "ERROR: Please specify the .env file to use"
    echo ""
    echo "Usage: $0 <path-to-env-file>"
    echo ""
    echo "Examples:"
    echo "  $0 .env                    # Bare metal (in <repo_root>/backend/.env)"
    echo "  $0 ../.env                 # Docker (in <repo_root>/.env), if you run the script from <repo_root>/backend"
    echo "  $0 /path/to/custom.env     # Custom location. Useful if you have multiple setups, e.g., testing vs production."
    echo ""
    echo "For Docker deployments, use the same .env file as docker-compose.yml, i.e., in repo root."
    echo "    * docker-compose.yml will pick it up from there (same directory) automatically, and is configured to pass relevant env vars in it on to the containers (as env vars)."
    echo "    * The backend running in the container will pick up the env vars and use them to connect to the database. It will ignore any .env file in its working directory, as env vars take precedence over the '.env' file."
    echo "For bare metal, use backend/.env"
    echo "    * The backend will read the env file in its working directory and use it to connect to the database."
    echo "    * Note that if you have set environment variables in your shell when you start the backend, they will override the .env file."
    exit 1
fi

ENV_FILE="$1"

if [ ! -f "$ENV_FILE" ]; then
    echo "ERROR: .env file not found: '$ENV_FILE'. Please provide a valid path."
    exit 1
fi

echo "Using environment from: '$ENV_FILE'"
source "$ENV_FILE"   # Loads environment variables DATABASE_NAME, DATABASE_USER, DATABASE_PASSWORD
## End of env file handling

echo "Dropping database..."


echo "WARNING: This will permanently delete the postgresql database '$DATABASE_NAME' and all its data!"
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