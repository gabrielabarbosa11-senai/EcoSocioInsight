from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from core.services.agent_orchestrator import AntigravityOrchestrator

@require_POST
def send_message(request):
    query = request.POST.get('query', '')
    if not query:
        return HttpResponse("")
        
    try:
        # Instancia e roda a pipeline multi-agente
        orchestrator = AntigravityOrchestrator()
        response_html = orchestrator.process_query(query)
    except Exception as e:
        response_html = f"<strong class='text-red-500'>Erro interno do Orquestrador IA:</strong> {str(e)}"
    
    # Prepara o HTML parcial para ser injetado pelo HTMX via hx-swap="beforeend"
    partial_html = f"""
    <!-- Mensagem do Usuário -->
    <div class="self-end bg-indigo-100 border border-indigo-200 rounded-2xl rounded-tr-none p-3 max-w-[85%] shadow-sm ml-auto text-right">
        <p class="text-sm text-indigo-900">{query}</p>
    </div>
    
    <!-- Resposta do Agente Sintetizador -->
    <div class="self-start bg-white border border-gray-200 rounded-2xl rounded-tl-none p-3 max-w-[85%] shadow-sm">
        <div class="text-sm text-gray-700 space-y-2">
            {response_html}
        </div>
    </div>
    """
    
    return HttpResponse(partial_html)
