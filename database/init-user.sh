#!/bin/bash
# 01-init-user.sh
# Creates fitsense user with network access (%) for cross-container communication
# Uses environment variables from docker-compose

mysql -u root -p"${MYSQL_ROOT_PASSWORD}" <<EOF
CREATE USER IF NOT EXISTS '${DB_USER:-fitsense}'@'%' IDENTIFIED BY '${DB_PASSWORD:-fitsense_password}';
GRANT ALL PRIVILEGES ON ${DB_NAME:-fitsense_ai}.* TO '${DB_USER:-fitsense}'@'%';
FLUSH PRIVILEGES;
EOF
