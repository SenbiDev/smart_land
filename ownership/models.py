from django.db import models
from investor.models import Investor
from asset.models import Asset
from funding.models import Funding

# Create your models here.
class Ownership(models.Model):
    investor = models.ForeignKey(Investor, on_delete=models.CASCADE, related_name='ownerships')
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='ownerships')
    funding = models.ForeignKey(Funding, on_delete=models.CASCADE, related_name='ownerships')
    units = models.IntegerField()
    investment_date = models.DateField()

    def __str__(self):
        return f"{self.investor.username} - {self.asset.name} ({self.units} units)"