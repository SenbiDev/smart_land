from django.db import models
from asset.models import Asset

class Project(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.PROTECT, related_name='projects')
    name = models.CharField(max_length=255)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    budget = models.DecimalField(max_digits=15, decimal_places=2)
    status = models.CharField(max_length=20, default='Planned')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name