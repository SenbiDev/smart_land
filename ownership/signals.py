from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Sum
from .models import Ownership

@receiver(post_save, sender=Ownership)
@receiver(post_delete, sender=Ownership)
def update_investor_total_investment(sender, instance, **kwargs):
    investor = instance.investor
    # Hitung total dari semua funding yang terhubung ke ownership investor ini
    total = Ownership.objects.filter(investor=investor).aggregate(
        total=Sum('funding__amount')
    )['total'] or 0
    
    investor.total_investment = total
    investor.save()