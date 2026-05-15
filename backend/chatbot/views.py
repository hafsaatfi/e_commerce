from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Q
import unicodedata

from chatbot.models import Log_Chatbot
from produit.models import Produit


def _normalize_text(text):
    """Remove accents from text for keyword matching"""
    nfd = unicodedata.normalize('NFD', text)
    return ''.join(char for char in nfd if unicodedata.category(char) != 'Mn')


class ChatbotIntent:
    """Détecte l'intention de l'utilisateur et extrait le contexte"""
    
    SKIN_TYPES = {
        'acne': ['acne', 'acné', 'bouton', 'boutons', 'imperfection', 'imperfections', 'comédone', 'point noir'],
        'oily': ['grasse', 'brillance', 'brillant', 'sébum', 'sebum', 'matifier'],
        'dry': ['sèche', 'seche', 'tiraillement', 'déshydrat', 'deshydrat', 'peau sèche'],
        'sensitive': ['sensible', 'sensibilité', 'rougeurs', 'rouge', 'irritation', 'irrité', 'réactif'],
        'mature': ['rides', 'ride', 'vieillissement', 'ridules', 'anti-age', 'anti age', 'fermeté'],
        'combination': ['mixte', 'combinaison', 'T-zone', 'zone T', 'grasse et sèche'],
    }
    
    CONCERN_KEYWORDS = {
        'nettoyant': ['nettoyant', 'cleanser', 'gommage', 'nettoyage'],
        'serum': ['sérum', 'serum'],
        'hydratant': ['hydratant', 'hydratante', 'crème', 'moisturizer'],
        'mask': ['masque', 'mask'],
        'sunscreen': ['solaire', 'spf', 'sun', 'protection', 'écran'],
        'eyes': ['yeux', 'contour', 'poches', 'cernes'],
        'routine': ['routine', 'régime', 'soin', 'soins', 'step by step'],
    }
    
    ORDER_KEYWORDS = ['commande', 'command', 'livraison', 'delivery', 'suivi', 'tracking', 'où', 'où est', 'arrive quand', 'reçu']
    PRICE_KEYWORDS = ['prix', 'coût', 'tarif', 'gratuit', 'cher', 'réduc', 'promo', 'discount']
    PRODUCT_KEYWORDS = ['produit', 'produits', 'quel', 'lequel', 'meilleur', 'recommand', 'propose', 'suggère']
    
    @classmethod
    def detect_intent(cls, message):
        """
        Détecte l'intention principale du message.
        Retourne: (intent_type, detected_skin_type, keywords)
        """
        text = message.lower().strip()
        normalized_text = _normalize_text(text)  # Remove accents for matching
        
        # Normaliser aussi les mots-clés pour une comparaison correcte
        normalized_order_keywords = [_normalize_text(kw) for kw in cls.ORDER_KEYWORDS]
        normalized_price_keywords = [_normalize_text(kw) for kw in cls.PRICE_KEYWORDS]
        normalized_product_keywords = [_normalize_text(kw) for kw in cls.PRODUCT_KEYWORDS]
        
        # Détection des mots-clés d'ordre/livraison
        if any(kw in normalized_text for kw in normalized_order_keywords):
            return ('order', None, [])
        
        # Détection des questions de prix
        if any(kw in normalized_text for kw in normalized_price_keywords):
            return ('price', None, [])
        
        # Détection du type de peau
        detected_skin = None
        for skin_type, keywords in cls.SKIN_TYPES.items():
            # Normaliser les mots-clés du dictionnaire aussi
            normalized_keywords = [_normalize_text(kw) for kw in keywords]
            if any(kw in normalized_text for kw in normalized_keywords):
                detected_skin = skin_type
                break
        
        # Détection des préoccupations/produits
        detected_concerns = []
        for concern, keywords in cls.CONCERN_KEYWORDS.items():
            # Normaliser les mots-clés du dictionnaire aussi
            normalized_keywords = [_normalize_text(kw) for kw in keywords]
            if any(kw in normalized_text for kw in normalized_keywords):
                detected_concerns.append(concern)
        
        # Déterminer l'intention principale
        if detected_skin and (detected_concerns or any(kw in normalized_text for kw in normalized_product_keywords)):
            return ('skin_diagnosis', detected_skin, detected_concerns)
        elif detected_concerns or any(kw in normalized_text for kw in normalized_product_keywords):
            return ('product_search', None, detected_concerns)
        elif detected_skin:
            return ('skin_type', detected_skin, [])
        else:
            return ('general', None, [])


