from django.contrib import admin
from .models import Dossier


# Modèle Dossier dans le admin Django
@admin.register(Dossier)
class DossierAdmin(admin.ModelAdmin):
    list_display = ('etudiant_nom_complet', 'statut', 'livrer', 'date_creation')
    list_filter = ('statut', 'livrer', 'date_creation')
    search_fields = ('etudiant__nom', 'etudiant__prenom')
    readonly_fields = ('date_creation', 'date_modification')

    def etudiant_nom_complet(self, obj):
        return f"{obj.etudiant.nom} {obj.etudiant.prenom}"
    etudiant_nom_complet.short_description = 'Étudiant'

