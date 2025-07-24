from django.db import models

# Create your models here.
class FundingSource(models.Model):
    SOURCE_CHOICES = [
        ('foundation', 'Yayasan'),
        ('csr', 'CSR'),
        ('investor', 'Investor'),
    ]

    name = models.CharField(max_length=255)
    type = models.CharField(max_length=50, choices=SOURCE_CHOICES)
    contact_info = models.TextField()

    def __str__(self):
        return self.name