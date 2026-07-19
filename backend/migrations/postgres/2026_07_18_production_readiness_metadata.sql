ALTER TABLE consents ADD COLUMN IF NOT EXISTS terms_version VARCHAR(80) DEFAULT 'minuta-lgpd-v1';

ALTER TABLE simulations ADD COLUMN IF NOT EXISTS rule_version VARCHAR(80) DEFAULT 'demo-v1';
ALTER TABLE simulations ADD COLUMN IF NOT EXISTS created_by_user_id INTEGER;

CREATE INDEX IF NOT EXISTS ix_consents_terms_version ON consents (terms_version);
CREATE INDEX IF NOT EXISTS ix_simulations_rule_version ON simulations (rule_version);
CREATE INDEX IF NOT EXISTS ix_simulations_created_by_user_id ON simulations (created_by_user_id);
