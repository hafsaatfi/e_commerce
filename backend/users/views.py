from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login

def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('/')
        else:
            return render(request, 'login.html', {'error': 'Login invalide'})

    return render(request, 'login.html')
from .models import Utilisateur
from django.contrib.auth import login

def register_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = Utilisateur.objects.create_user(
            username=username,
            password=password
        )

        login(request, user)
        return redirect('/')

    return render(request, 'register.html')

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from produit.models import Produit

@login_required
def user_home(request):
    produits = Produit.objects.all()[:6]  # derniers produits

    return render(request, 'users/home.html', {
        'produits': produits
    })