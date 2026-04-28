import re
import random
import unicodedata

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from produit.models import Produit

from .models import Log_Chatbot


SKIN_TYPE_KEYWORDS = {
    'grasse': [
        'peau grasse', 'grasse', 'huileuse', 'huileuse et brillante', 'brillante', 'brillance',
        'excès de sebum', 'excès sebum', 'sebum', 'seborrheique', 'boutons', 'acne', 'imperfections',
        'points noirs', 'zone t grasse', 'tendance grasse'
    ],
    'seche': [
        'peau seche', 'seche', 'tres seche', 'déshydratée', 'deshydratee', 'dessechee', 'tiraille',
        'tiraillee', 'rugueuse', 'peau qui tire', 'manque d hydratation', 'manque dhydratation'
    ],
    'mixte': [
        'peau mixte', 'mixte', 'combinaison', 'zone t', 't-zone', 'front gras', 'nez gras',
        'menton gras', 'joues seches', 'zone t grasse'
    ],
    'sensible': [
        'peau sensible', 'sensible', 'rougeur', 'rougeurs', 'irritation', 'reactive', 'reactive',
        'allergique', 'picotement', 'reaction', 'qui chauffe'
    ],
    'normale': [
        'peau normale', 'normale', 'equilibree', 'equilibre', 'bien equilibree', 'sans probleme'
    ],
}

CONCERN_KEYWORDS = {
    'acne': [
        'acne', 'boutons', 'imperfections', 'points noirs', 'comedons', 'comedones', 'microkystes',
        'poussée de boutons', 'poussee de boutons'
    ],
    'taches': [
        'taches', 'tache', 'pigmentation', 'hyperpigmentation', 'cicatrices', 'marques',
        'taches brunes', 'taches pigmentaires', 'uniformiser le teint'
    ],
    'hydratation': [
        'hydratation', 'hydrate', 'hydratant', 'secheresse', 'tiraillement', 'peau qui tire',
        'deshydratation', 'deshydratation', 'manque dhydratation'
    ],
    'sensibilite': [
        'sensibilite', 'sensible', 'rougeur', 'rougeurs', 'irritation', 'picotement', 'chauffe',
        'reaction', 'reaction cutanee', 'cutanee'
    ],
    'antiage': [
        'anti age', 'anti-age', 'antiage', 'rides', 'rides fines', 'premieres rides', 'ridules',
        'rajeunir', 'fermete', 'perte de fermete'
    ],
}

INTENT_KEYWORDS = {
    'greeting': ['bonjour', 'bonsoir', 'salut', 'hello', 'salam', 'coucou', 'hey', 'yo'],
    'routine': ['routine', 'rituel', 'programme', 'soin du matin', 'soin du soir', 'matin', 'soir', 'etapes'],
    'product': [
        'produit', 'produits', 'recommande', 'recommander', 'recommandez', 'conseille', 'conseilles', 
        'conseiller', 'acheter', 'achat', 'achete', 'quelle marque', 'quel produit', 'lequel', 
        'exemples', 'exemple', 'suggestions', 'suggestion', 'marques', 'marque', 'listes', 'liste',
        'quels produits', 'quel est le', 'peux tu me proposer'
    ],
    'ingredient': ['ingredient', 'ingredients', 'composition', 'acide', 'niacinamide', 'retinol', 'vitamine c', 'bha', 'aha', 'actif', 'actifs'],
    'concern': ['acne', 'tache', 'taches', 'hydratation', 'sensibilite', 'anti age', 'anti-age', 'rides', 'peau'],
    'how_to': ['comment', 'quoi utiliser', 'que mettre', 'que choisir', 'quoi prendre', 'que me conseilles tu', 'explique', 'expliques'],
}

