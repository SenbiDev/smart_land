# Generated by Django 5.2.4 on 2025-07-23 04:36

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('asset', '0003_delete_kategoriaset_alter_asset_ownership_status'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Pemilik',
            new_name='Owner',
        ),
        migrations.AddField(
            model_name='asset',
            name='owner',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='asset.owner'),
        ),
        migrations.AlterField(
            model_name='asset',
            name='ownership_status',
            field=models.CharField(choices=[('full_ownership', 'Full Ownership'), ('partial_ownership', 'Partial Ownership'), ('investor_owned', 'Investor Owned'), ('leashold', 'Leased'), ('under_construction', 'Under Construction'), ('personal_ownership', 'Personal Ownership')], max_length=50),
        ),
    ]
