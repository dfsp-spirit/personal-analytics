#!/bin/bash
#
# Script to set up PostgreSQL database and user based on .env file.
#
# This script will create the database, but the postgresql server must be
# running and accessible.
#
# This assumes you have sudo access to the postgres user.
# Usage: ./setup_db.sh <path-to-env-file>
# Example: ./setup_db.sh .env
# Example: ./setup_db.sh ../.env
#
# This script works for both bare metal and Docker deployments, as long as the .env file is correctly configured.
# In both cases, you should run this script from the bare metal host, not from inside the Docker container.
#
# If you need to run this script inside a container, or on bare metal with a custom database host (other than localhost:5432), you need to set PA_DBSCRIPTS_DATABASE_HOST and PA_DBSCRIPTS_DATABASE_PORT before running this script, or on the script command line.
# on the database container hostname defined in docker-compose.yml. (You will also need to have the 'psql' client installed in the container.)

echo "=== Database setup for personal-analytics ==="

## Env file handling
if [ $# -eq 0 ]; then
    echo "ERROR: Please specify the .env file to use"
    echo ""
    echo "Usage: $0 <path-to-env-file> [--in-container]"
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

# After sourcing the .env file, validate required variables
if [ -z "$DATABASE_NAME" ] || [ -z "$DATABASE_USER" ] || [ -z "$DATABASE_PASSWORD" ]; then
    echo "ERROR: Missing required database configuration in '$ENV_FILE'"
    echo "Please ensure DATABASE_NAME, DATABASE_USER, and DATABASE_PASSWORD are set"
    exit 1
fi

echo "Loaded env vars from '$ENV_FILE':"
echo " DATABASE_NAME='$DATABASE_NAME'"
echo " DATABASE_USER='$DATABASE_USER'"
echo " DATABASE_PASSWORD='(hidden)'"


# Hardcode the database port and host, overriding any values from the .env file, because we always connect to localhost:5432 when running this script on the host machine.
# Allow overriding these values via PA_DBSCRIPTS_DATABASE_HOST and PA_DBSCRIPTS_DATABASE_PORT environment variables, in case you need to connect to a different host/port.
DATABASE_HOST=${PA_DBSCRIPTS_DATABASE_HOST:-localhost}  # The database server host is 'localhost' for both Docker and bare metal, when you run this script on the host machine (due to port mapping in Docker).
DATABASE_PORT=${PA_DBSCRIPTS_DATABASE_PORT:-5432}  # The port is the same for both Docker and bare metal, as we map the container port 5432 to host port 5432 in docker-compose.yml.
echo "Hardcoded settings for database connection:"
echo " DATABASE_HOST='$DATABASE_HOST'"
echo " DATABASE_PORT='$DATABASE_PORT'"
echo "NOTICE: The host and port settings above do NOT come from the .env file, but are hardcoded in this script. You can override them by setting PA_DBSCRIPTS_DATABASE_HOST and PA_DBSCRIPTS_DATABASE_PORT environment variables before running this script. Overriding will be required only if you run this script inside a container, or if you are running bare metal but do NOT have the database server running on the local machine and default port."

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

# Determine authentication method based on host
if [ "$DATABASE_HOST" = "localhost" ] || [ "$DATABASE_HOST" = "127.0.0.1" ] || [ -z "$DATABASE_HOST" ]; then
    echo "Connecting to local database server as user 'postgres' (using sudo/peer authentication)..."

    # For local connections, use sudo without host specification for peer authentication
    sudo -u postgres psql -p ${DATABASE_PORT} << EOF
$SQL_COMMANDS
EOF
else
    echo "Connecting to remote database server at ${DATABASE_HOST}:${DATABASE_PORT} as user 'postgres'..."
    echo "WARNING: For remote connections, you need to handle authentication."
    echo "Options:"
    echo "  1. Set PGPASSWORD environment variable before running this script, or"
    echo "  2. Use .pgpass file in your home directory, or"
    echo "  3. You will be prompted for the postgres user password (the database superuser password)"
    echo ""

    # For remote connections, use the host specification
    psql -h ${DATABASE_HOST} -p ${DATABASE_PORT} -U postgres -W << EOF
$SQL_COMMANDS
EOF
fi

echo "Database setup complete. Check for errors above."