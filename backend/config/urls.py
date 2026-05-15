"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.views.generic import RedirectView
from django.urls import include, path

from panier.views import ajouter_au_panier
from commande.views import confirmation

urlpatterns = [
    path('', RedirectView.as_view(url='/users/login/', permanent=False), name='root-login'),
    path('admin/', admin.site.urls),
    path('logout/', LogoutView.as_view(), name='logout'),

    path('commane/', RedirectView.as_view(url='/commande/', permanent=False), name='commane-alias'),

    path('users/', include('users.urls')),
    path('gestion/', include('gestion.urls')),
    path('produits/', include('produit.urls')),
    path('panier/', include(('panier.urls', 'panier'), namespace='panier')),
    path('commande/', include('commande.urls')),
    path('avis/', include('avis.urls')),
    path('chatbot/', include('chatbot.urls')),
    path('ajouter/<int:produit_id>/', ajouter_au_panier),
    path('confirmation/', confirmation),
]
from django.conf import settings
from django.conf.urls.static import static


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
