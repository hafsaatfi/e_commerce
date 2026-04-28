from django.urls import path

from .views import dashboard, entity_create, entity_delete, entity_detail, entity_list, entity_update

app_name = 'gestion'

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('<str:entity>/<int:object_id>/', entity_detail, name='entity_detail'),
    path('<str:entity>/<int:object_id>/modifier/', entity_update, name='entity_update'),
    path('<str:entity>/<int:object_id>/supprimer/', entity_delete, name='entity_delete'),
    path('<str:entity>/ajouter/', entity_create, name='entity_create'),
    path('<str:entity>/', entity_list, name='entity_list'),
]
