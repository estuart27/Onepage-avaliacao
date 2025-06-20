from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    path('', views.home, name='home'),  # Página inicial que lista todos os colaboradores
    path('avaliar/colaborador/<int:colaborador_id>/', views.avaliar_colaborador, name='avaliar_colaborador'),
    path('avaliar/restaurante/<int:colaborador_id>/', views.avaliacao_restaurante, name='avaliar_restaurante'),
    path('perfil/<int:colaborador_id>/', views.perfil_colaborador, name='perfil_colaborador'),
    path('colaborador/<int:colaborador_id>/feedback/', views.feedback_colaborador, name='feedback_colaborador'),
    path('perfil-restaurante/<int:colaborador_id>/', views.perfil_colaborador_restaurante, name='perfil_colaborador_restaurante'),
    path('feedback-restaurante/<int:colaborador_id>/', views.feedback_colaborador_restaurante, name='feedback_colaborador_restaurante'),
    path('suporte/relatorio/', views.relatorio_op, name='relatorio'),
    path('api/generate-report/', views.generate_report, name='generate_report'),
    path('validar-codigo/', views.validar_codigo, name='validar_codigo'),
    path('colaboladores/ranking ', views.ranking , name='ranking'),

    # /api/generate-report/',



] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

