# Generated by Django 5.2.4 on 2025-07-24 06:18

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('investor', '0003_rename_total_invesment_investor_total_investment'),
        ('profit_distribution', '0003_alter_profitdistribution_investor_share'),
    ]

    operations = [
        migrations.CreateModel(
            name='DistributionDetail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ownership_percentage', models.FloatField()),
                ('amount_received', models.DecimalField(decimal_places=2, max_digits=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('distributon', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='details', to='profit_distribution.profitdistribution')),
                ('investor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='distribution_details', to='investor.investor')),
            ],
        ),
    ]
