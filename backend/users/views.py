import logging
from django.contrib.auth import authenticate, login
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import render, redirect
from django.utils.http import url_has_allowed_host_and_scheme


from produit.models import Categorie, Produit
from django.db import models
from avis.models import Avis


def home(request):
    if request.user.is_authenticated:
        return redirect('user-home')
    return redirect_to_login(request.get_full_path())

def login_view(request):
    next_url = request.POST.get('next') or request.GET.get('next')

    logger = logging.getLogger(__name__)

    if request.user.is_authenticated:
        if next_url and url_has_allowed_host_and_scheme(
            next_url,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        ):
            return redirect(next_url)
        if request.user.is_staff or getattr(request.user, 'role', None) == 'admin':
            return redirect('gestion:dashboard')
        return redirect('user-home')

    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        # Debug logging: record attempt (do not log password in production)
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            found = User.objects.filter(username=username).exists()
        except Exception:
            found = False
        logger.info(f"Login attempt for username='{username}' found_in_db={found}")
        print(f"[DEBUG] Login attempt for username='{username}' found_in_db={found}")

        user = authenticate(request, username=username, password=password)
        logger.info(f"Authentication result for username='{username}': {'OK' if user else 'FAIL'}")
        print(f"[DEBUG] Authentication result for username='{username}': {'OK' if user else 'FAIL'}")

        if user:
            login(request, user)
            if next_url and url_has_allowed_host_and_scheme(
                next_url,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure(),
            ):
                return redirect(next_url)
            if user.is_staff or getattr(user, 'role', None) == 'admin':
                return redirect('gestion:dashboard')
            return redirect('user-home')
        else:
            return render(request, 'login.html', {'error': 'Login invalide', 'hide_nav': True, 'next': next_url})

    return render(request, 'login.html', {'hide_nav': True, 'next': next_url})
from .models import Utilisateur

def register_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff or getattr(request.user, 'role', None) == 'admin':
            return redirect('gestion:dashboard')
        return redirect('user-home')

    if request.method == "POST":
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if not username or not password:
            return render(request, 'register.html', {
                'error': "Nom d'utilisateur et mot de passe sont obligatoires.",
                'hide_nav': True,
            })

        if password != confirm_password:
            return render(request, 'register.html', {
                'error': 'Les mots de passe ne correspondent pas.',
                'hide_nav': True,
            })

        if Utilisateur.objects.filter(username=username).exists():
            return render(request, 'register.html', {
                'error': "Ce nom d'utilisateur existe deja.",
                'hide_nav': True,
            })

        user = Utilisateur.objects.create_user(
            username=username,
            password=password,
            role='user',
            is_staff=False,
        )
        login(request, user)
        return redirect('user-home')

    return render(request, 'register.html', {'hide_nav': True})

def user_home(request):
    if not request.user.is_authenticated:
        return redirect_to_login(request.get_full_path())
    if request.user.is_staff or getattr(request.user, 'role', None) == 'admin':
        return redirect('gestion:dashboard')

    # Produits favoris (Curated Favourites)
    produits_favoris = list(
        Produit.objects.filter(is_favori=True).select_related('categorie')
        .order_by('-id')[:6]
    )

    # Produits recommandés (non favoris, max 3)
    produits_recommandes = list(
        Produit.objects.filter(is_favori=False).select_related('categorie')
        .order_by('-id')[:3]
    )
    categories = Categorie.objects.order_by('nom')[:6]
    featured_product = produits_recommandes[0] if produits_recommandes else None

    # Nombre d'articles dans le panier
    from panier.models import Panier, ArticlePanier
    panier_count = 0
    if request.user.is_authenticated:
        panier = Panier.objects.filter(utilisateur=request.user).first()
        if panier:
            panier_count = ArticlePanier.objects.filter(panier=panier).aggregate(models.Sum('quantite'))['quantite__sum'] or 0

    return render(request, 'home.html', {
        'produits': produits_recommandes,
        'categories': categories,
        'featured_product': featured_product,
        'produits_favoris': produits_favoris,
        'hide_nav': True,
        'full_layout': True,
        'panier_count': panier_count,
    })