SKIN_ONLY_RESPONSES = {
    'grasse': [
        'Je détecte une peau grasse. On va viser des textures légères, un nettoyage doux et un soin sébo-régulateur.',
        'Peau grasse repérée. Le plus utile ici est de garder une routine simple, non occlusive et bien équilibrée.',
    ],
    'seche': [
        'Je détecte une peau sèche. Il faut privilégier l hydratation, les céramides et des textures nourrissantes.',
        'Peau sèche repérée. On va surtout renforcer la barrière cutanée avec des soins doux et relipidants.',
    ],
    'mixte': [
        'Je détecte une peau mixte. L idée est d équilibrer la zone T sans assécher les zones plus sèches.',
        'Peau mixte repérée. Il faut des soins modulables: légers sur la zone T, plus confortables sur les joues.',
    ],
    'sensible': [
        'Je détecte une peau sensible. On va éviter les actifs trop agressifs et favoriser des formules apaisantes.',
        'Peau sensible repérée. Le meilleur point de départ est une routine courte, douce et anti-irritation.',
    ],
    'normale': [
        'Je détecte une peau normale. L objectif est de maintenir l équilibre avec une routine simple et régulière.',
        'Peau normale repérée. On peut partir sur une routine légère, stable et facile à suivre.',
    ],
}

GENERAL_SKIN_GUIDANCE = {
    'grasse': 'Nettoyant doux, sérum niacinamide, hydratant gel et SPF non comédogène.',
    'seche': 'Nettoyant crème, sérum hydratant, crème riche et SPF confort.',
    'mixte': 'Nettoyant équilibrant, soin léger sur la zone T et hydratation ciblée.',
    'sensible': 'Formules sans parfum, actifs apaisants et barrière cutanée renforcée.',
    'normale': 'Routine simple: nettoyage, hydratation et protection solaire.',
}


def _normalize_text(value):
    text = unicodedata.normalize('NFKD', value or '').encode('ascii', 'ignore').decode('ascii').lower()
    text = text.replace('&', ' and ')
    text = re.sub(r"['’`´]", '', text)
    text = re.sub(r'[^a-z0-9]+', ' ', text)
    return re.sub(r'\s+', ' ', text).strip()


def _phrase_found(normalized_text, phrase):
    phrase = _normalize_text(phrase)
    if not phrase:
        return False
    return bool(re.search(rf'(?<!\w){re.escape(phrase)}(?!\w)', normalized_text))


def _has_any_keyword(normalized_text, keywords):
    return any(_phrase_found(normalized_text, keyword) for keyword in keywords)


def _pick_variant(options):
    return random.choice(options) if options else ''


def _detect_skin_type(message):
    normalized = _normalize_text(message)
    for skin_type, keywords in SKIN_TYPE_KEYWORDS.items():
        if _has_any_keyword(normalized, keywords):
            return skin_type
    return None


def _detect_concerns(message):
    normalized = _normalize_text(message)
    concerns = []
    for concern, keywords in CONCERN_KEYWORDS.items():
        if _has_any_keyword(normalized, keywords):
            concerns.append(concern)
    return concerns


def _detect_intent(message):
    normalized = _normalize_text(message)
    for intent, keywords in INTENT_KEYWORDS.items():
        if _has_any_keyword(normalized, keywords):
            return intent
    return 'general'


