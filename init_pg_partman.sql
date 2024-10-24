CREATE EXTENSION IF NOT EXISTS pg_partman;
CREATE EXTENSION IF NOT EXISTS pg_cron;
SELECT cron.schedule('pg_partman maintenance', '0 0 1 * *', $$SELECT run_maintenance()$$);
