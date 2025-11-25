from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from .forms import *
from .models import *
from datetime import datetime
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from Dossier.models import Dossier
from django.db.models import Sum
from django.db.models import Q
from django.utils.timezone import now
from datetime import date

User = get_user_model()



# -----------------------------------------------------------
# -----------------------------------------------------------
# vues de connexion 

def login_view(request):
    if request.user.is_authenticated:
        return redirect('admin_dashboard')  # Redirige vers la page d'accueil si déjà connecté
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f"Bienvenue {user.username} !")
            return redirect('admin_dashboard')  # Redirige vers la page d'accueil après connexion
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
    
    return render(request, 'users/page-login.html')


@staff_member_required  # autorise seulement les utilisateurs admin
def admin_dashboard(request):
    etudiants = Etudiant.objects.all()
    paiements = Paiement.objects.all()
    dossiers = Dossier.objects.all()

    nb_etudiants = etudiants.count()
    nb_dossiers = dossiers.count()
    nb_paiements = paiements.count()
    
    sm_paiements = paiements.aggregate(total=Sum('montant'))['total'] or 0

    derniers_paiements = Paiement.objects.all().order_by('-date_paiement')[:5]
    context = {
        'paiements': derniers_paiements,
    }

    return render(request, 'users/index.html', {
        'etudiants': etudiants,
        'paiements': paiements,
        'dossiers':dossiers,

        'nb_etudiants': nb_etudiants,
        'nb_dossiers' : nb_dossiers,
        'nb_paiements' : nb_paiements,
        'sm_paiements': sm_paiements,
    }) 


# -----------------------------------------------------------
# -----------------------------------------------------------
# vue d'admission 
def enregistrer_etudiant(request):
    if request.method == 'POST':
        nom = request.POST.get('nom')
        prenom = request.POST.get('prenom')
        email = request.POST.get('email')
        date_naissance = request.POST.get('date_naissance')
        lieu_naissance = request.POST.get('lieu_naissance')
        filiere_id = request.POST.get('filiere')  # On récupère l'ID de la filière
        contact = request.POST.get('contact')
        theme_memoire = request.POST.get('theme_memoire')
        support_pdf = request.FILES.get('support_pdf')

        filiere_instance = Filiere.objects.get(id=filiere_id)

        # 1. Créer le User
        user = User.objects.create_user(
            username=f"{nom.lower()}{prenom.lower()}",  # Username = nom+prenom
            email=email,
            password='Gesms.Edu@',  # mot de passe temporaire
            last_name=nom,
            first_name=prenom,  # Prénom
            contact=contact,
        )

        # 2. Créer l'étudiant lié avec l'instance de la filière
        Etudiant.objects.create(
            user=user,
            nom=nom,
            prenom=prenom,
            email=email,
            date_naissance=date_naissance,
            lieu_naissance=lieu_naissance,
            filiere=filiere_instance,  # Assigner l'instance de la filière
            contact=contact,
            theme_memoire=theme_memoire,
            support_pdf=support_pdf,
        )
        etudiant = Etudiant.objects.get(email=email)
        return redirect('creer_paiement',etudiant_id=etudiant.id)  # Page de succès après l'enregistrement
    else:
        form = EtudiantForm()
    return render(request, 'users/add-student.html', {'form': form})



# -----------------------------------------------------------
# -----------------------------------------------------------
# vue des paiements


def creer_paiement(request, etudiant_id):
    etudiant = get_object_or_404(Etudiant, id=etudiant_id)
    
    if request.method == 'POST':
        form = PaiementForm(request.POST)
        if form.is_valid():
            paiement = form.save(commit=False)
            paiement.etudiant = etudiant
            paiement.save()
            return redirect('recu_paiement', paiement_id=paiement.id)
    else:
        form = PaiementForm()

    context = {
        'form': form,
        'etudiant': etudiant,
    }
    return render(request, 'users/add-fees.html', context)



def recu_paiement(request, paiement_id):
    paiement = get_object_or_404(Paiement, id=paiement_id)
    etudiant = paiement.etudiant  # si Paiement a un ForeignKey vers Etudiant
    return render(request, 'users/fees-receipt.html', {'paiement': paiement, 'etudiant': etudiant})


def recu_etudiant(request, paiement_id):
    paiement = get_object_or_404(Paiement, id=paiement_id)
    context = {
        'paiement': paiement,
        'etudiant': paiement.etudiant
    }
    return render(request, 'users/fees-receipt.html', context)