def _build_response(message):
    normalized = _normalize_text(message)
    skin_type = _detect_skin_type(message)
    concerns = _detect_concerns(message)
    intent = _detect_intent(message)

    # PRIORITIZE: If user explicitly asks for products, always show products
    if intent == 'product':
        if skin_type and concerns:
            response = _pick_variant([
                f'Excellente idée! Pour peau {skin_type} avec {", ".join(concerns)}, voici mes recommandations:',
                f'Pour peau {skin_type} et {", ".join(concerns)}, je te propose ces produits adaptés:',
                f'Voici les meilleurs produits pour peau {skin_type} et {", ".join(concerns)}:',
            ])
        elif skin_type:
            response = _pick_variant([
                f'Parfait! Pour peau {skin_type}, voici les produits les plus adaptés:',
                f'Voici les meilleurs soins pour peau {skin_type}:',
                f'Pour peau {skin_type}, je te conseille ces produits:',
            ])
        elif concerns:
            response = _pick_variant([
                f'Pour {", ".join(concerns)}, voici les meilleurs produits:',
                f'Voici des produits efficaces pour {", ".join(concerns)}:',
                f'Pour résoudre {", ".join(concerns)}, je recommande:',
            ])
        else:
            response = _pick_variant([
                'Je vais te proposer nos meilleurs produits skincare. Dis-moi ton type de peau pour affiner la sélection!',
                'Voici une sélection de produits de qualité. Si tu me donnes ton type de peau, je pourrai mieux les adapter.',
                'Découvre nos meilleures marques skincare. Décris ta peau pour que je te propose les plus appropriés.',
            ])
        return response, skin_type, concerns

    # PROFILE RESPONSES: When intent is NOT product
    if skin_type and not concerns:
        skin_prefix = _pick_variant(SKIN_ONLY_RESPONSES.get(skin_type, [
            f'Je détecte une peau {skin_type}.',
            f'Profil peau {skin_type} repéré.',
        ]))
        skin_guidance = GENERAL_SKIN_GUIDANCE.get(skin_type, 'On peut adapter une routine simple et ciblée.')

        if intent == 'routine':
            response = (
                f'{skin_prefix} Pour une routine adaptée: {skin_guidance} '
                'Si tu me donnes un souci précis, je peux te proposer une version matin et soir plus ciblée.'
            )
            return response, skin_type, concerns

        if intent in {'general', 'how_to', 'concern'}:
            response = (
                f'{skin_prefix} {skin_guidance} '
                'Ajoute ensuite un besoin précis comme l acné, les taches ou la sensibilité pour une réponse plus fine.'
            )
            return response, skin_type, concerns

    if intent == 'greeting':
        response = _pick_variant([
            'Bonjour. Dis-moi ton type de peau et ton souci principal, et je te propose une routine simple avec des produits adaptés.',
            'Salut. Donne-moi ton type de peau et le besoin principal, et je t aide à construire une routine efficace.',
            'Bonjour. Si tu me décris ta peau et ton problème principal, je peux te guider pas à pas.',
        ])
    elif intent == 'routine':
        response = _pick_variant([
            'Pour une routine efficace: nettoyant doux, soin ciblé, hydratant adapté et protection solaire le matin. Donne-moi ton type de peau pour la personnaliser.',
            'Une bonne base: nettoyage, actif ciblé, hydratation et SPF le matin. Je peux te faire une version plus précise selon ta peau.',
            'Je te conseille une routine courte et régulière: nettoyer, traiter, hydrater, protéger. Dis-moi ta peau pour l ajuster.',
        ])
    elif intent == 'ingredient':
        response = _pick_variant([
            'Pour les ingrédients, les plus utiles selon le besoin sont souvent: niacinamide pour le sébum et les pores, acide salicylique pour l acné, vitamine C pour les taches, et céramides pour réparer la barrière cutanée.',
            'Côté ingrédients, pense à la niacinamide pour équilibrer, au salicylique pour les boutons, à la vitamine C pour le teint, et aux céramides pour protéger.',
            'Selon le besoin, les actifs les plus utiles sont souvent niacinamide, acide salicylique, vitamine C et céramides.',
        ])
    elif skin_type and concerns:
        response = _pick_variant([
            f'Profil detecte: peau {skin_type}. Preoccupation principale: {", ".join(concerns)}. Je te conseille une routine douce, un soin ciblé et un SPF le matin.',
            f'Je lis peau {skin_type} avec {", ".join(concerns)}. On peut simplifier la routine et choisir des produits plus adaptés.',
        ])
    elif concerns:
        response = _pick_variant([
            f'Je vois surtout: {", ".join(concerns)}. Dis-moi aussi ton type de peau pour que je te propose les bons produits.',
            f'Le besoin principal semble être {", ".join(concerns)}. Avec ton type de peau, je pourrai préciser la routine.',
        ])
    else:
        response = _pick_variant([
            'Je peux t aider pour les routines, les types de peau, les imperfections, les taches, la sensibilité et les produits. Ecris par exemple: "peau grasse avec acne".',
            'Dis-moi simplement ton type de peau ou ton problème principal, et je te réponds avec une recommandation plus précise.',
            'Si tu veux, commence par une phrase courte comme: "peau sèche" ou "peau grasse avec boutons".',
        ])

    return response, skin_type, concerns


