from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import timedelta

from django.db.models import Count, Sum
from django.utils import timezone

from avis.models import Avis
from commande.models import ArticleCommande
from ia_recommandation.models import IA_Recommandation
from produit.models import Produit
from users.models import UserActivity

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
except Exception:  # pragma: no cover - fallback when sklearn cannot be imported
    TfidfVectorizer = None
    cosine_similarity = None


@dataclass
class RecommendationResult:
    produit: Produit
    score: float
    raison: str


def record_user_activity(user, action, produit=None, categorie=None, metadata=None):
    if not user or not getattr(user, 'is_authenticated', False):
        return None

    return UserActivity.objects.create(
        utilisateur=user,
        action=action,
        produit=produit,
        categorie=categorie,
        metadata=metadata or {},
    )


def _product_text(product):
    category_name = product.categorie.nom if product.categorie_id and product.categorie else ''
    return ' '.join(part for part in [product.nom, category_name, product.description] if part)


def _recent_viewed_products(user):
    return list(
        UserActivity.objects.filter(
            utilisateur=user,
            action__in=[UserActivity.ACTION_VIEW_PRODUCT, UserActivity.ACTION_ADD_TO_CART],
        )
        .exclude(produit__isnull=True)
        .select_related('produit', 'produit__categorie')
        .order_by('-created_at')[:30]
    )


def _user_interaction_weights():
    weights = defaultdict(lambda: defaultdict(float))

    for item in ArticleCommande.objects.select_related('commande', 'produit'):
        status = (item.commande.statut or '').lower()
        if status in {'rejeter', 'rejette', 'rejetee'}:
            continue

        base_weight = 4.0 if status in {'confirmer', 'confirmee', 'confirmed'} else 2.5
        weights[item.commande.utilisateur_id][item.produit_id] += base_weight * max(item.quantite, 1)

    for review in Avis.objects.select_related('utilisateur', 'produit'):
        if review.note >= 5:
            review_weight = 4.0
        elif review.note == 4:
            review_weight = 3.0
        elif review.note == 3:
            review_weight = 1.0
        else:
            review_weight = 0.25
        weights[review.utilisateur_id][review.produit_id] += review_weight

    for activity in UserActivity.objects.filter(
        action__in=[UserActivity.ACTION_VIEW_PRODUCT, UserActivity.ACTION_ADD_TO_CART],
        produit__isnull=False,
    ):
        activity_weight = 1.0 if activity.action == UserActivity.ACTION_VIEW_PRODUCT else 1.8
        weights[activity.utilisateur_id][activity.produit_id] += activity_weight

    return weights


def _collaborative_scores(user, candidate_products):
    if not candidate_products:
        return {}

    user_weights = _user_interaction_weights()
    target_weights = user_weights.get(user.id, {})

    if not user_weights:
        return {}

    product_ids = sorted({product.id for product in candidate_products} | {pid for mapping in user_weights.values() for pid in mapping})
    user_ids = list(user_weights.keys())

    if not product_ids or user.id not in user_weights:
        return {}

    try:
        from scipy.sparse import csr_matrix
    except Exception:
        return {}

    user_index = {user_id: idx for idx, user_id in enumerate(user_ids)}
    product_index = {product_id: idx for idx, product_id in enumerate(product_ids)}

    rows = []
    cols = []
    data = []
    for user_id, mapping in user_weights.items():
        row_index = user_index[user_id]
        for product_id, weight in mapping.items():
            rows.append(row_index)
            cols.append(product_index[product_id])
            data.append(weight)

    matrix = csr_matrix((data, (rows, cols)), shape=(len(user_ids), len(product_ids)))
    target_index = user_index[user.id]
    similarities = cosine_similarity(matrix[target_index], matrix).flatten()

    scores = defaultdict(float)
    for row_index, similarity in enumerate(similarities):
        if row_index == target_index or similarity <= 0:
            continue

        other_user_id = user_ids[row_index]
        for product_id, weight in user_weights[other_user_id].items():
            if product_id in target_weights:
                continue
            scores[product_id] += similarity * weight

    return scores


def _content_scores(user, candidate_products):
    if not candidate_products or TfidfVectorizer is None or cosine_similarity is None:
        return {}

    recent_views = _recent_viewed_products(user)
    profile_tokens = []

    for activity in recent_views:
        if activity.produit:
            profile_tokens.append(_product_text(activity.produit))
            if activity.produit.categorie_id:
                profile_tokens.append(activity.produit.categorie.nom)

    if not profile_tokens:
        for review in Avis.objects.filter(utilisateur=user, note__gte=4).select_related('produit__categorie')[:10]:
            if review.produit:
                profile_tokens.append(_product_text(review.produit))
                profile_tokens.append(review.produit.categorie.nom)

    if not profile_tokens:
        return {}

    corpus = [' '.join(profile_tokens)] + [_product_text(product) for product in candidate_products]
    matrix = TfidfVectorizer().fit_transform(corpus)
    similarities = cosine_similarity(matrix[0:1], matrix[1:]).flatten()
    return {product.id: float(similarity) for product, similarity in zip(candidate_products, similarities)}


