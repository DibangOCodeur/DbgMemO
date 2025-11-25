from django.apps import AppConfig

class DossierConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Dossier'  # Adaptez au nom exact de votre application

    def ready(self):
        # Importez les signaux seulement quand l'application est prête
        from . import signals  # Import relatif
        print("Signaux Dossier chargés avec succès")  # Message de confirmation