def list_paiement(request):
    query = request.GET.get('q', '').strip()
    etudiants = Etudiant.objects.all()
    paiements = Paiement.objects.select_related('etudiant')  # Optimisation pour les jointures

    if query:
        # Recherche sur les champs des étudiants et des paiements
        paiements = paiements.filter(
            Q(frais_impression__icontains=query) |
            Q(montant__icontains=query) |
            Q(date_paiement__icontains=query) |
            Q(source__icontains=query) |
            Q(etudiant__nom__icontains=query) |
            Q(etudiant__prenom__icontains=query) |
            Q(reference__icontains=query)
        )

    return render(request, 'users/fees-collection.html', {
        'etudiants': etudiants,
        'paiements': paiements,
        'query': query  # Important pour réafficher le terme recherché
    })


def modifier_paiement(request, paiement_id):
    paiement = get_object_or_404(Paiement, id=paiement_id)
    
    if request.method == 'POST':
        form = PaiementForm(request.POST, instance=paiement)
        if form.is_valid():
            form.save()
            messages.success(request, "Le paiement a été mis à jour avec succès.")
            return redirect('list_paiement')  # Redirigez vers la vue appropriée
    else:
        # Formatage initial de la date pour l'affichage
        initial_data = {
            'date_paiement': paiement.date_paiement.strftime('%Y-%m-%d') 
            if paiement.date_paiement else None
        }
        form = PaiementForm(instance=paiement, initial=initial_data)
    
    context = {
        'form': form,
        'paiement': paiement,
        'etudiant': paiement.etudiant
    }
    return render(request, 'users/add-fees.html', context)


def supprimer_paiement(request, paiement_id):
    paiement = get_object_or_404(Paiement, id=paiement_id)
    etudiant_id = paiement.etudiant.id  # On garde l'ID pour la redirection
    
    if request.method == 'POST':
        reference = paiement.reference
        paiement.delete()
        messages.success(request, f"Le paiement {reference} a été supprimé avec succès.")
        return redirect('list_paiement')
    
    # Si méthode GET, afficher la confirmation
    return render(request, 'users/confirmer_suppression_paiement.html', {
        'paiement': paiement
    })


def detail_paiement(request, paiement_id):
    paiement = get_object_or_404(
        Paiement.objects.select_related('etudiant'), 
        id=paiement_id
    )
    
    context = {
        'paiement': paiement,
        'etudiant': paiement.etudiant,
        'dossier': getattr(paiement.etudiant, 'dossier', None)  # Si relation existe
    }
    return render(request, 'users/detail_paiement.html', context)



# -----------------------------------------------------------
# -----------------------------------------------------------
# Vue des etudiants
def list_etudiant(request):
    query = request.GET.get('q', '').strip()
    etudiants = Etudiant.objects.all()
    paiements = Paiement.objects.all()
    dossiers = Dossier.objects.all()

    if query:
        # Liste des champs textuels valides pour la recherche
        text_fields = [
            'nom', 'prenom', 'filiere',
            'contact', 'email', 'matricule'
        ]
        
        # Vérification des champs existants et compatibles
        valid_fields = []
        for field in text_fields:
            try:
                if hasattr(Etudiant, field):
                    field_type = Etudiant._meta.get_field(field)
                    if field_type.get_internal_type() in ['CharField', 'TextField']:
                        valid_fields.append(field)
            except:
                continue
        
        # Construction des conditions de recherche
        search_conditions = Q()
        for field in valid_fields:
            search_conditions |= Q(**{f'{field}__icontains': query})
        
        etudiants = etudiants.filter(search_conditions)

    return render(request, 'users/all-students.html', {
        'etudiants': etudiants,
        'paiements': paiements,
        'dossiers': dossiers,
        'query': query
    })


def detail_etudiant(request, pk):
    etudiant = get_object_or_404(Etudiant, pk=pk)
    return render(request, 'users/oeil1.html', {'etudiant': etudiant})


def modifier_etudiant(request, pk):
    etudiant = get_object_or_404(Etudiant, pk=pk)
    
    # Formatage initial de la date pour le formulaire
    initial_data = {
        'date_naissance': etudiant.date_naissance.strftime('%Y-%m-%d') if etudiant.date_naissance else None
    }
    
    if request.method == 'POST':
        form = EtudiantForm(request.POST, instance=etudiant)
        if form.is_valid():
            form.save()
            messages.success(request, "Les informations de l'étudiant ont été mises à jour avec succès.")
            return redirect('list_etudiant')
    else:
        form = EtudiantForm(instance=etudiant, initial=initial_data)
    
    return render(request, 'users/form-wizard.html', {
        'form': form,
        'etudiant': etudiant
    })


