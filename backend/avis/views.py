from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, Count

from produit.models import Produit
from .models import Avis
from .forms import AvisForm


def product_reviews(request, produit_id):
    produit = get_object_or_404(Produit, pk=produit_id)
    reviews = Avis.objects.filter(produit=produit).select_related('utilisateur')
    avg = reviews.aggregate(avg_note=Avg('note'))['avg_note'] or 0
    user_review = None
    if request.user.is_authenticated:
        user_review = reviews.filter(utilisateur=request.user).first()

    form = AvisForm(instance=user_review)

    return render(request, 'avis/product_reviews.html', {
        'produit': produit,
        'reviews': reviews,
        'average': round(avg, 2) if avg else None,
        'form': form,
        'user_review': user_review,
    })


@login_required
def add_or_edit_review(request, produit_id):
    produit = get_object_or_404(Produit, pk=produit_id)
    review, created = Avis.objects.get_or_create(utilisateur=request.user, produit=produit, defaults={'note': 5, 'commentaire': ''})

    if request.method == 'POST':
        form = AvisForm(request.POST, instance=review)
        if form.is_valid():
            form.instance.utilisateur = request.user
            form.instance.produit = produit
            form.save()
            messages.success(request, 'Merci — ton avis a été enregistré.')
            return redirect('avis:avis-product', produit_id=produit.id)
        else:
            messages.error(request, 'Corrige les erreurs dans le formulaire.')
    else:
        form = AvisForm(instance=review)

    return render(request, 'avis/review_form.html', {'form': form, 'produit': produit, 'review': review})


@login_required
def delete_review(request, avis_id):
    avis = get_object_or_404(Avis, pk=avis_id, utilisateur=request.user)
    produit_id = avis.produit.id
    if request.method == 'POST':
        avis.delete()
        messages.success(request, 'Ton avis a été supprimé.')
        return redirect('avis:avis-product', produit_id=produit_id)

    return render(request, 'avis/confirm_delete.html', {'avis': avis})


def index(request):
    """Display all products with their average ratings."""
    products = Produit.objects.annotate(
        avg_note=Avg('avis__note'),
        review_count=Count('avis')
    ).order_by('-avg_note', 'nom')
    
    # Debug info
    total_products = Produit.objects.count()
    total_reviews = Avis.objects.count()
    products_with_reviews = products.filter(review_count__gt=0).count()
    
    return render(request, 'avis/index.html', {
        'products': products,
        'total_products': total_products,
        'total_reviews': total_reviews,
        'products_with_reviews': products_with_reviews,
        'debug': request.GET.get('debug') == '1',
    })