from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login


from produit.models import Categorie, Produit
from django.db import models
from avis.models import Avis


def home(request):
    if request.user.is_authenticated:
        return redirect('user-home')
    return redirect('login')

def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff or getattr(request.user, 'role', None) == 'admin':
            return redirect('gestion:dashboard')
        return redirect('user-home')

    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            if user.is_staff or getattr(user, 'role', None) == 'admin':
                return redirect('gestion:dashboard')
            return redirect('user-home')
        else:
            return render(request, 'login.html', {'error': 'Login invalide', 'hide_nav': True})

    return render(request, 'login.html', {'hide_nav': True})
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
        return redirect('login')
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

    return render(request, 'home.html', {
        'produits': produits_recommandes,
        'categories': categories,
        'featured_product': featured_product,
        'produits_favoris': produits_favoris,
        'hide_nav': True,
        'full_layout': True,
    })