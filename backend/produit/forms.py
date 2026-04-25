from django import forms

from .models import Categorie, Produit


class BootstrapModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, forms.Select):
                css_class = 'form-select'
            else:
                css_class = 'form-control'
            widget.attrs['class'] = css_class


class ProduitForm(BootstrapModelForm):
    class Meta:
        model = Produit
        fields = ['nom', 'categorie', 'prix', 'stock', 'description', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }


class CategorieForm(BootstrapModelForm):
    class Meta:
        model = Categorie
        fields = ['nom', 'description', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }
