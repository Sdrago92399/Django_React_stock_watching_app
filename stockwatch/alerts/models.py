from django.db import models
from django.contrib.auth.models import User
from stocks.models import Stock
from decimal import Decimal
from bson.decimal128 import Decimal128

class AlertType(models.TextChoices):
    PRICE_ABOVE = 'PRICE_ABOVE', 'Price Above'
    PRICE_BELOW = 'PRICE_BELOW', 'Price Below'
    PERCENT_CHANGE = 'PERCENT_CHANGE', 'Percent Change'
    VOLUME_ABOVE = 'VOLUME_ABOVE', 'Volume Above'

class Alert(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='alerts')
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    alert_type = models.CharField(max_length=20, choices=AlertType.choices)
    threshold_value = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    is_triggered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_triggered_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # Convert Decimal128 to Decimal before saving
        if isinstance(self.threshold_value, Decimal128):
            self.threshold_value = Decimal(self.threshold_value.to_decimal())
        super(Alert, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.stock.symbol}"