def _get_product_recommendations(intent, skin_type=None, concerns=None):
    """
    Retourne les produits pertinents selon l'intention et le contexte.
    """
    queryset = Produit.objects.all()
    
    if skin_type:
        # Mapper les types de peau aux catégories de produits
        skin_category_map = {
            'acne': 'Acné & Imperfections',
            'oily': 'Peaux Grasses',
            'dry': 'Peaux Sèches',
            'sensitive': 'Peaux Sensibles',
            'mature': 'Anti-Age',
            'combination': 'Peaux Mixtes',
        }
        category = skin_category_map.get(skin_type)
        if category:
            queryset = queryset.filter(categorie__nom=category) | queryset.filter(is_favori=True)
    
    if concerns:
        # Filtrer par type de produit basé sur les préoccupations
        q_filter = Q()
        for concern in concerns:
            q_filter |= Q(nom__icontains=concern) | Q(description__icontains=concern)
        queryset = queryset.filter(q_filter)
    
    # Si aucun résultat spécifique, retourner les favoris
    if not queryset.exists():
        queryset = Produit.objects.filter(is_favori=True)
    
    return queryset.order_by('-is_favori', 'nom')[:3]


def _build_chatbot_reply(message, user=None):
    """
    Génère une réponse intelligente en analysant le message utilisateur.
    Retourne: (response_text, products_list, profile_label)
    """
    text = message.lower().strip()
    
    # Si message vide
    if not text:
        return (
            "👋 Salut ! Dis-moi ton type de peau (acné, grasse, sèche, sensible...), "
            "tes préoccupations, ou le produit que tu cherches. Je vais te proposer une routine adaptée ! 🧴",
            [],
            None
        )
    
    # Détecter l'intention
    intent, skin_type, concerns = ChatbotIntent.detect_intent(message)
    
    # ========== INTENT: ORDER/DELIVERY ==========
    if intent == 'order':
        if user and user.is_authenticated:
            from commande.models import Commande
            try:
                last_order = Commande.objects.filter(utilisateur=user).latest('date_creation')
                response = (
                    f"📦 Voici ta dernière commande :\n"
                    f"Statut : {last_order.statut.upper()}\n"
                    f"Date : {last_order.date_creation.strftime('%d/%m/%Y')}\n\n"
                    f"Tu peux suivre ton colis sur la page de suivi. Si tu as besoin d'aide, n'hésite pas ! 💌"
                )
                return (response, [], None)
            except Commande.DoesNotExist:
                return (
                    "📦 Tu n'as pas encore de commande. Découvre nos produits pour créer ta première routine ! 🛍️",
                    _get_product_recommendations('general'),
                    None
                )
        else:
            return (
                "📦 Pour suivre ta commande, connecte-toi à ton compte. C'est plus facile ! 🔐",
                _get_product_recommendations('general'),
                None
            )
    
    # ========== INTENT: PRICE QUESTIONS ==========
    if intent == 'price':
        products = _get_product_recommendations('general')
        return (
            "💰 Nos produits sont entre 150 et 500 DH selon le type et la marque. "
            "Regarde nos meilleures ventes - elles offrent vraiment le meilleur rapport qualité-prix ! ✨",
            products,
            None
        )
    
    # ========== INTENT: SKIN DIAGNOSIS (Type de peau + Préoccupations) ==========
    if intent == 'skin_diagnosis':
        skin_labels = {
            'acne': '🔴 Peau à Tendance Acnéique',
            'oily': '✨ Peau Grasse',
            'dry': '💧 Peau Sèche',
            'sensitive': '🌸 Peau Sensible',
            'mature': '👑 Peau Mature',
            'combination': '🎨 Peau Mixte',
        }
        
        label = skin_labels.get(skin_type, skin_type.title())
        
        recommendations = {
            'acne': (
                "Pour une peau à tendance acnéique, j'te recommande :\n"
                "• Un nettoyant doux (sans agresser)\n"
                "• Un soin ciblé (BHA ou acide salicylique)\n"
                "• Une hydratation légère (non comédogène)\n"
                "• Une protection solaire (SPF 30+)\n\n"
                "Surtout : sois patient(e), les bons soins prennent 6-8 semaines pour montrer des résultats ! 💪"
            ),
            'oily': (
                "Pour une peau grasse, voici ma routine :\n"
                "• Nettoyant purifiant (nettoie en profondeur)\n"
                "• Tonique matifiant (réduit la brillance)\n"
                "• Sérums légers (évite les huiles)\n"
                "• Crème légère (matifiante, non grasse)\n"
                "• Masques purifiant 1-2x/semaine\n\n"
                "La clé : hydrater même une peau grasse pour qu'elle ne surproduise ! 🎯"
            ),
            'dry': (
                "Pour une peau sèche, mise sur :\n"
                "• Nettoyant doux & riche (hydratant)\n"
                "• Toner nourrissant\n"
                "• Sérums hydratants (acide hyaluronique)\n"
                "• Crème riche (nourrissante & occlusive)\n"
                "• Huiles ou masques nourrissants\n\n"
                "Pro tip : applique les soins sur peau humide pour vraiment bien hydrater ! 💦"
            ),
            'sensitive': (
                "Pour une peau sensible, sois doux :\n"
                "• Nettoyant hypoallergénique (très doux)\n"
                "• Tonique apaisant (sans alcool)\n"
                "• Sérums calmants (camomille, centella)\n"
                "• Crème apaisante (sans paraben, sans parfum)\n"
                "• Moins = mieux (pas trop de produits)\n\n"
                "La règle d'or : teste chaque produit avant d'en mettre partout ! 🧪"
            ),
            'mature': (
                "Pour une peau mature, anti-âge c'est :\n"
                "• Nettoyant doux (respecte l'élasticité)\n"
                "• Sérums actifs (rétinol, vitamine C)\n"
                "• Contour des yeux (rides & cernes)\n"
                "• Crème riche (fermeté & nutrition)\n"
                "• Masques anti-âge 1x/semaine\n\n"
                "Bonus : le solaire est ESSENTIEL pour prévenir le vieillissement ! ☀️"
            ),
            'combination': (
                "Pour une peau mixte, la flexibilité c'est clé :\n"
                "• Nettoyant doux (nettoie sans dessécher)\n"
                "• 2 crèmes différentes (légère pour T-zone, riche pour joues)\n"
                "• Sérums polyvalents (hydratants + légers)\n"
                "• Masques adaptés (purifiant ET hydratant)\n\n"
                "Stratégie : traite chaque zone selon ses besoins ! 🎭"
            ),
        }
        
        response = recommendations.get(skin_type, "Je peux t'aider à créer une routine adaptée !")
        products = _get_product_recommendations(intent, skin_type, concerns)
        
        return (response, products, label)
    
    # ========== INTENT: SKIN TYPE ONLY ==========
    if intent == 'skin_type':
        skin_labels = {
            'acne': '🔴 Peau à Tendance Acnéique',
            'oily': '✨ Peau Grasse',
            'dry': '💧 Peau Sèche',
            'sensitive': '🌸 Peau Sensible',
            'mature': '👑 Peau Mature',
            'combination': '🎨 Peau Mixte',
        }
        
        label = skin_labels.get(skin_type, skin_type.title())
        
        responses = {
            'acne': "Peau acnéique détectée ! On va créer une routine ciblée pour toi. Ces produits sont parfaits pour réduire les boutons et les imperfections. 💪",
            'oily': "Peau grasse ! Pas de souci, j'ai les bons produits matifiants pour toi. Les textures légères vont te changer la vie ! 🌟",
            'dry': "Peau sèche ? On va la réhydrater de fou ! Ces soins vont lui redonner de l'éclat et de la souplesse. 💧",
            'sensitive': "Peau sensible ! Pas d'agresseurs ici, que des soins doux et apaisants. Ton visage va enfin respirer ! 🌸",
            'mature': "Peau mature ! Anti-âge sérieux, avec des actifs qui fonctionnent vraiment. Prépare-toi à un teint plus ferme ! 👑",
            'combination': "Peau mixte ! Je vais pas te forcer à choisir entre une T-zone grasse et des joues sèches. Ces produits gèrent les deux ! 🎭",
        }
        
        response = responses.get(skin_type, "Parfait, j'ai trouvé les produits qui te correspondent !")
        products = _get_product_recommendations(intent, skin_type)
        
        return (response, products, label)
    
    # ========== INTENT: PRODUCT SEARCH ==========
    if intent == 'product_search':
        concern_names = ", ".join(concerns) if concerns else "tous types"
        response = (
            f"🔍 Recherche de {concern_names}...\n\n"
            f"Voici les produits les plus adaptés pour toi ! Ils ont tous de super avis. "
            f"N'hésite pas à regarder les détails pour trouver ton coup de cœur ! 💝"
        )
        products = _get_product_recommendations(intent, concerns=concerns)
        
        return (response, products, None)
    
    # ========== INTENT: GENERAL (Par défaut) ==========
    default_responses = [
        "Hmm, j'ai pas bien compris. Parle-moi de ton type de peau et je vais t'aider ! 😊",
        "C'est une bonne question ! Dis-moi un peu plus sur ta peau (grasse, sèche, sensible...) et je te proposerai une routine. 🧴",
        "Je suis là pour t'aider avec tes soins ! Quel est ton type de peau ? (acné, peau grasse, sèche, sensible...)",
        "Parle-moi de ta peau ! C'est comment ? Grasse ? Sèche ? Sensible ? Acnéique ? Je vais proposer le parfait ! 🎯",
    ]
    
    import random
    response = random.choice(default_responses)
    products = _get_product_recommendations('general')
    
    return (response, products, None)


