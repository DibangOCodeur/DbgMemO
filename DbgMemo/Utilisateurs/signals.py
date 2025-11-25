# Utilisateurs/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Etudiant
from Dossier.models import Dossier
import shutil
import os
from django.conf import settings

@receiver(post_save, sender=Etudiant)
def create_dossier_for_etudiant(sender, instance, created, **kwargs):
    """Crée un dossier lorsque l'étudiant est enregistré."""
    if created:
        # Créer un dossier pour l'étudiant
        dossier = Dossier.objects.create(etudiant=instance)

        # Si l'étudiant a un fichier 'support_pdf', nous le copions dans le dossier
        if instance.support_pdf:
            # Copie du fichier 'support_pdf' dans le dossier
            fichier_pdf_path = instance.support_pdf.path
            nom_fichier = os.path.basename(fichier_pdf_path)
            
            # Nouveau chemin où le fichier sera copié
            nouveau_chemin = os.path.join(settings.MEDIA_ROOT, 'dossiers/memoires/', nom_fichier)
            
            # Créer le dossier de destination s'il n'existe pas
            os.makedirs(os.path.dirname(nouveau_chemin), exist_ok=True)

            # Copier le fichier
            shutil.copy(fichier_pdf_path, nouveau_chemin)

            # Assigner le chemin du fichier copié au modèle Dossier
            dossier.support_pdf = f'dossiers/memoires/{nom_fichier}'
            dossier.save()

        print(f"Dossier créé pour l'étudiant {instance.nom} {instance.prenom}")
