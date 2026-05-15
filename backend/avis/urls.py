from django.urls import path
from . import views

app_name = 'avis'

urlpatterns = [
    path('', views.index, name='avis-index'),
    path('product/<int:produit_id>/', views.product_reviews, name='avis-product'),
    path('product/<int:produit_id>/add/', views.add_or_edit_review, name='avis-add'),
    path('edit/<int:avis_id>/delete/', views.delete_review, name='avis-delete'),
]