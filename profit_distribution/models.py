from django.db import models
from django.utils import timezone
from production.models import Production

class ProfitDistribution(models.Model):
    production = models.ForeignKey(Production, on_delete=models.CASCADE, related_name='profit_distributions')
    period = models.CharField(max_length=100)
    net_profit = models.DecimalField(max_digits=20, decimal_places=2)
    landowner_share = models.DecimalField(max_digits=20, decimal_places=2)
    investor_share = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    distribution_date = models.DateField(default=timezone.now)

    def __str__(self):
        return f"Profit Distribution - {self.period} (ID: {self.id})"