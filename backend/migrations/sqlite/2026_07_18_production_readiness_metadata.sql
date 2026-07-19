ALTER TABLE consents ADD COLUMN terms_version VARCHAR(80) DEFAULT 'minuta-lgpd-v1';

ALTER TABLE simulations ADD COLUMN rule_version VARCHAR(80) DEFAULT 'demo-v1';
ALTER TABLE simulations ADD COLUMN created_by_user_id INTEGER;
