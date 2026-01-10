from django.db import models
from investor.models import Investor
from asset.models import Asset
from funding.models import Funding

class Ownership(models.Model):
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    ]

    investor = models.ForeignKey(Investor, on_delete=models.CASCADE, related_name='ownerships')
    asset = models.ForeignKey(Asset, on_delete=models.PROTECT, related_name='ownerships', null=True, blank=True)
    funding = models.ForeignKey(Funding, on_delete=models.CASCADE, related_name='ownerships')
    units = models.IntegerField()
    ownership_percentage = models.FloatField(default=0.0, blank=True, null=True)
    investment_date = models.DateField()
    # [BARU] Menambahkan status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')

    def __str__(self):
        asset_name = self.asset.name if self.asset else "Dana Mengendap (Cash)"
        return f"{self.investor.user.username} - {asset_name} ({self.units} units) - {self.status}"
    
    class Meta:
        ordering = ['-ownership_percentage']