def home(request):
    """Chatbot skincare intelligent - accessible publiquement"""
    user_message = ''
    bot_message = ''
    suggestions = []
    profile_label = None

    if request.method == 'POST':
        user_message = request.POST.get('message', '').strip()
        
        # Appeler la nouvelle fonction intelligente avec l'utilisateur
        bot_message, suggested_products, profile_label = _build_chatbot_reply(
            user_message,
            user=request.user
        )
        
        # Formater les suggestions de produits
        suggestions = [
            {
                'nom': product.nom,
                'prix': product.prix,
                'description': product.description[:50] + '...' if len(product.description) > 50 else product.description,
                'url': f'/produits/{product.id}/',
            }
            for product in suggested_products
        ]

        # Enregistrer le log seulement si l'utilisateur est connecté
        if user_message and request.user.is_authenticated:
            Log_Chatbot.objects.create(
                utilisateur=request.user,
                question=user_message,
                reponse=bot_message,
            )

        # Return an HTML fragment for the floating widget to parse
        bot_html = (
            '<div class="msg-row bot">\n'
            '  <div class="msg-stack">\n'
            '    <div class="msg-label">Assistant</div>\n'
            f'    <div class="bubble bot">{bot_message}</div>\n'
            '  </div>\n'
            '</div>'
        )

        return HttpResponse(bot_html, content_type='text/html')

    chat_history = []
    if user_message or bot_message:
        chat_history.append({
            'user': user_message,
            'bot': bot_message,
            'suggestions': suggestions,
            'profile_label': profile_label,
        })

    return render(
        request,
        'chatbot/chatbot.html',
        {
            'chat_history': chat_history,
            'user_message': user_message,
        },
    )