from django.urls import path, include 
from . import views
from .views import login_view
from django.contrib.auth.views import LogoutView
from .views import creer_paiement

urlpatterns = [
    path('', login_view, name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('recu-paiement/<int:paiement_id>/', views.recu_paiement, name='recu_paiement'),
    path('paiement/<int:etudiant_id>/', views.creer_paiement, name='creer_paiement'),
    path('enregistrer/', views.enregistrer_etudiant, name='enregistrer_etudiant'),
    path('list_paiement/', views.list_paiement, name='list_paiement'),
    path('list_etudiant/', views.list_etudiant, name='list_etudiant'),
    path('list_recu/', views.list_recu, name='list_recu'),

    path('etudiant/<int:pk>/', views.detail_etudiant, name='detail_etudiant'),
    path('etudiant/modifier/<int:pk>/', views.modifier_etudiant, name='modifier_etudiant'),
    path('etudiant/supprimer/<int:pk>/', views.supprimer_etudiant, name='supprimer_etudiant'),
    path('recu-paiement/<int:paiement_id>/', views.recu_etudiant, name='recu_etudiant'),
    path('paiement/modifier/<int:paiement_id>/', views.modifier_paiement, name='modifier_paiement'),
    path('paiement/supprimer/<int:paiement_id>/', views.supprimer_paiement, name='supprimer_paiement'),
    path('paiement-detail/detail/<int:paiement_id>/', views.detail_paiement, name='detail_paiement'),
    path('list_memoire/', views.list_memoire, name="list_memoire"),
    path('statistique/', views.statistique, name="statistique"),
    path('revenus/', views.revenus, name='revenus'),

]
