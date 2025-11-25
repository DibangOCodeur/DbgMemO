from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from decimal import Decimal



# Modèle User personnalisé
class User(AbstractUser):
    contact = models.CharField(max_length=15, null=True, blank=True)  # Numéro de contact de l'utilisateur
    role = models.CharField(max_length=50, choices=[
        ('etudiant', 'Étudiant'),
        ('Personnel', 'Personnel'),
    ], default='etudiant')  # Rôle de l'utilisateur

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.role})"


Filiere_choices = (
    ('AUDIT ET CONTRÔLE DE GESTION - (ACG)', 'AUDIT ET CONTRÔLE DE GESTION - (ACG)'),
    ('ADMINISTRATION DES AFFAIRES - (ADAF)', 'ADMINISTRATION DES AFFAIRES - (ADAF)'),
    ('ANGLAIS - (ANG)', 'ANGLAIS - (ANG)'),
    ('SCIENCE JURIDIQUE OPTION DROIT PRIVE - (SCJ-PV)', 'SCIENCE JURIDIQUE OPTION DROIT PRIVE - (SCJ-PV)'),
    ('SCIENCE JURIDIQUE OPTION DROIT PUBLIC - (SCJ-PB)', 'SCIENCE JURIDIQUE OPTION DROIT PUBLIC - (SCJ-PB)'),
    ('FINANCE BANQUE ASSURANCE - (FBA)', 'FINANCE BANQUE ASSURANCE - (FBA)'),
    ('FINANCE COMPTABILITE ET GESTION DES ENTREPRISES - (FCGE)', 'FINANCE COMPTABILITE ET GESTION DES ENTREPRISES - (FCGE)'),
    ('GENIE CIVIL OPTION BATIMENT - (GBAT)', 'GENIE CIVIL OPTION BATIMENT - (GBAT)'),
    ('GENIE CIVIL OPTION TRAVAUX PUBLIC - (GTP)', 'GENIE CIVIL OPTION TRAVAUX PUBLIC - (GTP)'),
    ('GESTION DES RESSOURCES HUMAINE - (GRH)', 'GESTION DES RESSOURCES HUMAINE - (GRH)'),
    ('INFORMATIQUE OPTION GENIE LOGICIEL - (IGL)', 'INFORMATIQUE OPTION GENIE LOGICIEL - (IGL)'),
    ('LETTRES MODERNES - (LMO)', 'LETTRES MODERNES - (LMO)'),
    ('MARKETING MANAGEMENT - (MAM)', 'MARKETING MANAGEMENT - (MAM)'),
    ('MINE GEOLOGIE ET PETRÔLE - (MGP)', 'MINE GEOLOGIE ET PETRÔLE - (MGP)'),
    ('RESEAUX INFORMATIQUE ET TELECOMMUNICATION - (RIT)', 'RESEAUX INFORMATIQUE ET TELECOMMUNICATION - (RIT)'),
    ('SCIENCE ECONOMIQUE OPTION ECONOMIE - (SEG-ECO)', 'SCIENCE ECONOMIQUE OPTION ECONOMIE - (SEG-ECO)'),
    ('SCIENCE ECONOMIQUE OPTION GESTION - (SEG-GES)', 'SCIENCE ECONOMIQUE OPTION GESTION - (SEG-GES)'),
    (" SCIENCE DE L'INFORMATION ET DE LA COMMUNICATION - (SIC)", " SCIENCE DE L'INFORMATION ET DE LA COMMUNICATION - (SIC)"),
    ('SOCIOLOGIE ET ETHNOLOGIE - (SOC)', 'SOCIOLOGIE ET ETHNOLOGIE - (SOC)'),
    ('TOURISME HÔTELERIE - (TH)', 'TOURISME HÔTELERIE - (TH)'),
    ('TRANSPORT LOGISTIQUE - (TLOG)', 'TRANSPORT LOGISTIQUE - (TLOG)'),
)
Cycle_choices = (
    ('CYCLE PROFESSIONNEL', 'CYCLE PROFESSIONNEL'),
    ('CYCLE UNIVERSITAIRE', 'CYCLE UNIVERSITAIRE'),
)

class Filiere(models.Model):
    nom = models.CharField(max_length=100, choices=Filiere_choices)
    cycle = models.CharField(max_length=100, choices=Cycle_choices, null=False, blank=False, default='CYCLE UNIVERSITAIRE')
    def __str__(self):
        return self.nom



