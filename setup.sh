#!/bin/bash

# Set database credentials
DB_NAME="proiect"
DB_USER="radu"
DB_PASSWORD="radu"
DB_SCHEMA="django"
APP_NAME="app1"

echo "Starting database setup..."

# Create the PostgreSQL user and database
sudo -u postgres psql <<EOF
CREATE DATABASE $DB_NAME;
CREATE USER $DB_USER WITH ENCRYPTED PASSWORD '$DB_PASSWORD';
GRANT ALL ON DATABASE $DB_NAME TO $DB_USER;
EOF

echo "Database and user created."

# Create the Django schema and set privileges
sudo -u postgres psql -d $DB_NAME <<EOF
CREATE SCHEMA IF NOT EXISTS $DB_SCHEMA;
GRANT ALL ON SCHEMA $DB_SCHEMA TO $DB_USER;
ALTER ROLE $DB_USER SET search_path = $DB_SCHEMA, public;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA $DB_SCHEMA TO $DB_USER;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA $DB_SCHEMA TO $DB_USER;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA $DB_SCHEMA TO $DB_USER;
EOF

echo "Schema and privileges set."

# Run Django migrations
echo "Running Django migrations..."
python3 manage.py makemigrations $APP_NAME
python3 manage.py migrate

# Load data
python3 manage.py loaddata data.json

echo "Database setup complete!"
