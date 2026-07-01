CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY,
  nome VARCHAR(140) NOT NULL,
  email VARCHAR(140) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  role VARCHAR(40) NOT NULL DEFAULT 'operador',
  ativo BOOLEAN NOT NULL DEFAULT 1,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS ix_users_email ON users(email);
CREATE INDEX IF NOT EXISTS ix_users_role ON users(role);

UPDATE users SET role = lower(role) WHERE role IS NOT NULL;
UPDATE users SET role = 'operador' WHERE role NOT IN ('admin', 'supervisor', 'operador', 'parceiro') OR role IS NULL;
