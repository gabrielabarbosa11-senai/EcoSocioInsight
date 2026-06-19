import json
from datetime import date
from decimal import Decimal
from django.shortcuts import render
from core.models import MetricaSocioEconomica

# PNAD Contínua (unemployment) starts March 2012. Filtering from this date
# ensures the chart never shows a false 0% unemployment line for earlier periods.
_PNAD_START = date(2012, 3, 1)

def index(request):
    """
    Dashboard Analítico Principal.
    Calcula o "Índice de Miséria" (Inflação + Desemprego) e variações.
    """
    metricas = MetricaSocioEconomica.objects.filter(
        tipo_metrica__in=['IPCA', 'Desemprego'],
        regiao='Brasil',
        data__gte=_PNAD_START,
    ).order_by('data')

    historico = {}
    for m in metricas:
        dt_str = m.data.strftime("%Y-%m")
        if dt_str not in historico:
            historico[dt_str] = {'IPCA': Decimal('0.0'), 'Desemprego': Decimal('0.0')}
        historico[dt_str][m.tipo_metrica] = m.valor

    labels = []
    ipca_data = []
    desemprego_data = []
    miseria_data = []

    # Only months where both metrics were actually ingested are used for the KPI.
    # PNAD (unemployment) is quarterly, so recent months may lack Desemprego data —
    # using those would produce a falsely low Misery Index.
    complete_miseria = []

    indice_miseria_atual = Decimal('0.0')
    indice_miseria_anterior = Decimal('0.0')

    datas_ordenadas = sorted(historico.keys())
    for dt in datas_ordenadas:
        ipca = historico[dt]['IPCA']
        desemp = historico[dt]['Desemprego']
        miseria = ipca + desemp

        labels.append(dt)
        ipca_data.append(float(ipca))
        desemprego_data.append(float(desemp))
        miseria_data.append(float(miseria))

        if ipca > 0 and desemp > 0:
            complete_miseria.append(float(miseria))

    if len(complete_miseria) >= 1:
        indice_miseria_atual = complete_miseria[-1]
    if len(complete_miseria) >= 2:
        indice_miseria_anterior = complete_miseria[-2]

    variacao = 0
    if indice_miseria_anterior > 0:
        variacao = ((indice_miseria_atual - indice_miseria_anterior) / indice_miseria_anterior) * 100

    # Per-metric KPI values — latest non-zero entry for each series
    ipca_series = [(dt, historico[dt]['IPCA']) for dt in datas_ordenadas if historico[dt]['IPCA'] > 0]
    desemp_series = [(dt, historico[dt]['Desemprego']) for dt in datas_ordenadas if historico[dt]['Desemprego'] > 0]

    ipca_atual = float(ipca_series[-1][1]) if ipca_series else 0
    ipca_ref = ipca_series[-1][0] if ipca_series else ''
    ipca_anterior_val = float(ipca_series[-2][1]) if len(ipca_series) >= 2 else 0
    ipca_variacao = ((ipca_atual - ipca_anterior_val) / ipca_anterior_val * 100) if ipca_anterior_val > 0 else 0

    desemp_atual = float(desemp_series[-1][1]) if desemp_series else 0
    desemp_ref = desemp_series[-1][0] if desemp_series else ''
    desemp_anterior_val = float(desemp_series[-2][1]) if len(desemp_series) >= 2 else 0
    desemp_variacao = ((desemp_atual - desemp_anterior_val) / desemp_anterior_val * 100) if desemp_anterior_val > 0 else 0

    context = {
        'active_metric': request.GET.get('metric', 'dashboard'),
        # Misery Index KPIs
        'indice_miseria_atual': f"{indice_miseria_atual:.2f}",
        'variacao': f"{variacao:.2f}",
        # IPCA KPIs
        'ipca_atual': f"{ipca_atual:.2f}",
        'ipca_variacao': f"{ipca_variacao:.2f}",
        'ipca_ref': ipca_ref,
        # Desemprego KPIs
        'desemp_atual': f"{desemp_atual:.2f}",
        'desemp_variacao': f"{desemp_variacao:.2f}",
        'desemp_ref': desemp_ref,
        'chart_data_json': json.dumps({
            'labels': labels,
            'ipca': ipca_data,
            'desemprego': desemprego_data,
            'miseria': miseria_data
        })
    }

    return render(request, 'dashboard.html', context)
