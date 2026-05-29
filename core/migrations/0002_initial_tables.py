"""
Migration 0002 — Cria as tabelas relacionais e vetorial do SocioEcoData.
Depende de 0001 (pgvector já habilitado).
"""
import pgvector.django
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_enable_pgvector'),
    ]

    operations = [
        # Tabela relacional: armazena séries históricas do IBGE
        migrations.CreateModel(
            name='MetricaSocioEconomica',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('data', models.DateField(help_text='Data de referência da métrica')),
                ('tipo_metrica', models.CharField(help_text='Ex: IPCA, Desemprego', max_length=100)),
                ('valor', models.DecimalField(decimal_places=4, help_text='Valor da métrica', max_digits=10)),
                ('regiao', models.CharField(help_text='Região de abrangência', max_length=100)),
                ('estado', models.CharField(blank=True, help_text='Sigla do Estado, se aplicável', max_length=2, null=True)),
            ],
            options={
                'verbose_name': 'Métrica Socioeconômica',
                'verbose_name_plural': 'Métricas Socioeconômicas',
                'db_table': 'metrica_socioeconomica',
            },
        ),
        # Tabela vetorial: armazena documentos com embeddings de 1536 dims
        migrations.CreateModel(
            name='DocumentoMetodologico',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('titulo', models.CharField(help_text='Título do documento', max_length=255)),
                ('conteudo_texto', models.TextField(help_text='Conteúdo textual do IBGE')),
                ('embedding', pgvector.django.VectorField(dimensions=1536, help_text='Vetor de embeddings (1536 dims)')),
                ('data_atualizacao', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Documento Metodológico',
                'verbose_name_plural': 'Documentos Metodológicos',
                'db_table': 'documento_metodologico',
            },
        ),
        # Índices compostos para otimizar queries temporais
        migrations.AddIndex(
            model_name='metricasocioeconomica',
            index=models.Index(fields=['data', 'tipo_metrica'], name='idx_data_tipo'),
        ),
        migrations.AddIndex(
            model_name='metricasocioeconomica',
            index=models.Index(fields=['tipo_metrica'], name='idx_tipo'),
        ),
    ]
