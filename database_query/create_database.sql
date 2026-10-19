/*
===============================================================================
Init Script: Create Databases (Bronze / Silver / Gold)  -- MySQL version
===============================================================================
Purpose:
    MySQL does not have a "schema" that is separate from a "database" the way
    SQL Server does (in SQL Server, one database holds many schemas; in MySQL,
    CREATE SCHEMA is just a synonym for CREATE DATABASE). To keep the exact
    same qualified naming used throughout this project (bronze.table,
    silver.table, gold.table) we create three databases instead of three
    schemas inside one database.

    This script:
    - Drops the bronze / silver / gold databases if they already exist.
    - Re-creates them with a utf8mb4 character set (recommended default for
      MySQL 8+, avoids encoding issues with names/text from source systems).

WARNING:
    Running this script will drop the 'bronze', 'silver' and 'gold' databases
    if they exist. All data in them will be permanently deleted. Make sure you
    have backups before running this in anything other than a fresh dev setup.

Notes for later ML use:
    - utf8mb4 avoids silent truncation/mojibake issues that can corrupt
      categorical features (names, categories, country codes) fed into models.
    - Keeping the three-database split mirrors the medallion architecture and
      makes it easy to grant read-only access to the 'gold' database to
      notebooks / BI / ML tooling without exposing raw bronze data.
===============================================================================
*/

DROP DATABASE IF EXISTS bronze;
DROP DATABASE IF EXISTS silver;
DROP DATABASE IF EXISTS gold;

CREATE DATABASE bronze CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
CREATE DATABASE silver CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
CREATE DATABASE gold   CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;

-- If your MySQL version is older than 8.0, replace utf8mb4_0900_ai_ci
-- with utf8mb4_general_ci or utf8mb4_unicode_ci above.