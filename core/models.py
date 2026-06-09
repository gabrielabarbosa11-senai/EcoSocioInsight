from django.db import models
from pgvector.django import VectorField

class MetricaSocioEconomica(models.Model):
    data = models.DateField(help_text="Data de referência da métrica")
    tipo_metrica = models.CharField(max_length=100, help_text="Ex: IPCA, Desemprego")
    valor = models.DecimalField(max_digits=10, decimal_places=4, help_text="Valor da métrica")
    regiao = models.CharField(max_length=100, help_text="Região de abrangência (Ex: Brasil, SP, RJ)")
    estado = models.CharField(max_length=2, blank=True, null=True, help_text="Sigla do Estado, se aplicável")

    class Meta:
        db_table = 'metrica_socioeconomica'
        verbose_name = 'Métrica Socioeconômica'
        verbose_name_plural = 'Métricas Socioeconômicas'
        indexes = [
            models.Index(fields=['data', 'tipo_metrica'], name='idx_data_tipo'),
            models.Index(fields=['tipo_metrica'], name='idx_tipo'),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['data', 'tipo_metrica', 'regiao', 'estado'],
                name='unique_metrica_por_data_regiao'
            )
        ]

    def __str__(self):
        return f"{self.tipo_metrica} - {self.data} - {self.valor}"


class DocumentoMetodologico(models.Model):
    titulo = models.CharField(max_length=255, help_text="Título do documento ou nota metodológica")
    conteudo_texto = models.TextField(help_text="Conteúdo textual completo extraído da documentação do IBGE")
    # Embedding: 1536 dimensões compatível com text-embedding-3-small da OpenAI
    embedding = VectorField(dimensions=1536, help_text="Vetor de embeddings (1536 dims) para similaridade de cosseno")
    data_atualizacao = models.DateTimeField(auto_now=True, help_text="Data da última atualização deste documento no banco")

    class Meta:
        db_table = 'documento_metodologico'
        verbose_name = 'Documento Metodológico'
        verbose_name_plural = 'Documentos Metodológicos'

    def __str__(self):
        return self.titulo
