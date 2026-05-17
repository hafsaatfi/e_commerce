from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404, render
from panier.models import Panier, ArticlePanier
from .forms import CommandeCheckoutForm
from .models import Commande, ArticleCommande
from users.recommendations import record_user_activity


@login_required
def commande_index(request):
    panier = get_object_or_404(Panier, utilisateur=request.user)
    articles = ArticlePanier.objects.filter(panier=panier)
    if not articles:
        return redirect('/panier/')

    if request.method == 'POST':
        form = CommandeCheckoutForm(request.POST)
        if form.is_valid():
            # 1. calcul total
            total = sum(item.produit.prix * item.quantite for item in articles)

            # 2. créer commande
            commande = Commande.objects.create(
                utilisateur=request.user,
                montant_total=total,
                statut="confirmer",
                full_name=form.cleaned_data.get('full_name'),
                phone=form.cleaned_data.get('phone'),
                email=form.cleaned_data.get('email'),
                address=form.cleaned_data.get('address'),
                ville=form.cleaned_data.get('ville'),
                quartier=form.cleaned_data.get('quartier'),
                skin_type=form.cleaned_data.get('skin_type'),
                delivery_method=form.cleaned_data.get('delivery_method'),
                skin_problem=form.cleaned_data.get('skin_problem'),
                note=form.cleaned_data.get('note'),
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
            # 5. stocker l'id de la commande pour la confirmation
            request.session['last_commande_id'] = commande.id
            return redirect('/commande/confirmation/')
    else:
        form = CommandeCheckoutForm()
    return render(request, 'commande/passer_commande.html', {'form': form, 'articles': articles})

## La logique de validation de commande est maintenant dans commande_index
from django.http import HttpResponse

@login_required
def confirmation(request):
    commande_id = request.session.get('last_commande_id')
    commande = None
    articles = []
    if commande_id:
        try:
            commande = Commande.objects.get(id=commande_id, utilisateur=request.user)
            articles = ArticleCommande.objects.filter(commande=commande)
        except Commande.DoesNotExist:
            commande = None
    return render(request, 'commande/confirmation.html', {
        'commande': commande,
        'articles': articles,
    })

@login_required
def historique(request):
    commandes = Commande.objects.filter(utilisateur=request.user).order_by('-date_creation')
    return render(request, 'commande/historique.html', {'commandes': commandes})