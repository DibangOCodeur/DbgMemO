from Utilisateurs.models import * 
from . models import *
from django.shortcuts import render, get_object_or_404, redirect
from .forms import *
from Utilisateurs.forms import EtudiantForm
from django.core.mail import send_mail
from Utilisateurs.models import *
from django.contrib import messages  # Ajoutez cette ligne
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.paginator import Paginator
from datetime import date
from django.utils.formats import date_format
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone








def list_dossiers(request):
    query = request.GET.get('q', '').strip()
    dossiers = Dossier.objects.select_related('etudiant').all()
    
    etudiants_ids = [d.etudiant.id for d in dossiers if d.etudiant]
    paiements_dict = {
        p.etudiant_id: p 
        for p in Paiement.objects.filter(etudiant_id__in=etudiants_ids)
    }

    if query:
        search_conditions = Q()
        text_fields = ['nom', 'prenom']
        optional_fields = ['filiere', 'contact', 'email', 'matricule']
        
        for field in text_fields + optional_fields:
            try:
                if hasattr(Dossier.etudiant.field.related_model, field):
                    field_type = Dossier.etudiant.field.related_model._meta.get_field(field)
                    if hasattr(field_type, 'get_internal_type') and field_type.get_internal_type() in ['CharField', 'TextField']:
                        search_conditions |= Q(**{f'etudiant__{field}__icontains': query})
            except:
                continue
        
        dossiers = dossiers.filter(search_conditions)
    
    return render(request, 'users/all-holiday.html', {
        'dossiers': dossiers,
        'paiements_dict': paiements_dict,
        'query': query
    })


def modifier_dossier(request, dossier_id):
    dossier = get_object_or_404(Dossier, id=dossier_id)
    etudiant = dossier.etudiant
    ancien_statut = dossier.statut
    ancien_livrer = dossier.livrer

    if request.method == 'POST':
        dossier_form = DossierForm(request.POST, request.FILES, instance=dossier)
        etudiant_form = EtudiantForm(request.POST, request.FILES, instance=etudiant)
        
        if dossier_form.is_valid() and etudiant_form.is_valid():
            dossier_form.save()
            etudiant_form.save()
            
            # Récupérer le dossier fraîchement sauvegardé
            nouveau_dossier = Dossier.objects.get(id=dossier_id)
            
            # Vérifier si le statut a changé
            if ancien_statut != nouveau_dossier.statut:
                # Envoyer l'email pour l'impression
                subject = 'IMPRESSION DE MEMOIRE CHEZ DbgMemO'
                message = f"""
                Bonjour M./Mme {etudiant.nom} {etudiant.prenom},

                Nous tenons à vous informer que vos exemplaire de mémoire ont bien été imprimés.

                Veuillez vous rendre dans nos locaux avec votre reçu de paiement pour la récupération.

                Cordialement,
                DbgMemO
                """
                
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [etudiant.email],
                    fail_silently=False,
                )
            
            # Vérifier si le statut livrer a changé
            if ancien_livrer != nouveau_dossier.livrer:
                # Envoyer l'email pour la récupération
                subject = "RECUPERATION DE MEMOIRE CHEZ DbgMemO"
                message = f"""
                Bonjour M./Mme {etudiant.nom} {etudiant.prenom},

                Ce mail confirme que vous avez récupéré vos exemplaires de mémoire dans nos locaux.

                L'équipe DbgMemO tient à vous remercier d'avoir choisi notre service d'impression de mémoire.

                Cordialement,
                DbgMemO
                """
                
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [etudiant.email],
                    fail_silently=False,
                )
            
            return redirect('list_dossiers')
    else:
        initial_data = {}
        if etudiant.date_naissance:
            initial_data['date_naissance'] = etudiant.date_naissance.strftime('%Y-%m-%d')
        
        dossier_form = DossierForm(instance=dossier)
        etudiant_form = EtudiantForm(instance=etudiant, initial=initial_data)

    return render(request, 'users/form-wizard.html', {
        'form': dossier_form,
        'etudiant_form': etudiant_form,
        'dossier': dossier
    }) 


    

def detail_dossier(request, dossier_id):  # Le paramètre est dossier_id, pas paiement_id
    # Récupération du dossier
    dossier = get_object_or_404(Dossier, id=dossier_id)
    
    # Récupération des paiements associés à l'étudiant du dossier
    paiements = Paiement.objects.filter(etudiant=dossier.etudiant)
    
    return render(request, 'users/oeil.html', {
        'dossier': dossier,
        'paiements': paiements  # Passage des paiements au template
    })



