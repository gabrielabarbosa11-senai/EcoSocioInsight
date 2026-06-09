from django.shortcuts import render

def about(request):
    """
    View para a página 'Sobre' (About).
    Explica o objetivo do dashboard, a fonte dos dados e o uso do agente.
    """
    context = {
        'active_metric': 'about'
    }
    return render(request, 'about.html', context)
