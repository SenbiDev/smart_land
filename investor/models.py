from django.db import models
from django.conf import settings

# Create your models here.
class Investor(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    contact = models.TextField()
    join_date = models.DateField()
    total_investment = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"Investor:{self.user.username}"