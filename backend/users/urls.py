from django.urls import path
from .views import login_view, register_view, user_home, recommendations_page

urlpatterns = [
    path('home/', user_home, name='user-home'),
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('recommandations/', recommendations_page, name='user-recommendations'),
]