def supprimer_etudiant(request, pk):
    etudiant = get_object_or_404(Etudiant, pk=pk)
    if request.method == 'POST':
        etudiant.delete()
        return redirect('list_etudiant')
    return render(request, 'users/confirm_delete.html', {'etudiant': etudiant})



def list_memoire(request):
    query = request.GET.get('q', '')
    
    # Initialisation des querysets de base
    etudiants = Etudiant.objects.all()
    paiements = Paiement.objects.all()
    dossiers = Dossier.objects.all()
    
    # Filtrage si une recherche est effectuée
    if query:
        etudiants = etudiants.filter(
            Q(nom__icontains=query) | 
            Q(prenom__icontains=query) |
            Q(filiere__nom__icontains=query)
        )
        
        # Optionnel : filtrer aussi les paiements et dossiers des étudiants trouvés
        paiements = paiements.filter(etudiant__in=etudiants)
        dossiers = dossiers.filter(etudiant__in=etudiants)

    context = {
        'etudiants': etudiants,
        'paiements': paiements,
        'dossiers': dossiers,
        'search_query': query,
    }
    return render(request, 'users/all-staff.html', context)




def list_recu(request):   
    query = request.GET.get('q', '').strip()
    paiements = Paiement.objects.select_related('etudiant').prefetch_related('etudiant__dossiers')

    if query:
        paiements = paiements.filter(
            Q(frais_impression__icontains=query) |
            Q(montant__icontains=query) |
            Q(date_paiement__icontains=query) |
            Q(source__icontains=query) |
            Q(etudiant__nom__icontains=query) |
            Q(etudiant__prenom__icontains=query) |
            Q(reference__icontains=query)
        )

    return render(request, 'users/all-library.html', {
        'paiements': paiements,
        'query': query
    })



def statistique(request):
    # 1. Récupération des données de base
    etudiants = Etudiant.objects.all()
    paiements = Paiement.objects.all()
    dossiers = Dossier.objects.all()
    today = date.today()
    
    # 2. Calcul des agrégations en une seule requête pour optimisation
    aggregates = paiements.aggregate(
        total_montant=Sum('montant'),
        total_frais_annexe=Sum('frais_annexe'),
        total_commission=Sum('commission')
    )

    # 3. Préparation des statistiques de base
    stats = {
        'nb_etudiants': etudiants.count(),
        'nb_dossiers': dossiers.count(),
        'nb_paiements': paiements.count(),
        'sm_paiements': aggregates['total_montant'] or 0,
        'dossiers_aujourdhui': dossiers.filter(date_creation__date=today).count(),
        # Modification ici: statut est un BooleanField, pas besoin de Q avec iexact
        'nb_dossiers_statut': dossiers.filter(statut=True).count(),  # Dossiers traités
        'nb_dossiers_livrer': dossiers.filter(livrer=True).count(),  # Dossiers livrés
        'nb_service_annexe': paiements.filter(service_annexe=True).count(),
        'total_frais_annexes': aggregates['total_frais_annexe'] or 0,
        'total_commission': aggregates['total_commission'] or 0,
        'gain_total': (aggregates['total_frais_annexe'] or 0) + (aggregates['total_commission'] or 0),
        'derniers_paiements': paiements.order_by('-date_paiement')[:5],
    }

    # 4. Préparation des éléments pour le tableau de stats
    stats_items = [
        {
            'icon': 'fa-calendar-day',
            'color': '#f39c12',
            'label': 'Dossiers du jour',
            'value': stats['dossiers_aujourdhui'],
            'badge_class': 'warning',
            'badge_text': 'Pending',
            'progress_class': 'warning',
            'progress': min(70, stats['dossiers_aujourdhui'] * 10),
        },
        {
            'icon': 'fa-tasks',
            'color': '#28a745',
            'label': 'Dossiers traités',
            'value': stats['nb_dossiers_statut'],
            'badge_class': 'primary',
            'badge_text': 'DONE',
            'progress_class': 'primary',
            'progress': min(70, stats['nb_dossiers_statut'] * 10),
        },
        {
            'icon': 'fa-truck',
            'color': '#17a2b8',
            'label': 'Mémoires livrés',
            'value': stats['nb_dossiers_livrer'],
            'badge_class': 'primary',
            'badge_text': 'DONE',
            'progress_class': 'primary',
            'progress': min(70, stats['nb_dossiers_livrer'] * 10),
        },
        {
            'icon': 'fa-plus-circle',
            'color': '#6f42c1',
            'label': 'Services annexes',
            'value': stats['nb_service_annexe'],
            'badge_class': 'info',
            'badge_text': 'EXTRA',
            'progress_class': 'info',
            'progress': min(70, stats['nb_service_annexe'] * 10),
        },
        {
            'icon': 'fa-money-bill-wave',
            'color': '#20c997',
            'label': 'Gain Total',
            'value': f"{stats['gain_total']:,.2f} FCFA",  # Formatage avec 2 décimales
            'badge_class': 'success',
            'badge_text': 'PROFIT',
            'progress_class': 'success',
            'progress': 100,
        },
    ]

    # 5. Préparation du contexte
    context = {
        **stats,
        'stats_items': stats_items,
        'etudiants': etudiants,
        'paiements': paiements,
        'dossiers': dossiers,
    }

    return render(request, 'users/index-3.html', context)



