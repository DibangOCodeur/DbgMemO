from django import forms
from .models import *
from decimal import Decimal

class LoginForm(forms.Form):
    username = forms.CharField(label="Nom d'utilisateur ou Email")
    password = forms.CharField(widget=forms.PasswordInput, label="Mot de passe")

class EtudiantForm(forms.ModelForm):
    class Meta:
        model = Etudiant
        fields = ['nom', 'prenom', 'email', 'date_naissance', 'lieu_naissance', 'filiere', 'contact', 'theme_memoire', 'support_pdf']
        widgets = {
            'date_naissance': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super(EtudiantForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})



# class PaiementForm(forms.ModelForm):
#     class Meta:
#         model = Paiement
#         fields = ['frais_impression', 'service_annexe', 'intitule_annexe', 'source', 'reference_paiement', 'commission', 'statut']
#         widgets = {
#             'frais_impression': forms.NumberInput(attrs={
#                 'step': '0.01', 
#                 'min': '0',
#                 'class': 'form-control',
#                 'placeholder': 'Entrez le montant des frais d\'impression'
#             }),
#             'service_annexe': forms.CheckboxInput(attrs={
#                 'class': 'form-check-input',
#                 'onchange': "toggleAnnexeFields(this)"
#             }),
#             'intitule_annexe': forms.Select(attrs={
#                 'class': 'form-control',
#                 'onchange': "updateAnnexeFrais(this)"
#             }),
#             'source': forms.Select(attrs={
#                 'class': 'form-control'
#             }),
#             'reference_paiement': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Référence du paiement'
#             }),
#             'commission': forms.NumberInput(attrs={
#                 'step': '0.01', 
#                 'min': '0',
#                 'class': 'form-control',
#                 'placeholder': 'Entrez le montant de la commission'
#             }),

#         }
#         labels = {
#             'frais_impression': "Frais d'impression ",
#             'intitule_annexe': "Intitulé du service annexe",
#             'source': "Moyen de paiement",
#             'reference_paiement': "Référence",
#             'commission': "Commission"
#         }

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields['intitule_annexe'].required = False
        
#         # On rend le champ frais_annexe invisible car il sera géré automatiquement
#         if 'frais_annexe' in self.fields:
#             del self.fields['frais_annexe']

#     def clean(self):
#         cleaned_data = super().clean()
#         service_annexe = cleaned_data.get('service_annexe')
#         intitule_annexe = cleaned_data.get('intitule_annexe')

#         if service_annexe and not intitule_annexe:
#             self.add_error('intitule_annexe', "Veuillez préciser l'intitulé du service annexe lorsque le service annexe est coché")

#         return cleaned_data

#     def save(self, commit=True):
#         instance = super().save(commit=False)
        
#         # Gestion automatique des frais annexes
#         if instance.service_annexe and instance.intitule_annexe:
#             prix_annexe = instance.PRIX_ANNEXE.get(instance.intitule_annexe, 0)
#             instance.frais_annexe = prix_annexe
#         else:
#             instance.frais_annexe = 0

#         # Calcul du montant total
#         instance.montant = instance.frais_impression + instance.frais_annexe

#         if commit:
#             instance.save()
#         return instance




class PaiementForm(forms.ModelForm):
    class Meta:
        model = Paiement
        fields = ['frais_impression', 'service_annexe', 'intitule_annexe', 'source', 'reference_paiement', 'commission', 'statut']
        widgets = {
            'frais_impression': forms.NumberInput(attrs={
                'step': '0.01', 
                'min': '0',
                'class': 'form-control',
                'placeholder': 'Entrez le montant des frais d\'impression'
            }),
            'service_annexe': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'onchange': "toggleAnnexeFields(this)"
            }),
            'intitule_annexe': forms.Select(attrs={
                'class': 'form-control',
                'onchange': "updateAnnexeFrais(this)"
            }),
            'source': forms.Select(attrs={
                'class': 'form-control'
            }),
            'reference_paiement': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Référence du paiement'
            }),
            'commission': forms.NumberInput(attrs={
                'step': '0.01', 
                'min': '0',
                'class': 'form-control',
                'placeholder': 'Entrez le montant de la commission'
            }),
        }
        labels = {
            'frais_impression': "Frais d'impression",
            'intitule_annexe': "Intitulé du service annexe",
            'source': "Moyen de paiement",
            'reference_paiement': "Référence",
            'commission': "Commission"
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['intitule_annexe'].required = False
        if 'frais_annexe' in self.fields:
            del self.fields['frais_annexe']

    def clean(self):
        cleaned_data = super().clean()
        service_annexe = cleaned_data.get('service_annexe')
        intitule_annexe = cleaned_data.get('intitule_annexe')

        if service_annexe and not intitule_annexe:
            self.add_error('intitule_annexe', "Veuillez préciser l'intitulé du service annexe lorsque le service annexe est coché")

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Calcul des frais annexes
        if instance.service_annexe and instance.intitule_annexe:
            instance.frais_annexe = Decimal(str(instance.PRIX_ANNEXE.get(instance.intitule_annexe, 0)))
        else:
            instance.frais_annexe = Decimal('0')

        # Calcul du montant total
        instance.montant = (instance.frais_impression or Decimal('0')) + instance.frais_annexe

        if commit:
            instance.save()
        return instance