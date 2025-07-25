# Generated by Django 5.2.4 on 2025-07-24 12:04

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('asset', '0004_rename_pemilik_owner_asset_owner_and_more'),
        ('funding', '0001_initial'),
        ('project', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Expense',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(choices=[('pertanian', 'Pertanian'), ('peternakan', 'Peternakan'), ('bagunan', 'Bangunan')], max_length=20)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=20)),
                ('date', models.DateField()),
                ('description', models.TextField(max_length=100)),
                ('proof_url', models.TextField(max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('asset_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='expense', to='asset.asset')),
                ('funding_url', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='expense', to='funding.funding')),
                ('project_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='expense', to='project.project')),
            ],
        ),
    ]
