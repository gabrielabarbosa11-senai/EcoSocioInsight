import json
from decimal import Decimal
from django.shortcuts import render
from core.models import MetricaSocioEconomica

def index(request):
    """
    Dashboard Analítico Principal.
    Calcula o "Índice de Miséria" (Inflação + Desemprego) e variações.
    """
    metricas = MetricaSocioEconomica.objects.filter(
        tipo_metrica__in=['IPCA', 'Desemprego']
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

    if len(miseria_data) >= 1:
        indice_miseria_atual = miseria_data[-1]
    if len(miseria_data) >= 2:
        indice_miseria_anterior = miseria_data[-2]

    # Cálculo da variação
    variacao = 0
    if indice_miseria_anterior > 0:
        variacao = ((indice_miseria_atual - indice_miseria_anterior) / indice_miseria_anterior) * 100

    context = {
        'indice_miseria_atual': f"{indice_miseria_atual:.2f}",
        'variacao': f"{variacao:.2f}",
        'chart_data_json': json.dumps({
            'labels': labels,
            'ipca': ipca_data,
            'desemprego': desemprego_data,
            'miseria': miseria_data
        })
    }
    
    return render(request, 'dashboard.html', context)
