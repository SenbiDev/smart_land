from django.db import models
from funding_source.models import FundingSource

# Create your models here.
class Funding(models.Model):
    STATUS_CHOICES = [
        ('avaliable', 'Tersedia'),
        ('allocated', 'Teralokasi'),
        ('used', 'Terpakai'),
    ]

    source = models.ForeignKey(FundingSource, on_delete=models.CASCADE, related_name='fundings')
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    date_received = models.DateField()
    purpose = models.TextField()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.source.name} - {self.amount}"