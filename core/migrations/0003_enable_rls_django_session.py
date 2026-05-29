"""
Migration 0003 — Habilita Row Level Security (RLS) na tabela public.django_session.
Isso impede que a tabela seja acessada publicamente via a API PostgREST do Supabase,
enquanto mantém o acesso irrestrito para a aplicação Django que conecta como proprietária/superuser.
"""
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_initial_tables'),
        ('sessions', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            sql="ALTER TABLE public.django_session ENABLE ROW LEVEL SECURITY;",
            reverse_sql="ALTER TABLE public.django_session DISABLE ROW LEVEL SECURITY;",
        ),
    ]
