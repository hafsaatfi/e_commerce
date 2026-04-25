from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Produit, Categorie
from django.utils.html import format_html

class CategorieAdmin(admin.ModelAdmin):
	list_display = ('nom', 'description', 'image_tag')
	readonly_fields = ('image_tag',)
	fields = ('nom', 'description', 'image', 'image_tag')

	def image_tag(self, obj):
		if obj.image:
			return format_html('<img src="{}" style="max-height: 80px; max-width: 120px; border-radius: 8px;" />', obj.image.url)
		return ""
	image_tag.short_description = 'Aperçu'



class ProduitAdmin(admin.ModelAdmin):
    list_display = ('nom', 'categorie', 'prix', 'stock', 'is_favori', 'image_tag')
    readonly_fields = ('image_tag',)
    fields = ('nom', 'categorie', 'prix', 'stock', 'description', 'image', 'image_tag', 'is_favori')

    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 60px; max-width: 90px; border-radius: 8px;" />', obj.image.url)
        return ""
    image_tag.short_description = 'Image principale'

    class Media:
        css = {
            'all': ('produit/admin_feminine.css',)
        }

admin.site.register(Produit, ProduitAdmin)
admin.site.register(Categorie, CategorieAdmin)