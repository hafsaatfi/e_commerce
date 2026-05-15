from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CategorieForm, ProduitForm
from .models import Categorie, Produit
from users.permissions import admin_required


def liste_produits(request):
    query = request.GET.get('q', '').strip()
    categorie_id = request.GET.get('categorie', '').strip()

    produits = Produit.objects.select_related('categorie').all()
    categories = Categorie.objects.all().order_by('nom')

    if query:
        produits = produits.filter(
            Q(nom__icontains=query) | Q(description__icontains=query)
        )

    if categorie_id.isdigit():
        produits = produits.filter(categorie_id=int(categorie_id))

    context = {
        'produits': produits.order_by('nom'),
        'categories': categories,
        'query': query,
        'categorie_id': categorie_id,
    }
    return render(request, 'produit/produits.html', context)


from django.db.models import Avg

def detail_produit(request, produit_id):
    produit = get_object_or_404(Produit.objects.select_related('categorie'), id=produit_id)
    # compute average note and check if current user already reviewed
    from avis.models import Avis
    reviews = Avis.objects.filter(produit=produit)
    avg = reviews.aggregate(avg_note=Avg('note'))['avg_note'] or None
    user_review = None
    if request.user.is_authenticated:
        user_review = reviews.filter(utilisateur=request.user).first()

    context = {
        'produit': produit,
        'average': round(avg,2) if avg else None,
        'user_review': user_review,
    }
    return render(request, 'produit/produit_detail.html', context)


@admin_required
def creer_produit(request):
    form = ProduitForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Produit cree avec succes.')
        return redirect('produit:liste_produits')

    return render(request, 'produit/produit_form.html', {
        'form': form,
        'titre': 'Ajouter un produit',
        'texte_bouton': 'Creer',
    })


@admin_required
def modifier_produit(request, produit_id):
    produit = get_object_or_404(Produit, id=produit_id)
    form = ProduitForm(request.POST or None, request.FILES or None, instance=produit)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Produit modifie avec succes.')
        return redirect('produit:detail_produit', produit_id=produit.id)

    return render(request, 'produit/produit_form.html', {
        'form': form,
        'titre': 'Modifier un produit',
        'texte_bouton': 'Mettre a jour',
    })


@admin_required
def supprimer_produit(request, produit_id):
    produit = get_object_or_404(Produit, id=produit_id)

    if request.method == 'POST':
        produit.delete()
        messages.success(request, 'Produit supprime avec succes.')
        return redirect('produit:liste_produits')

    return render(request, 'produit/produit_confirm_delete.html', {'produit': produit})


def liste_categories(request):
    categories = Categorie.objects.all().order_by('nom')
    return render(request, 'produit/categories.html', {'categories': categories})


def detail_categorie(request, categorie_id):
    categorie = get_object_or_404(Categorie, id=categorie_id)
    produits = Produit.objects.filter(categorie=categorie).order_by('nom')
    context = {
        'categorie': categorie,
        'produits': produits,
    }
    return render(request, 'produit/categorie_detail.html', context)


@admin_required
@admin_required
def creer_categorie(request):
    form = CategorieForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Categorie creee avec succes.')
        return redirect('produit:liste_categories')

    return render(request, 'produit/categorie_form.html', {
        'form': form,
        'titre': 'Ajouter une categorie',
        'texte_bouton': 'Creer',
    })


@admin_required
def modifier_categorie(request, categorie_id):
    categorie = get_object_or_404(Categorie, id=categorie_id)
    form = CategorieForm(request.POST or None, instance=categorie)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Categorie modifiee avec succes.')
        return redirect('produit:detail_categorie', categorie_id=categorie.id)

    return render(request, 'produit/categorie_form.html', {
        'form': form,
        'titre': 'Modifier une categorie',
        'texte_bouton': 'Mettre a jour',
    })


@admin_required
def supprimer_categorie(request, categorie_id):
    categorie = get_object_or_404(Categorie, id=categorie_id)

    if request.method == 'POST':
        if Produit.objects.filter(categorie=categorie).exists():
            messages.error(
                request,
                'Impossible de supprimer cette categorie: des produits y sont encore associes.',
            )
            return redirect('produit:detail_categorie', categorie_id=categorie.id)

        categorie.delete()
        messages.success(request, 'Categorie supprimee avec succes.')
        return redirect('produit:liste_categories')

    return render(request, 'produit/categorie_confirm_delete.html', {'categorie': categorie})