@login_required
def supprimer_dossier(request, dossier_id):
    dossier = get_object_or_404(Dossier, id=dossier_id)
    if request.method == 'POST':
        dossier.delete()
        messages.success(request, "Le dossier a été supprimé avec succès.")
        return redirect('list_dossiers')
    return render(request, 'users/confirm_delete.html', {'dossier': dossier})




# Vue pour la liste des dossiers du jour

def dossiers_du_jour(request):
    today = timezone.now().date()
    query = request.GET.get('q', '').strip()
    
    # Requête de base
    dossiers = Dossier.objects.filter(
        date_creation__date=today,
    ).select_related('etudiant').order_by('-date_creation')
    
    # Filtre de recherche corrigé
    if query:
        dossiers = dossiers.filter(
            Q(etudiant__nom__icontains=query) |         # Champ texte
            Q(etudiant__prenom__icontains=query) |      # Champ texte
            Q(etudiant__filiere__nom__icontains=query) |  # Si filiere est ForeignKey
            Q(etudiant__contact__icontains=query)  # Champ texte
        ).distinct()
    
    # Pagination
    paginator = Paginator(dossiers, 10)
    page_number = request.GET.get('page')
    
    try:
        page_obj = paginator.get_page(page_number)
    except (PageNotAnInteger, EmptyPage):
        page_obj = paginator.get_page(1)
    
    context = {
        'today': today,
        'today_formatted': date_format(today, "l j F Y"),
        'page_obj': page_obj,
        'total_dossiers': paginator.count,
        'query': query,
    }
    
    return render(request, 'users/dossier-jour.html', context)



#Vue pour les dossiers traités 

def dossiers_traites(request):
    query = request.GET.get('q', '').strip()
    
    # Récupération des dossiers traités
    dossiers_traites = Dossier.objects.filter(statut=True).select_related('etudiant').order_by('-date_modification')
    
    # Appliquer le filtre de recherche sur cette même requête
    if query:
        dossiers_traites = dossiers_traites.filter(
            Q(etudiant__nom__icontains=query) |
            Q(etudiant__prenom__icontains=query) |
            Q(etudiant__filiere__nom__icontains=query) |
            Q(etudiant__contact__icontains=query)
        ).distinct()

    # Pagination
    paginator = Paginator(dossiers_traites, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'query': query,  # Pour garder la recherche dans l'input
        'total_dossiers': dossiers_traites.count(),
        'titre': 'Dossiers traités'
    }

    return render(request, 'users/dossier-traiter.html', context)


# Vue pour les Memoire livré
def memoires_livres(request):
    query = request.GET.get('q', '').strip()
    
    # Récupération des dossiers traités    
    # Appliquer le filtre de recherche sur cette même requête
   
    # Récupérer les dossiers livrés (livrer=True) avec leur PDF
    dossiers_livres = Dossier.objects.filter(
        livrer=True
    ).exclude(
        support_pdf__isnull=True
    ).exclude(
        support_pdf__exact=''
    ).order_by('-date_modification')

    if query:
        dossiers_livres = dossiers_livres.filter(
            Q(etudiant__nom__icontains=query) |
            Q(etudiant__prenom__icontains=query) |
            Q(etudiant__filiere__nom__icontains=query) |
            Q(etudiant__contact__icontains=query)
        ).distinct()
    
    # Pagination - 10 éléments par page
    paginator = Paginator(dossiers_livres, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'total_dossiers': dossiers_livres.count(),
        'titre': 'Mémoires livrés'
    }
    
    return render(request, 'users/memoire-livre.html', context)


#Vue de la liste des service annexe
def dossiers_service_annexe(request):
    query = request.GET.get('q', '').strip()
    # Récupérer les paiements avec service annexe et leurs relations
    paiements_annexe = Paiement.objects.filter(
        service_annexe=True
    ).select_related('etudiant').order_by('-date_paiement')


    if query:
        paiements_annexe = paiements_annexe.filter(
            Q(etudiant__nom__icontains=query) |
            Q(etudiant__prenom__icontains=query) |
            Q(etudiant__filiere__nom__icontains=query) |
            Q(etudiant__contact__icontains=query)
        ).distinct()
    
    # Pagination - 10 éléments par page
    paginator = Paginator(paiements_annexe, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Calcul des statistiques
    total_montant = sum(p.montant for p in paiements_annexe)
    total_commission = sum(p.commission for p in paiements_annexe)
    
    context = {
        'page_obj': page_obj,
        'total_dossiers': paiements_annexe.count(),
        'total_montant': total_montant,
        'total_commission': total_commission,
        'titre': 'Dossiers avec service annexe'
    }
    
    return render(request, 'users/liste-Sannexe.html', context)
