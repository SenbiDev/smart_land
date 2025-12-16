from django.db import models
from production.models import Production

class ProfitDistribution(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Distributed', 'Distributed'),
    ]

    production = models.ForeignKey(Production, on_delete=models.CASCADE, related_name='profit_distributions')
    period = models.CharField(max_length=100)  
    net_profit = models.DecimalField(max_digits=15, decimal_places=2)
    landowner_share = models.DecimalField(max_digits=15, decimal_places=2)
    investor_share = models.DecimalField(max_digits=15, decimal_places=2)
    distribution_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending') 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Distribution for {self.production.name} - {self.period}"