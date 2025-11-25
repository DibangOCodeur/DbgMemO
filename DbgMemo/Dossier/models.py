from django.db import models
from Utilisateurs.models import Etudiant

class Dossier(models.Model):
    etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE, related_name='dossiers')
    date_creation = models.DateTimeField(auto_now_add=True)  # Date et heure de la création du dossier
    date_modification = models.DateTimeField(auto_now=True)  # Date de la dernière modification
    statut = models.BooleanField(default=False)   # Statut du dossier
    document_joint = models.FileField(upload_to='dossiers/%Y/%m/%d/', blank=True, null=True)  # Pour stocker des fichiers liés au dossier
    livrer = models.BooleanField(default=False)  
    support_pdf = models.FileField(upload_to='dossiers/memoires/', null=True, blank=True)  # Support PDF du mémoire de l'étudiant

    def __str__(self):
        return f"Dossier de {self.etudiant.nom} {self.etudiant.prenom}"

    def valider_dossier(self):
        """Méthode pour valider le dossier (changement de statut en 'validé')"""
        self.statut = True
        self.save()

    def cloturer_dossier(self):
        """Méthode pour clôturer le dossier"""
        self.livrer = True
        self.save()
