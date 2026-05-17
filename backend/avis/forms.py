from django import forms
from .models import Avis

class AvisForm(forms.ModelForm):
    NOTE_CHOICES = [
        (1, 'Médiocre'),
        (2, 'Passable'),
        (3, 'Moyen'),
        (4, 'Bon'),
        (5, 'Excellent'),
    ]
    note = forms.TypedChoiceField(choices=NOTE_CHOICES, coerce=int, widget=forms.RadioSelect)

    class Meta:
        model = Avis
        fields = ['note', 'commentaire']
        widgets = {
            'commentaire': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Partagez votre expérience avec ce produit...'}),
        }

    def clean_note(self):
        n = self.cleaned_data.get('note')
        if n is None or not (1 <= n <= 5):
            raise forms.ValidationError('La note doit être entre 1 et 5.')
        return n
