"""
URL Configuration — SocioEcoData
Mapeia as rotas para as views de Dashboard e Chat (HTMX).
"""
from django.contrib import admin
from django.urls import path
from core.views.dashboard import index
from core.views.chat import send_message
from core.views.about import about

urlpatterns = [
    path('admin/', admin.site.urls),

    # Rota principal: Dashboard analítico com Chart.js
    path('', index, name='dashboard'),
    
    # Rota Sobre: Informações sobre o Dashboard
    path('sobre/', about, name='about'),

    # Rota do Chat HTMX — recebe POST com a query do usuário
    # e retorna HTML parcial com a resposta do Antigravity Orchestrator
    path('chat/send/', send_message, name='chat_send'),
]
