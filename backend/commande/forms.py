from django import forms
import re

from .models import DELIVERY_METHOD_CHOICES, SKIN_TYPE_CHOICES


class CommandeCheckoutForm(forms.Form):
    full_name = forms.CharField(
        label='Nom complet',
        max_length=120,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Votre nom complet'})
    )
    phone = forms.CharField(
        label='Téléphone',
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+212 6xx xx xx xx'})
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'votre@email.com'})
    )
    address = forms.CharField(
        label='Adresse',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Rue et numéro'})
    )
    ville = forms.CharField(
        label='Ville',
        max_length=120,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Casablanca'})
    )
    quartier = forms.CharField(
        label='Quartier',
        max_length=120,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Maarif'})
    )
    skin_type = forms.ChoiceField(
        label='Type de peau',
        choices=SKIN_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    delivery_method = forms.ChoiceField(
        label='Options de livraison',
        choices=DELIVERY_METHOD_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    skin_problem = forms.CharField(
        label='Problème de peau (optionnel)',
        required=False,
        max_length=160,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Acné, taches, rougeurs...'})
    )
    note = forms.CharField(
        label='Message',
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Ajoutez un message ou une instruction'})
    )

    def clean_full_name(self):
        value = self.cleaned_data['full_name'].strip()
        if len(value) < 3:
            raise forms.ValidationError('Le nom doit contenir au moins 3 caractères.')
        if not re.fullmatch(r"[A-Za-zÀ-ÿ'\-\s]+", value):
            raise forms.ValidationError('Le nom contient des caractères non valides.')
        return re.sub(r'\s+', ' ', value)

    def clean_phone(self):
        raw_value = self.cleaned_data['phone']
        value = re.sub(r'\s+', '', raw_value)
        if value.startswith('+212'):
            digits = '+212' + re.sub(r'\D', '', value[4:])
            if len(digits) != 13:
                raise forms.ValidationError('Numéro marocain invalide (format +212).')
            return digits

        digits = re.sub(r'\D', '', value)
        if digits.startswith('0') and len(digits) == 10:
            return digits

        raise forms.ValidationError('Numéro invalide. Exemple: +2126XXXXXXXX ou 06XXXXXXXX.')

    def clean_address(self):
        value = self.cleaned_data['address'].strip()
        if len(value) < 6:
            raise forms.ValidationError('Adresse trop courte.')
        return value

    def clean_ville(self):
        value = self.cleaned_data['ville'].strip()
        if len(value) < 2:
            raise forms.ValidationError('Ville invalide.')
        return re.sub(r'\s+', ' ', value)

    def clean_quartier(self):
        value = self.cleaned_data['quartier'].strip()
        if len(value) < 2:
            raise forms.ValidationError('Quartier invalide.')
        return re.sub(r'\s+', ' ', value)

    def clean_skin_problem(self):
        return self.cleaned_data['skin_problem'].strip()

    def clean_note(self):
        return self.cleaned_data['note'].strip()