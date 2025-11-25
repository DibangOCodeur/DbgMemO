from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin



# Personnalisation de l'interface d'administration pour le modèle User
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('last_name', 'first_name', 'email', 'contact', 'role', 'date_joined')
    list_filter = ('role',)
    search_fields = ('first_name', 'last_name', 'email', 'contact')
    ordering = ('date_joined',)

    # Ajouter des champs pour l'ajout et la modification de l'utilisateur
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Informations personnelles', {'fields': ('last_name', 'first_name', 'email', 'contact', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'first_name', 'last_name', 'email', 'contact', 'role'),
        }),
    )

# Personnalisation de l'interface d'administration pour le modèle Etudiant
class EtudiantAdmin(admin.ModelAdmin):
    list_display = ['nom', 'prenom', 'email', 'date_naissance', 'lieu_naissance', 'filiere', 'contact', 'theme_memoire']
    search_fields = ('nom', 'prenom', 'email', 'contact', 'date_inscription')
    ordering = ['nom', 'prenom', 'date_inscription']  # Pour trier par date_inscription

    def support_pdf_link(self, obj):
        if obj.support_pdf:
            return f'<a href="{obj.support_pdf.url}" target="_blank">Télécharger</a>'
        return "Pas de fichier"
    support_pdf_link.allow_tags = True  # Permet d'afficher le lien HTML dan



class FiliereAdmin(admin.ModelAdmin):
    list_display = ['nom','cycle',]
    search_fields = ('nom','cycle',)
    ordering = ['nom',]  # Pour trier par date_inscription



@admin.register(Paiement)
class PaiementAdmin(admin.ModelAdmin):
    list_display = ('etudiant', 'frais_impression', 'service_annexe', 'frais_annexe', 'montant','commission', 'statut')
    search_fields = ('etudiant','frais_impression','montant','commission')
    readonly_fields = ('montant', 'detail_frais','statut','commission')
    fieldsets = (
        ('Information', {
            'fields': ('etudiant', 'source','statut')
        }),
        ('Frais', {
            'fields': ('frais_impression', 'service_annexe', 'frais_annexe', 'montant','commission','detail_frais')
        }),
    )



# Enregistrement des modèles dans l'admin
admin.site.register(User, CustomUserAdmin)
admin.site.register(Etudiant, EtudiantAdmin)
admin.site.register(Filiere, FiliereAdmin)
