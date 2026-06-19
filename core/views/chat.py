from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils.html import escape
from django.views.decorators.http import require_POST
from core.services.agent_orchestrator import AntigravityOrchestrator

@login_required
@require_POST
def send_message(request):
    query = request.POST.get('query', '')
    if not query:
        return HttpResponse("")

    if len(query) > 1000:
        query = query[:1000]

    try:
        orchestrator = AntigravityOrchestrator()
        response_html = orchestrator.process_query(query)
    except Exception as e:
        response_html = f"<strong class='text-red-500'>Erro interno do Orquestrador IA:</strong> {escape(str(e))}"

    partial_html = f"""
    <div class="self-end bg-indigo-100 border border-indigo-200 rounded-2xl rounded-tr-none p-3 max-w-[85%] shadow-sm ml-auto text-right">
        <p class="text-sm text-indigo-900">{escape(query)}</p>
    </div>
    <div class="self-start bg-white border border-gray-200 rounded-2xl rounded-tl-none p-3 max-w-[85%] shadow-sm">
        <div class="text-sm text-gray-700 space-y-2">
            {response_html}
        </div>
    </div>
    """

    return HttpResponse(partial_html)
