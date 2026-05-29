"""
Migration 0001 — Habilita a extensão pgvector no PostgreSQL.
DEVE ser a primeira migration rodada no projeto.
O VectorField do modelo DocumentoMetodologico depende desta extensão.
"""
from django.db import migrations


class Migration(migrations.Migration):

    initial = True
    dependencies = []

    operations = [
        migrations.RunSQL(
            sql="CREATE EXTENSION IF NOT EXISTS vector;",
            reverse_sql="DROP EXTENSION IF EXISTS vector;",
        ),
    ]
