from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Dossier

@receiver(post_save, sender=Dossier)
def envoyer_mail_si_statut_change(sender, instance, created, **kwargs):
    """Envoi d'email quand le statut passe à True (Traité)"""
    if created:
        return  # Ne rien faire pour les nouvelles créations
    
    try:
        old = Dossier.objects.get(pk=instance.pk)
        # Vérifier si le statut est passé de False à True
        if not old.statut and instance.statut:
            subject = 'IMPRESSION DE MEMOIRE CHEZ DbgMemO'
            message = f"""
            Bonjour M./Mme {instance.etudiant.nom} {instance.etudiant.prenom},

            Nous tenons à vous informer que votre mémoire a bien été imprimé.

            Veuillez vous rendre dans nos locaux avec votre reçu de paiement pour la récupération.

            Cordialement,
            DbgMemO
            """
            recipient_list = [instance.etudiant.email]
            send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_list)
            print(f"Email envoyé à {instance.etudiant.email}")
            
    except Dossier.DoesNotExist:
        pass