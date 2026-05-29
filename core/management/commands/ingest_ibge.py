import logging
import requests
import pandas as pd
from datetime import datetime
from django.core.management.base import BaseCommand
from core.models import MetricaSocioEconomica

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Ingere dados socioeconômicos (IPCA e Desemprego) da API do IBGE (SIDRA)'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Iniciando ingestão de dados do IBGE...'))
        
        # URLs da API SIDRA do IBGE
        # IPCA (Índice Nacional de Preços ao Consumidor Amplo) - Variação mensal (Tabela 1737)
        ipca_url = "https://servicodados.ibge.gov.br/api/v3/agregados/1737/periodos/all/variaveis/63?localidades=N1[all]"
        
        # Desemprego (Taxa de desocupação PNAD Contínua - Tabela 6381)
        desemprego_url = "https://servicodados.ibge.gov.br/api/v3/agregados/6381/periodos/all/variaveis/4099?localidades=N1[all]"

        dados_novos = []

        # Processar IPCA
        self.stdout.write('Buscando dados de IPCA...')
        dados_novos.extend(self._fetch_and_transform(ipca_url, 'IPCA'))

        # Processar Desemprego
        self.stdout.write('Buscando dados de Desemprego...')
        dados_novos.extend(self._fetch_and_transform(desemprego_url, 'Desemprego'))

        if dados_novos:
            # Salvar no banco em lote com ignore_conflicts=True para evitar duplicidade
            MetricaSocioEconomica.objects.bulk_create(
                dados_novos,
                ignore_conflicts=True
            )
            self.stdout.write(self.style.SUCCESS(f'Ingestão concluída. {len(dados_novos)} registros processados.'))
        else:
            self.stdout.write(self.style.WARNING('Nenhum dado novo para ingerir.'))

    def _fetch_and_transform(self, url, tipo_metrica):
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            if not data:
                return []

            # Extrair série temporal do JSON
            serie = data[0].get('resultados', [])[0].get('series', [])[0].get('serie', {})
            
            # Transformar em DataFrame Pandas para limpeza robusta
            df = pd.DataFrame(list(serie.items()), columns=['periodo', 'valor'])
            
            # Limpar valores não numéricos ('-', '...', 'X')
            df['valor'] = pd.to_numeric(df['valor'], errors='coerce')
            df = df.dropna(subset=['valor'])

            registros = []
            for _, row in df.iterrows():
                periodo_str = str(row['periodo'])
                if len(periodo_str) == 6:
                    ano = int(periodo_str[:4])
                    mes = int(periodo_str[4:])
                    try:
                        data_ref = datetime(ano, mes, 1).date()
                        registros.append(MetricaSocioEconomica(
                            data=data_ref,
                            tipo_metrica=tipo_metrica,
                            valor=row['valor'],
                            regiao='Brasil',
                            estado=None
                        ))
                    except ValueError:
                        continue
            
            return registros

        except Exception as e:
            logger.error(f"Erro ao buscar/processar {tipo_metrica}: {e}")
            self.stdout.write(self.style.ERROR(f"Erro no processamento de {tipo_metrica}: {str(e)}"))
            return []
