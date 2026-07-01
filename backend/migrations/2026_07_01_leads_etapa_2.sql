ALTER TABLE leads ADD COLUMN prioridade VARCHAR(20) NOT NULL DEFAULT 'Media';

UPDATE leads
SET prioridade = 'Media'
WHERE prioridade IS NULL OR prioridade = '';
