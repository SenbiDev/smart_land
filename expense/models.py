from django.db import models
from project.models import Project 
from funding.models import Funding
from asset.models import Asset
# Create your models here.

class Expense(models.Model):
    CATEGORY_CHOICES=[
        ('material', 'Material'),
        ('tenaga kerja', 'Tenaga Kerja'),
        ('transport', 'Transport'),
        ('feed', 'Pakan'),
        ('perawatan', 'Perawatan'),
        ('tools', 'Alat dan Perlengkapan'),
        ('other', 'Lain-Lain'),
    ]

    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    date = models.DateField()
    description = models.TextField(max_length=100)
    proof_url = models.TextField(max_length=100)
    project_id = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='expense', null=True, blank=True)
    funding_id = models.ForeignKey(Funding, on_delete=models.CASCADE, related_name='expense', null=True, blank=True)
    asset_id = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='expense', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Expense {self.id} – {self.description[:20]}"
