# forms.py
from django import forms
from .models import Dossier
from Utilisateurs.models import Etudiant
from Utilisateurs.forms import EtudiantForm
from .models import Etudiant

class DossierForm(forms.ModelForm):
    class Meta:
        model = Dossier
        fields = ['statut', 'livrer',]  # Ajoute tous les champs nécessaires

class EtudiantForm(forms.ModelForm):
    date_naissance = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        input_formats=['%Y-%m-%d', '%d/%m/%Y', '%d/%m/%y']  # Formats acceptés
    )
    class Meta:
        model = Etudiant
        fields = '__all__'