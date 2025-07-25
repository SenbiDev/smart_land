# Generated by Django 5.2.4 on 2025-07-23 12:01

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('production', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProfitDistribution',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('period', models.CharField(max_length=100)),
                ('net_profit', models.DecimalField(decimal_places=2, max_digits=12)),
                ('landowner_share', models.DecimalField(decimal_places=2, max_digits=15)),
                ('Investor_share', models.DecimalField(decimal_places=2, max_digits=15)),
                ('distribution_date', models.DateField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('production', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='profit_distribution', to='production.production')),
            ],
        ),
    ]
