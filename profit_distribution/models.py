from django.db import models
from production.models import Production  

# Create your models here.
class ProfitDistribution(models.Model):
    production = models.ForeignKey(Production, on_delete=models.CASCADE, related_name='profit_distribution')
    period = models.CharField(max_length=100)
    net_profit = models.DecimalField(max_digits=12, decimal_places=2)
    landowner_share = models.DecimalField(max_digits=15, decimal_places=2)
    Investor_share = models.DecimalField(max_digits=15, decimal_places=2)
    distribution_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"ProfitDistribution : {self.net_profit} on {self.date}"