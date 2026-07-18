DROP INDEX IF EXISTS ix_simulations_created_by_user_id;
DROP INDEX IF EXISTS ix_simulations_rule_version;
DROP INDEX IF EXISTS ix_consents_terms_version;

ALTER TABLE simulations DROP COLUMN IF EXISTS created_by_user_id;
ALTER TABLE simulations DROP COLUMN IF EXISTS rule_version;

ALTER TABLE consents DROP COLUMN IF EXISTS terms_version;
