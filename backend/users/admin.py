from django.contrib import admin

# Register your models here.
from .models import UserActivity


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
	list_display = ('utilisateur', 'action', 'produit', 'categorie', 'created_at')
	list_filter = ('action', 'created_at')
	search_fields = ('utilisateur__username', 'produit__nom', 'categorie__nom')
