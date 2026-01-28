# File: `scripts/wait_for_db.sh`
#!/usr/bin/env sh
# Usage: wait_for_db.sh <host> <user> <dbname> [port]
HOST="$1"
USER="$2"
DB="$3"
PORT="${4:-5432}"
MAX=60
i=0

while [ $i -lt $MAX ]; do
  if pg_isready -h "$HOST" -p "$PORT" -U "$USER" -d "$DB" >/dev/null 2>&1; then
    echo "Database is available"
    exit 0
  fi
  i=$((i + 1))
  echo "Waiting for database ($i/$MAX)..."
  sleep 1
done

echo "Timed out waiting for database"
exit 1



# Update `docker-compose.yml` backend service command (example)
# command: sh -c "/app/scripts/wait_for_db.sh db ${POSTGRES_USER} ${POSTGRES_DB} ${DB_PORT:-5432} && alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"