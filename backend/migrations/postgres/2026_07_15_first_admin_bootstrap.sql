CREATE TABLE IF NOT EXISTS admin_bootstrap_tokens (
  id SERIAL PRIMARY KEY,
  user_id INTEGER,
  email VARCHAR(140) NOT NULL,
  token_hash VARCHAR(64) NOT NULL UNIQUE,
  purpose VARCHAR(80) NOT NULL DEFAULT 'first_admin_activation',
  expires_at TIMESTAMPTZ NOT NULL,
  used_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ,
  github_run_id VARCHAR(80),
  created_by_source VARCHAR(120) NOT NULL DEFAULT 'github_actions'
);

CREATE INDEX IF NOT EXISTS ix_admin_bootstrap_tokens_email ON admin_bootstrap_tokens (email);
CREATE INDEX IF NOT EXISTS ix_admin_bootstrap_tokens_token_hash ON admin_bootstrap_tokens (token_hash);
CREATE INDEX IF NOT EXISTS ix_admin_bootstrap_tokens_expires_at ON admin_bootstrap_tokens (expires_at);
