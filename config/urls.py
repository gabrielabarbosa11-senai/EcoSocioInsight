"""
URL Configuration — SocioEcoData
Mapeia as rotas para as views de Dashboard e Chat (HTMX).
"""
from django.contrib import admin
from django.templatetags.static import static
from django.urls import path
from django.views.generic.base import RedirectView
from core.views.dashboard import index
from core.views.chat import send_message
from core.views.about import about

urlpatterns = [
    path('admin/', admin.site.urls),

    # Browsers request /favicon.ico automatically regardless of <link> tags
    path('favicon.ico', RedirectView.as_view(url=static('img/favicon.png'), permanent=True)),

    path('', index, name='dashboard'),
    path('sobre/', about, name='about'),
    path('chat/send/', send_message, name='chat_send'),
]
