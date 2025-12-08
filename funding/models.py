from django.db import models
# Pastikan import model lain sesuai struktur project Anda
from project.models import Project
from funding_source.models import FundingSource

class Funding(models.Model):
    STATUS_CHOICES = [
        ('available', 'Tersedia'),
        ('allocated', 'Dialokasikan'),
        ('used', 'Digunakan'),
    ]

    # [PERUBAHAN UTAMA] null=True, blank=True agar Project bersifat OPSIONAL
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True, related_name='fundings')
    
    source = models.ForeignKey(FundingSource, on_delete=models.CASCADE, related_name='fundings')
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    date_received = models.DateField()
    purpose = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        project_name = self.project.name if self.project else "Dana Belum Dialokasikan"
        return f"{self.source.name} - {project_name} - {self.amount}"