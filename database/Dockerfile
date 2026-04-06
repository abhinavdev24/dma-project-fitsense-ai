# =============================================================================
# FitSense AI - Custom MySQL Image
# Bakes init scripts into the image so they work on any deployment platform
# (Coolify, Railway, etc.) without relying on bind mounts
# =============================================================================

FROM mysql:9.6.0

# Copy initialization scripts into the entrypoint directory
# MySQL executes these alphabetically on first start when data dir is empty
COPY init-user.sh /docker-entrypoint-initdb.d/01-init-user.sh
COPY fitsense_ai_data_backup.sql /docker-entrypoint-initdb.d/02-data.sql

# Ensure the shell script is executable
RUN chmod +x /docker-entrypoint-initdb.d/01-init-user.sh
