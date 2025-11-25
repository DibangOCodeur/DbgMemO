from django.urls import path
from .import views


urlpatterns = [
  path('list-dossier/', views.list_dossiers, name='list_dossiers'),
  path('dossiers/modifier/<int:dossier_id>/', views.modifier_dossier, name='modifier_dossier'),
  path('dossier/<int:dossier_id>/', views.detail_dossier, name='detail_dossier'),
  path('dossier/<int:dossier_id>/supprimer/', views.supprimer_dossier, name='supprimer_dossier'),
  path('dossiers_du_jour/', views.dossiers_du_jour, name='dossiers_du_jour'),
  path('dossiers_traites/', views.dossiers_traites, name='dossiers_traites'),
  path('memoires_livres/', views.memoires_livres, name='memoires_livres'),
  path('dossiers_service_annexe/', views.dossiers_service_annexe, name='dossiers_service_annexe'),
]