# Modèle Etudiant
class Etudiant(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='etudiant_profile')  # Lien avec le modèle User
    nom = models.CharField(max_length=50)
    prenom = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    date_naissance = models.DateField()
    lieu_naissance = models.CharField(max_length=100)
    filiere = models.ForeignKey('Filiere', on_delete=models.CASCADE)
    contact = models.CharField(max_length=15)
    theme_memoire = models.CharField(max_length=255, null=False, blank=False)  # Optionnel : thème de mémoire
    support_pdf = models.FileField(upload_to='Memoires/', null=False, blank=False)  # Support PDF pour le mémoire
    date_inscription = models.DateField(auto_now_add=True)  # Date d'inscription

    def __str__(self):
        return f"{self.nom} {self.prenom} "



class Paiement(models.Model):
    SOURCE_CHOICES = [
        ('ESPECE', 'ESPECE'),
        ('WAVE_MONEY', 'WAVE MONEY'),
    ]

    ANNEXE_CHOICES = [
        ('PAGE_DE_GARDE', 'PAGE DE GARDE 1.000fr'),
        ('PAGINATION_TABLE_MATIERE', 'PAGINATION (TABLE DE MATIERE) 1.500fr'),
        ('COMPLET', 'COMPLET [P,PDG,TDM] 2.500fr'),
    ]

    # Définition des prix pour les services annexes (doit correspondre aux clés de ANNEXE_CHOICES)
    PRIX_ANNEXE = {
        'PAGE_DE_GARDE': 1000,
        'PAGINATION_TABLE_MATIERE': 1500,
        'COMPLET': 2500,
    }

    # Relations et champs de base
    etudiant = models.ForeignKey('Etudiant', on_delete=models.CASCADE, related_name='paiements')
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    statut = models.BooleanField(default=False, verbose_name="statut")
    reference = models.CharField(max_length=100, unique=True, editable=False)
    commission = models.DecimalField(max_digits=10, decimal_places=2, null=True, verbose_name="commission")
    reference_paiement = models.CharField(max_length=20)
    date_paiement = models.DateTimeField(auto_now_add=True)

    # Champs de frais
    frais_impression = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        verbose_name="Frais d'impression"
    )
    
    service_annexe = models.BooleanField(
        default=False,
        verbose_name="Service annexe"
    )
    
    frais_annexe = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Frais annexe"
    )

    intitule_annexe = models.CharField(
        max_length=50, 
        choices=ANNEXE_CHOICES, 
        blank=True, 
        null=True,
        verbose_name="Intitulé du service annexe"
    )

    # Champ montant calculé (non éditable)
    montant = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        editable=False,
        verbose_name="Montant total"
    )

    class Meta:
        verbose_name = "Paiement"
        verbose_name_plural = "Paiements"
        ordering = ['-date_paiement']

    def save(self, *args, **kwargs):
        # Génération de la référence si elle n'existe pas
        if not self.reference:
            self.reference = f"PAY-{uuid.uuid4().hex[:10].upper()}"

        # Calcul des frais annexes
        self.calculer_frais_annexe()
        
        # Calcul du montant total
        self.calculer_montant()
        
        super().save(*args, **kwargs)

    def calculer_frais_annexe(self):
        """Calcule automatiquement les frais annexes en fonction du service choisi"""
        if self.service_annexe and self.intitule_annexe:
            self.frais_annexe = Decimal(str(self.PRIX_ANNEXE.get(self.intitule_annexe, 0)))
        else:
            self.frais_annexe = Decimal('0')
            if not self.service_annexe:
                self.intitule_annexe = None

    def calculer_montant(self):
        """Calcule le montant total du paiement"""
        self.montant = (self.frais_impression or Decimal('0')) + (self.frais_annexe or Decimal('0'))
        return self.montant

    def __str__(self):
        return f"{self.etudiant.nom} - {self.montant} FCFA"

    @property
    def detail_frais(self):
        """Retourne le détail des frais pour l'admin"""
        details = [f"Impression: {self.frais_impression} FCFA"]
        if self.service_annexe and self.intitule_annexe:
            display_name = dict(self.ANNEXE_CHOICES).get(self.intitule_annexe, self.intitule_annexe)
            details.append(f"{display_name}: {self.frais_annexe} FCFA")
        return " + ".join(details)