#Vue pour afficher les revenues
def revenus(request):
    # 1. Récupération des données de base
    etudiants = Etudiant.objects.all()
    paiements = Paiement.objects.all()
    dossiers = Dossier.objects.all()
    today = date.today()
    
    # 2. Calcul des agrégations en une seule requête pour optimisation
    aggregates = paiements.aggregate(
        total_montant=Sum('montant'),
        total_frais_annexe=Sum('frais_annexe'),
        total_commission=Sum('commission')
    )

    # 3. Préparation des statistiques de base
    stats = {
        'nb_etudiants': etudiants.count(),
        'nb_dossiers': dossiers.count(),
        'nb_paiements': paiements.count(),
        'sm_paiements': aggregates['total_montant'] or 0,
        'dossiers_aujourdhui': dossiers.filter(date_creation__date=today).count(),
        # Modification ici: statut est un BooleanField, pas besoin de Q avec iexact
        'nb_dossiers_statut': dossiers.filter(statut=True).count(),  # Dossiers traités
        'nb_dossiers_livrer': dossiers.filter(livrer=True).count(),  # Dossiers livrés
        'nb_service_annexe': paiements.filter(service_annexe=True).count(),
        'total_frais_annexes': aggregates['total_frais_annexe'] or 0,
        'total_commission': aggregates['total_commission'] or 0,
        'gain_total': (aggregates['total_frais_annexe'] or 0) + (aggregates['total_commission'] or 0),
        'derniers_paiements': paiements.order_by('-date_paiement')[:5],
    }

    # 4. Préparation des éléments pour le tableau de stats
    stats_items = [
        {
            'icon': 'fa-calendar-day',
            'color': '#f39c12',
            'label': 'Dossiers du jour',
            'value': stats['dossiers_aujourdhui'],
            'badge_class': 'warning',
            'badge_text': 'Pending',
            'progress_class': 'warning',
            'progress': min(70, stats['dossiers_aujourdhui'] * 10),
        },
        {
            'icon': 'fa-tasks',
            'color': '#28a745',
            'label': 'Dossiers traités',
            'value': stats['nb_dossiers_statut'],
            'badge_class': 'primary',
            'badge_text': 'DONE',
            'progress_class': 'primary',
            'progress': min(70, stats['nb_dossiers_statut'] * 10),
        },
        {
            'icon': 'fa-truck',
            'color': '#17a2b8',
            'label': 'Mémoires livrés',
            'value': stats['nb_dossiers_livrer'],
            'badge_class': 'primary',
            'badge_text': 'DONE',
            'progress_class': 'primary',
            'progress': min(70, stats['nb_dossiers_livrer'] * 10),
        },
        {
            'icon': 'fa-plus-circle',
            'color': '#6f42c1',
            'label': 'Services annexes',
            'value': stats['nb_service_annexe'],
            'badge_class': 'info',
            'badge_text': 'EXTRA',
            'progress_class': 'info',
            'progress': min(70, stats['nb_service_annexe'] * 10),
        },
        {
            'icon': 'fa-money-bill-wave',
            'color': '#20c997',
            'label': 'Gain Total',
            'value': f"{stats['gain_total']:,.2f} FCFA",  # Formatage avec 2 décimales
            'badge_class': 'success',
            'badge_text': 'PROFIT',
            'progress_class': 'success',
            'progress': 100,
        },
    ]

    # 5. Préparation du contexte
    context = {
        **stats,
        'stats_items': stats_items,
        'etudiants': etudiants,
        'paiements': paiements,
        'dossiers': dossiers,
    }

    return render(request, 'users/index-2.html', context)