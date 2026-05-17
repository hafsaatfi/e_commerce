from django import forms

from .models import Categorie, Produit


class ProduitForm(forms.ModelForm):
    class Meta:
        model = Produit
        fields = ['nom', 'categorie', 'prix', 'stock', 'description', 'image', 'is_favori', 'score_etoiles']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'score_etoiles': forms.RadioSelect(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.RadioSelect):
                field.widget.attrs['class'] = 'space-y-2'
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs['class'] = 'w-full rounded-xl border border-outline-variant/40 bg-surface-container-low px-3 py-2 text-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20'
            elif isinstance(field.widget, forms.FileInput):
                field.widget.attrs['class'] = 'w-full rounded-xl border border-outline-variant/40 bg-surface-container-low px-3 py-2 text-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20'
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs['class'] = 'w-full rounded-xl border border-outline-variant/40 bg-surface-container-low px-3 py-2 text-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20'
            elif isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'w-4 h-4 rounded border-outline-variant/40'
            else:
                field.widget.attrs['class'] = 'w-full rounded-xl border border-outline-variant/40 bg-surface-container-low px-3 py-2 text-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20'


class CategorieForm(forms.ModelForm):
    class Meta:
        model = Categorie
        fields = ['nom', 'description', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs['class'] = 'w-full rounded-xl border border-outline-variant/40 bg-surface-container-low px-3 py-2 text-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20'
            elif isinstance(field.widget, forms.FileInput):
                field.widget.attrs['class'] = 'w-full rounded-xl border border-outline-variant/40 bg-surface-container-low px-3 py-2 text-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20'
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs['class'] = 'w-full rounded-xl border border-outline-variant/40 bg-surface-container-low px-3 py-2 text-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20'
            else:
                field.widget.attrs['class'] = 'w-full rounded-xl border border-outline-variant/40 bg-surface-container-low px-3 py-2 text-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20'
