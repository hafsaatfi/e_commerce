from django import forms
from django.contrib import messages
from django.forms import modelform_factory
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.db import models

from avis.models import Avis
from chatbot.models import Log_Chatbot
from commande.models import ArticleCommande, Commande
from ia_recommandation.models import IA_Recommandation
from panier.models import ArticlePanier, Panier
from produit.models import Categorie, Produit
from produit.forms import ProduitForm, CategorieForm
from users.models import Utilisateur
from users.permissions import admin_required

ENTITY_CONFIGS = {
    'produits': {'model': Produit, 'label': 'Produit', 'detail_label': 'Produit'},
    'categories': {'model': Categorie, 'label': 'Categorie', 'detail_label': 'Categorie'},
    'avis': {'model': Avis, 'label': 'Avis', 'detail_label': 'Avis'},
    'commandes': {'model': Commande, 'label': 'Commande', 'detail_label': 'Commande'},
    'articles-commandes': {'model': ArticleCommande, 'label': 'Article de commande', 'detail_label': 'Article de commande'},
    'paniers': {'model': Panier, 'label': 'Panier', 'detail_label': 'Panier'},
    'articles-paniers': {'model': ArticlePanier, 'label': 'Article de panier', 'detail_label': 'Article de panier'},
    'chatbot-logs': {'model': Log_Chatbot, 'label': 'Log chatbot', 'detail_label': 'Log chatbot'},
    'ia-recommandations': {'model': IA_Recommandation, 'label': 'Recommandation IA', 'detail_label': 'Recommandation IA'},
    'utilisateurs': {'model': Utilisateur, 'label': 'Utilisateur', 'detail_label': 'Utilisateur'},
}

EXCLUDED_LIST_FIELDS = {
    'password',
    'last_login',
    'groups',
    'user_permissions',
}

EXCLUDED_FORM_FIELDS = {
    'last_login',
    'date_joined',
    'groups',
    'user_permissions',
    'password',
}


def render_gestion(request, template_name, context):
    base_context = {
        'hide_nav': True,
        'full_layout': True,
    }
    base_context.update(context)
    return render(request, template_name, base_context)


class UserAdminForm(forms.ModelForm):
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput,
        help_text='Laisser vide pour conserver le mot de passe actuel.',
    )

    class Meta:
        model = Utilisateur
        fields = ['username', 'first_name', 'last_name', 'email', 'role', 'is_staff', 'is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs['class'] = 'w-full rounded-xl border border-outline-variant/40 bg-surface-container-low px-3 py-2 text-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20'
            else:
                field.widget.attrs['class'] = 'w-full rounded-xl border border-outline-variant/40 bg-surface-container-low px-3 py-2 text-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20'
        if self.instance.pk is None:
            self.fields['password'].required = True

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)
        if commit:
            user.save()
            self.save_m2m()
        return user


class CommandeAdminForm(forms.ModelForm):
    class Meta:
        model = Commande
        fields = ['utilisateur', 'montant_total', 'statut']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs['class'] = 'w-full rounded-xl border border-outline-variant/40 bg-surface-container-low px-3 py-2 text-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20'
            elif isinstance(field.widget, forms.FileInput):
                field.widget.attrs['class'] = 'w-full rounded-xl border border-outline-variant/40 bg-surface-container-low px-3 py-2 text-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20'
            else:
                field.widget.attrs['class'] = 'w-full rounded-xl border border-outline-variant/40 bg-surface-container-low px-3 py-2 text-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20'


def get_entity_config(entity):
    config = ENTITY_CONFIGS.get(entity)
    if not config:
        raise Http404('Entite introuvable')
    return config


def get_model_fields(model):
    fields = []
    for field in model._meta.concrete_fields:
        if field.name in EXCLUDED_LIST_FIELDS:
            continue
        fields.append(field)
    return fields


def format_value(value):
    if value is None:
        return '-'
    return str(value)


def build_form_class(model):
    if model is Utilisateur:
        return UserAdminForm
    if model is Commande:
        return CommandeAdminForm
    if model is Produit:
        return ProduitForm
    if model is Categorie:
        return CategorieForm

    form_fields = []
    widgets = {}
    for field in model._meta.concrete_fields:
        if field.auto_created or not field.editable or field.name in EXCLUDED_FORM_FIELDS:
            continue
        form_fields.append(field.name)
        if isinstance(field, models.TextField):
            widgets[field.name] = forms.Textarea(attrs={'rows': 4})

    form_class = modelform_factory(model, fields=form_fields, widgets=widgets)

    class BootstrapForm(form_class):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            for field in self.fields.values():
                if isinstance(field.widget, forms.Select):
                    field.widget.attrs['class'] = 'w-full rounded-xl border border-outline-variant/40 bg-surface-container-low px-3 py-2 text-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20'
                elif isinstance(field.widget, forms.FileInput):
                    field.widget.attrs['class'] = 'w-full rounded-xl border border-outline-variant/40 bg-surface-container-low px-3 py-2 text-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20'
                else:
                    field.widget.attrs['class'] = 'w-full rounded-xl border border-outline-variant/40 bg-surface-container-low px-3 py-2 text-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20'

    return BootstrapForm


