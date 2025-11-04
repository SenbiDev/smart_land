from django.db import models
from project.models import Project 
from funding.models import Funding

class Expense(models.Model):
    CATEGORY_CHOICES = [
        ('material', 'Material'),
        ('tenaga kerja', 'Tenaga Kerja'),
        ('transport', 'Transport'),
        ('feed', 'Pakan'),
        ('perawatan', 'Perawatan'),
        ('tools', 'Alat dan Perlengkapan'),
        ('other', 'Lain-Lain'),
    ]

    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    date = models.DateField()
    description = models.TextField(max_length=100)
    proof_url = models.TextField(max_length=100)
    
    # FIXED: SET_NULL agar tidak cascade delete semua expense jika project/funding dihapus
    project_id = models.ForeignKey(
        Project, 
        on_delete=models.SET_NULL,  # Changed from CASCADE
        related_name='expenses',  # Changed from 'expense'
        null=True, 
        blank=True
    )
    funding_id = models.ForeignKey(
        Funding, 
        on_delete=models.SET_NULL,  # Changed from CASCADE
        related_name='expenses',  # Changed from 'expense'
        null=True, 
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Expense {self.id} – {self.description[:20]}"
    
    class Meta:
        ordering = ['-date']  # Default ordering by date descending