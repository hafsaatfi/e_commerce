from django import forms
from .models import Avis

class AvisForm(forms.ModelForm):
    class Meta:
        model = Avis
        fields = ['note', 'commentaire']
        widgets = {
            'note': forms.NumberInput(attrs={'min': 1, 'max': 5, 'class': 'form-control form-control-sm'}),
            'commentaire': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

    def clean_note(self):
        n = self.cleaned_data.get('note')
        if n is None or not (1 <= n <= 5):
            raise forms.ValidationError('La note doit être entre 1 et 5.')
        return n