@admin_required
def dashboard(request):
    entities = []
    entities_by_key = {}
    entity_counts = {}
    visible_entities = {
        'utilisateurs',
        'commandes',
        'articles-commandes',
        'produits',
        'categories',
        'paniers',
        'articles-paniers',
    }

    for entity, config in ENTITY_CONFIGS.items():
        model = config['model']
        count = model.objects.count()
        if entity in visible_entities:
            entity_item = {
                'entity': entity,
                'label': config['label'],
                'count': count,
            }
            entities.append(entity_item)
            entities_by_key[entity] = entity_item
        entity_counts[entity] = count

    primary_order = ['utilisateurs', 'commandes', 'produits', 'paniers']
    secondary_order = ['categories', 'articles-commandes', 'articles-paniers']

    primary_entities = [entities_by_key[key] for key in primary_order if key in entities_by_key]
    secondary_entities = [entities_by_key[key] for key in secondary_order if key in entities_by_key]

    return render_gestion(request, 'gestion/dashboard.html', {
        'entities': entities,
        'entity_counts': entity_counts,
        'primary_entities': primary_entities,
        'secondary_entities': secondary_entities,
    })


@admin_required
def entity_list(request, entity):
    config = get_entity_config(entity)
    model = config['model']
    fields = get_model_fields(model)
    objects = model.objects.all().order_by('-pk')

    import json
    rows = []
    text_content_map = {}  # Stockage des descriptions
    text_field_names = []  # Noms des TextField
    
    for field in fields:
        if isinstance(field, models.TextField):
            text_field_names.append(field.name)
    
    for obj in objects:
        row_data = {
            'pk': obj.pk,
            'values': [],
        }
        for field in fields:
            value = getattr(obj, field.name)
            # Si c'est un TextField, stocker séparément
            if isinstance(field, models.TextField):
                text_content_map[f"{obj.pk}_{field.name}"] = value
                row_data['values'].append({
                    'type': 'text_field',
                    'field_name': field.name,
                })
            else:
                row_data['values'].append({
                    'type': 'normal',
                    'value': format_value(value),
                })
        rows.append(row_data)

    return render_gestion(request, 'gestion/object_list.html', {
        'entity': entity,
        'label': config['label'],
        'detail_label': config['detail_label'],
        'fields': fields,
        'rows': rows,
        'text_content_map': json.dumps(text_content_map),
        'text_field_names': text_field_names,
    })


@admin_required
def entity_detail(request, entity, object_id):
    config = get_entity_config(entity)
    model = config['model']
    obj = get_object_or_404(model, pk=object_id)
    fields = get_model_fields(model)

    detail_fields = [
        {
            'name': field.name,
            'label': field.verbose_name,
            'value': format_value(getattr(obj, field.name)),
        }
        for field in fields
    ]

    return render_gestion(request, 'gestion/object_detail.html', {
        'entity': entity,
        'label': config['detail_label'],
        'object': obj,
        'fields': detail_fields,
    })


@admin_required
def entity_create(request, entity):
    config = get_entity_config(entity)
    model = config['model']
    form_class = build_form_class(model)
    form = form_class(request.POST or None, request.FILES or None)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f"{config['label']} cree avec succes.")
        return redirect('gestion:entity_list', entity=entity)

    return render_gestion(request, 'gestion/object_form.html', {
        'entity': entity,
        'label': config['label'],
        'form': form,
        'title': f'Ajouter un {config["label"].lower()}',
        'button_text': 'Creer',
    })


@admin_required
def entity_update(request, entity, object_id):
    config = get_entity_config(entity)
    model = config['model']
    obj = get_object_or_404(model, pk=object_id)
    form_class = build_form_class(model)
    form = form_class(request.POST or None, request.FILES or None, instance=obj)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f"{config['label']} modifie avec succes.")
        return redirect('gestion:entity_detail', entity=entity, object_id=obj.pk)

    return render_gestion(request, 'gestion/object_form.html', {
        'entity': entity,
        'label': config['label'],
        'form': form,
        'title': f'Modifier un {config["label"].lower()}',
        'button_text': 'Mettre a jour',
    })


@admin_required
def entity_delete(request, entity, object_id):
    config = get_entity_config(entity)
    model = config['model']
    obj = get_object_or_404(model, pk=object_id)

    if entity == 'utilisateurs' and request.user.pk == obj.pk:
        messages.error(request, 'Vous ne pouvez pas supprimer votre propre compte.')
        return redirect('gestion:entity_detail', entity=entity, object_id=obj.pk)

    if request.method == 'POST':
        obj.delete()
        messages.success(request, f"{config['label']} supprime avec succes.")
        return redirect('gestion:entity_list', entity=entity)

    return render_gestion(request, 'gestion/object_confirm_delete.html', {
        'entity': entity,
        'label': config['label'],
        'object': obj,
    })