def _recommend_products(message, skin_type=None, concerns=None):
    normalized = _normalize_text(message)
    search_terms = []
    
    # Boost scoring when product intent is explicitly detected
    intent = _detect_intent(message)
    is_product_request = intent == 'product'

    if skin_type:
        search_terms.extend(SKIN_TYPE_KEYWORDS.get(skin_type, []))
    if concerns:
        for concern in concerns:
            search_terms.extend(CONCERN_KEYWORDS.get(concern, []))

    if not search_terms:
        search_terms = re.findall(r'[a-z0-9]+', normalized)

    products = []
    for produit in Produit.objects.select_related('categorie').all():
        haystack = _normalize_text(' '.join([
            produit.nom,
            produit.description or '',
            produit.categorie.nom if produit.categorie_id else '',
        ]))
        score = 0
        for term in search_terms:
            if not term:
                continue
            normalized_term = _normalize_text(term)
            if normalized_term and re.search(rf'(?<!\w){re.escape(normalized_term)}(?!\w)', haystack):
                score += 2 if len(normalized_term.split()) > 1 else 1
        if skin_type and skin_type in haystack:
            score += 1
        if score:
            products.append((score, produit))

    if not products:
        # When no products match filters, still return some products if product request
        if is_product_request:
            products = [(1, produit) for produit in Produit.objects.select_related('categorie').all()[:5]]
        else:
            products = [(0, produit) for produit in Produit.objects.select_related('categorie').all()[:3]]

    products.sort(key=lambda item: (-item[0], item[1].nom))

    return [
        {
            'nom': produit.nom,
            'prix': produit.prix,
            'description': produit.description[:120] if produit.description else '',
            'url': '/produits/',
        }
        for _, produit in products[:3]
    ]


def home(request):
    mode = 'bubble'  # Only bubble mode available
    chat_history = request.session.get('chat_history', [])
    user_message = ''
    bot_response = ''
    profile_label = None
    suggestions = []

    if request.method == 'POST':
        user_message = (request.POST.get('message') or '').strip()
        if user_message:
            bot_response, skin_type, concerns = _build_response(user_message)
            profile_label = skin_type.replace('_', ' ') if skin_type else None
            suggestions = _recommend_products(user_message, skin_type=skin_type, concerns=concerns)

            chat_history = (chat_history + [{
                'user': user_message,
                'bot': bot_response,
                'profile_label': profile_label,
                'suggestions': suggestions,
            }])[-8:]
            request.session['chat_history'] = chat_history

            if request.user.is_authenticated:
                try:
                    Log_Chatbot.objects.create(
                        utilisateur=request.user,
                        question=user_message,
                        reponse=bot_response,
                    )
                except Exception:
                    pass

    logs = []
    if request.user.is_authenticated:
        logs = list(
            Log_Chatbot.objects.filter(utilisateur=request.user)
            .order_by('-date_creation')[:5]
        )

    for log in logs:
        log.reponse = log.reponse[:120] + ('...' if len(log.reponse) > 120 else '')

    return render(request, 'chatbot/chatbot.html', {
        'mode': mode,
        'chat_history': chat_history,
        'user_message': user_message,
        'logs': logs,
        'bot_response': bot_response,
        'profile_label': profile_label,
        'suggestions': suggestions,
    })