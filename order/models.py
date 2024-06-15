from django.db import models
from django.utils import timezone
from datetime import timedelta

from core.models import BaseModel
from p2p.settings import  AUTH_USER_MODEL, SITE_PROFIT_PERCENT_USER
from product.models import Product

ORDER_CHOICES = (
    ("pending", "Pending"),
    ("confirmed", "Confirmed"),
    ("canceled", "Canceled"),
    ("approved", "Approved"),
    ("delayed", "Delayed"),
    ("rejected", "Rejected"),
    ("completed", "Completed"),

)


class Order(BaseModel):
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="orders")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="orders")
    total_price = models.DecimalField(max_digits=10, default=0, decimal_places=2)
    status = models.CharField(max_length=20, choices=ORDER_CHOICES)
    is_paid = models.BooleanField(default=False)
    quantity = models.IntegerField(default=0)
    finalize_day = models.IntegerField(default=5)

    def __str__(self):
        return f"{self.user} ordered - {self.quantity} - {self.product} - price= {self.total_price}"

    def save(self, *args, **kwargs):
        self.total_price = (self.quantity * self.product.price) + (
                (self.quantity * self.product.price) / SITE_PROFIT_PERCENT_USER)
        super().save(*args, **kwargs)

    def is_finalized(self):
        final_date = self.create_datetime + timedelta(days=self.finalize_day)
        return timezone.now() >= final_date


class Freeze_money(BaseModel):
    order = models.OneToOneField(Order, on_delete=models.PROTECT, related_name="suspend_money")
    value = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.value} - {self.order}"
