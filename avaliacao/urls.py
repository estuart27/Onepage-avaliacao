from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),  # Página inicial que lista todos os colaboradores
    path('avaliar/<int:colaborador_id>/', views.avaliar_colaborador, name='avaliar_colaborador'),
    path('perfil/<int:colaborador_id>/', views.perfil_colaborador, name='perfil_colaborador'),
    path('colaborador/<int:colaborador_id>/feedback/', views.feedback_colaborador, name='feedback_colaborador'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
