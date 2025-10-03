#!/bin/bash
set -e

# Create multiple databases for different services
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    CREATE DATABASE litellm;
    CREATE USER litellm WITH PASSWORD 'litellm';
    GRANT ALL PRIVILEGES ON DATABASE litellm TO litellm;
    
    CREATE DATABASE langfuse;
    CREATE USER langfuse WITH PASSWORD 'langfuse';
    GRANT ALL PRIVILEGES ON DATABASE langfuse TO langfuse;
EOSQL
