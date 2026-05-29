-- Este script é executado automaticamente pelo Docker na primeira inicialização.
-- Habilita a extensão pgvector no banco de dados socio_db.
CREATE EXTENSION IF NOT EXISTS vector;