def _trend_scores(candidate_products):
    if not candidate_products:
        return {}

    recent_window = timezone.now() - timedelta(days=90)
    purchase_trends = (
        ArticleCommande.objects.filter(commande__date_creation__gte=recent_window)
        .values('produit_id')
        .annotate(total=Sum('quantite'))
    )
    review_trends = (
        Avis.objects.filter(date_creation__gte=recent_window, note__gte=4)
        .values('produit_id')
        .annotate(total=Count('id'))
    )

    purchase_map = {row['produit_id']: float(row['total'] or 0) for row in purchase_trends}
    review_map = {row['produit_id']: float(row['total'] or 0) for row in review_trends}

    scores = {}
    for product in candidate_products:
        scores[product.id] = (purchase_map.get(product.id, 0.0) * 0.7) + (review_map.get(product.id, 0.0) * 0.3)
    return scores


def _category_affinity(user):
    category_scores = defaultdict(float)

    for review in Avis.objects.filter(utilisateur=user).select_related('produit__categorie'):
        if review.produit and review.produit.categorie_id:
            category_scores[review.produit.categorie_id] += 1.5 if review.note >= 4 else 0.4

    for activity in UserActivity.objects.filter(utilisateur=user, categorie__isnull=False):
        if activity.action == UserActivity.ACTION_VIEW_CATEGORY:
            category_scores[activity.categorie_id] += 1.0
        elif activity.action == UserActivity.ACTION_VIEW_PRODUCT and activity.produit and activity.produit.categorie_id:
            category_scores[activity.produit.categorie_id] += 0.75

    for item in ArticleCommande.objects.filter(commande__utilisateur=user).select_related('produit__categorie'):
        if item.produit and item.produit.categorie_id:
            category_scores[item.produit.categorie_id] += 2.0

    return category_scores


def _preferred_product_ids(user):
    purchased_products = set(
        ArticleCommande.objects.filter(commande__utilisateur=user)
        .exclude(commande__statut__in=['rejeter', 'rejette', 'rejetee'])
        .values_list('produit_id', flat=True)
    )
    reviewed_products = set(Avis.objects.filter(utilisateur=user).values_list('produit_id', flat=True))
    return purchased_products | reviewed_products


def build_home_recommendations(user, limit=6):
    products = list(Produit.objects.select_related('categorie').all())
    if not products:
        return []

    excluded_ids = _preferred_product_ids(user)
    candidate_products = [product for product in products if product.id not in excluded_ids]
    if not candidate_products:
        candidate_products = products

    collaborative = _collaborative_scores(user, candidate_products)
    content = _content_scores(user, candidate_products)
    trends = _trend_scores(candidate_products)
    affinities = _category_affinity(user)

    recent_views = _recent_viewed_products(user)
    recent_view_counts = defaultdict(int)
    for activity in recent_views:
        if activity.produit_id:
            recent_view_counts[activity.produit_id] += 1

    results = []
    for product in candidate_products:
        collab_score = collaborative.get(product.id, 0.0)
        content_score = content.get(product.id, 0.0)
        trend_score = trends.get(product.id, 0.0)
        affinity_score = affinities.get(product.categorie_id, 0.0)
        browse_score = 1.2 * recent_view_counts.get(product.id, 0)

        score = (collab_score * 0.4) + (content_score * 0.35) + (trend_score * 0.15) + (affinity_score * 0.25) + browse_score
        if product.stock <= 0:
            score *= 0.4

        if recent_view_counts.get(product.id):
            reason = 'Vu récemment pendant ta navigation'
        elif collab_score >= max(content_score, trend_score, 0.01):
            reason = 'Choisi par des utilisateurs au profil similaire'
        elif content_score >= trend_score:
            reason = f'Similaire à tes intérêts pour {product.categorie.nom}'
        elif trend_score > 0:
            reason = 'Tendance du moment'
        else:
            reason = f'Aligné avec ton profil {product.categorie.nom}'

        results.append(RecommendationResult(produit=product, score=score, raison=reason))

    results.sort(key=lambda item: (item.score, item.produit.id), reverse=True)
    top_results = results[:limit]

    if top_results:
        IA_Recommandation.objects.update_or_create(
            utilisateur=user,
            defaults={'list_produit_ids': ','.join(str(item.produit.id) for item in top_results)},
        )

    return top_results
