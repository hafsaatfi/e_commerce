from django.shortcuts import get_object_or_404, redirect, render
from produit.models import Produit
from .models import Panier, ArticlePanier
from django.contrib.auth.decorators import login_required

@login_required
def ajouter_au_panier(request, produit_id):
    produit = get_object_or_404(Produit, id=produit_id)

    quantite = int(request.POST.get('quantite', 1))

    panier, created = Panier.objects.get_or_create(utilisateur=request.user)

    article, created = ArticlePanier.objects.get_or_create(
        panier=panier,
        produit=produit
    )

    # IMPORTANT : remplacer au lieu d’additionner
    article.quantite = quantite
    article.save()

    return redirect('panier:panier')
@login_required
def voir_panier(request):
    panier, created = Panier.objects.get_or_create(utilisateur=request.user)
    articles = ArticlePanier.objects.filter(panier=panier)
    total = sum(item.produit.prix * item.quantite for item in articles)

    return render(request, 'panier.html', {
        'articles': articles,
        'total': total
    })

@login_required
def modifier_quantite(request, article_id):
    article = get_object_or_404(ArticlePanier, id=article_id)
    if request.method == 'POST':
        try:
            quantite = int(request.POST.get('quantite', 1))
            if quantite > 0:
                article.quantite = quantite
                article.save()
            else:
                article.delete()
        except (ValueError, TypeError):
            pass
    return redirect('panier:panier')

@login_required
def supprimer_article(request, article_id):
    article = get_object_or_404(ArticlePanier, id=article_id)
    article.delete()
    return redirect('panier:panier')