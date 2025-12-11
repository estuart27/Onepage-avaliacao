from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    path('', views.home, name='home'),  # Página inicial que lista todos os colaboradores
    path('avaliar/colaborador/<int:colaborador_id>/', views.avaliar_colaborador, name='avaliar_colaborador'),
    path('avaliar/restaurante/<int:colaborador_id>/', views.avaliacao_restaurante, name='avaliar_restaurante'),
    path('perfil/<int:colaborador_id>/', views.perfil_colaborador, name='perfil_colaborador'),
    path('suporte/relatorio/', views.relatorio_op, name='relatorio'),
    path('api/analise-ia/', views.api_analise_ia, name='api_analise_ia'),
    path('validar-codigo/', views.validar_codigo, name='validar_codigo'),
    path('colaboladores/ranking ', views.ranking , name='ranking'),
    path("painel-medalhas/", views.painel_medalhas, name="painel_medalhas"),
    path("painel-medalhas/aceitar/<int:sugestao_id>/", views.aceitar_sugestao, name="aceitar_sugestao"),
    path("painel-medalhas/excluir/<int:sugestao_id>/", views.excluir_sugestao, name="excluir_sugestao"),


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

