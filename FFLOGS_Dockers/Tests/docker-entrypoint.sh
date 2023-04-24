#!/bin/bash
set -e

# Check if the database exists
if mysql -h"$MYSQL_HOST" -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" -e "use $MYSQL_DATABASE"; then
  echo "Database already exists."
else
  # Create the database and import data
  echo "Creating database and importing data."
  mysql -h"$MYSQL_HOST" -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" -e "create database $MYSQL_DATABASE;"
  mysql -h"$MYSQL_HOST" -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" "$MYSQL_DATABASE" < /init.sql
fi

# Start the MySQL service
exec docker-entrypoint.sh "$@"
