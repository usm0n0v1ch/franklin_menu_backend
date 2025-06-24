from django.db import models
from django.utils import timezone

class WaiterCall(models.Model):
    STATUS_CHOICES = [
        ('called', 'Вызван'),
        ('coming', 'В пути'),
        ('arrived', 'Подошел'),
    ]

    table_id = models.IntegerField()
    message_id = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='called')
    called_at = models.DateTimeField(default=timezone.now)
    coming_at = models.DateTimeField(null=True, blank=True)
    arrived_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.status == 'coming' and not self.coming_at:
            self.coming_at = timezone.now()
        elif self.status == 'arrived' and not self.arrived_at:
            self.arrived_at = timezone.now()
        super().save(*args, **kwargs)