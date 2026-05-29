from django.contrib import admin
from .models import MetricaSocioEconomica, DocumentoMetodologico

@admin.register(MetricaSocioEconomica)
class MetricaSocioEconomicaAdmin(admin.ModelAdmin):
    list_display = ('tipo_metrica', 'data', 'valor', 'regiao', 'estado')
    list_filter = ('tipo_metrica', 'regiao', 'estado', 'data')
    search_fields = ('tipo_metrica', 'regiao', 'estado')
    ordering = ('-data',)

@admin.register(DocumentoMetodologico)
class DocumentoMetodologicoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'data_atualizacao')
    search_fields = ('titulo', 'conteudo_texto')
    ordering = ('-data_atualizacao',)
