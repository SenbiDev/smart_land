from django.db import models
from investor.models import Investor
from ownership.models import Ownership
from profit_distribution.models import ProfitDistribution

# Create your models here.
class DistributionDetail(models.Model):
    distribution = models.ForeignKey(ProfitDistribution, on_delete=models.CASCADE, related_name='details')
    investor = models.ForeignKey(Investor, on_delete=models.CASCADE, related_name='distribution_details')
    ownership_percentage = models.FloatField()
    amount_received = models.DecimalField(max_digits=20, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.investor.username} - {self.amount_received}"
