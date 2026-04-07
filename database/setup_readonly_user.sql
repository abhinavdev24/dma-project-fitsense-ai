-- FitSense AI Dashboard - Read-Only User Setup
-- =============================================================================
-- This script creates a read-only MySQL user with SELECT-only privileges.
-- Use this for production deployments to ensure maximum data protection.
-- =============================================================================

-- Create read-only user (adjust password as needed)
CREATE USER IF NOT EXISTS 'fitsense_readonly'@'localhost' IDENTIFIED BY 'your_secure_password_here';

-- Grant all read-only privileges on the FitSense database
GRANT SELECT, SHOW VIEW, LOCK TABLES ON fitsense_ai.* TO 'fitsense_readonly'@'localhost';

-- Grant SELECT on information_schema for table metadata (used by some queries)
GRANT SELECT ON information_schema.* TO 'fitsense_readonly'@'localhost';

-- Grant SHOW DATABASES for database listing (read-only)
GRANT SHOW DATABASES ON *.* TO 'fitsense_readonly'@'localhost';

-- Apply changes immediately
FLUSH PRIVILEGES;

-- Verify the user was created with correct permissions
SHOW GRANTS FOR 'fitsense_readonly'@'localhost';

-- =============================================================================
-- TO USE THIS USER:
-- 1. Run this SQL script as your MySQL admin user
-- 2. Update your .env file to use the new credentials:
--    DB_USER=fitsense_readonly
--    DB_PASSWORD=your_secure_password_here
--
-- The application will now be protected at the database level from any write
-- operations, in addition to the application-level query validation.
-- =============================================================================
