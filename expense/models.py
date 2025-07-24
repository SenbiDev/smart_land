from django.db import models

# Create your models here.

class Expense(models.Model):
    CATEGORY_CHOICES=[
        ('', '')
    ]

    amaount = models.DecimalField(max_digits=20, decimal_places=2)
    date = models.DateField()
    description = models.TextField(max_length=100)
    proof_url = models.TextField(max_length=100)
    project_id = models.IntegerField()
    funding_url = models.IntegerField()
    asset_id = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name