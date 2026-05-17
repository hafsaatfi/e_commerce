from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404, render
from panier.models import Panier, ArticlePanier
from .forms import CommandeCheckoutForm
from .models import Commande, ArticleCommande
from users.recommendations import record_user_activity


@login_required
def commande_index(request):
    form = CommandeCheckoutForm(request.POST or None)
    return render(request, 'commande/passer_commande.html', {'form': form})

@login_required
def passer_commande(request):
    panier = get_object_or_404(Panier, utilisateur=request.user)
    articles = ArticlePanier.objects.filter(panier=panier)

    if not articles:
        return redirect('/panier/')

    # 1. calcul total
    total = sum(item.produit.prix * item.quantite for item in articles)

    # 2. créer commande
    commande = Commande.objects.create(
        utilisateur=request.user,
        montant_total=total,
        statut="confirmer"
    )

    # 3. copier articles panier → commande
    for item in articles:
        ArticleCommande.objects.create(
            commande=commande,
            produit=item.produit,
            quantite=item.quantite,
            prix=item.produit.prix
        )

        # (optionnel) réduire stock
        item.produit.stock -= item.quantite
        item.produit.save()

        record_user_activity(
            request.user,
            action='purchase',
            produit=item.produit,
            categorie=item.produit.categorie,
            metadata={'quantite': item.quantite, 'commande_id': commande.id},
        )

    # 4. vider panier
    articles.delete()

    return redirect('/commande/confirmation/')
from django.http import HttpResponse

@login_required
def confirmation(request):
    return HttpResponse("Commande confirmée ✔")