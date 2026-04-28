from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('commande', '0004_alter_articlecommande_id_alter_commande_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='commande',
            name='address',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='commande',
            name='delivery_method',
            field=models.CharField(blank=True, choices=[('standard', 'Livraison standard (2-4 jours)'), ('express', 'Livraison express (24h)'), ('pickup', 'Retrait en point relais')], default='', max_length=20),
        ),
        migrations.AddField(
            model_name='commande',
            name='email',
            field=models.EmailField(blank=True, default='', max_length=254),
        ),
        migrations.AddField(
            model_name='commande',
            name='full_name',
            field=models.CharField(blank=True, default='', max_length=120),
        ),
        migrations.AddField(
            model_name='commande',
            name='note',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='commande',
            name='payment_method',
            field=models.CharField(blank=True, choices=[('cash_on_delivery', 'Cash on delivery'), ('card', 'Carte bancaire')], default='', max_length=20),
        ),
        migrations.AddField(
            model_name='commande',
            name='phone',
            field=models.CharField(blank=True, default='', max_length=20),
        ),
        migrations.AddField(
            model_name='commande',
            name='quartier',
            field=models.CharField(blank=True, default='', max_length=120),
        ),
        migrations.AddField(
            model_name='commande',
            name='skin_problem',
            field=models.CharField(blank=True, default='', max_length=160),
        ),
        migrations.AddField(
            model_name='commande',
            name='skin_type',
            field=models.CharField(blank=True, choices=[('seche', 'Peau sèche'), ('grasse', 'Peau grasse'), ('mixte', 'Peau mixte')], default='', max_length=20),
        ),
        migrations.AddField(
            model_name='commande',
            name='ville',
            field=models.CharField(blank=True, default='', max_length=120),
        ),
    ]
