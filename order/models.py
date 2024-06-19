from django.db import models
from django.utils import timezone
from datetime import timedelta
from product.models import PRODUCT_TYPE_CHOICES
from core.models import BaseModel
from p2p.settings import AUTH_USER_MODEL, SITE_PROFIT_PERCENT_USER
from product.models import Product, Shipping_options
from vendor.models import Vendor

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
    shipping_option = models.ForeignKey(Shipping_options, on_delete=models.PROTECT, related_name="orders", null=True,
                                        blank=True)
    shipping_details = models.ForeignKey('Shipping_details', on_delete=models.PROTECT, related_name="orders",
                                         null=True, )

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


class Shipping_details(BaseModel):
    # physical product information
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="shipping_details")
    type = models.CharField(max_length=255, choices=PRODUCT_TYPE_CHOICES)
    address = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True,
                            help_text="its not necessarily if your order is digital")
    state = models.CharField(max_length=255, null=True, blank=True,
                             help_text="its not necessarily if your order is digital")
    country = models.CharField(max_length=255, null=True, blank=True,
                               help_text="its not necessarily if your order is digital")
    zipcode = models.CharField(max_length=255, null=True, blank=True,
                               help_text="its not necessarily if your order is digital")
    phone = models.CharField(max_length=255, null=True, blank=True,
                             help_text="its not necessarily if your order is digital")
    email = models.CharField(max_length=255, null=True, blank=True,
                             help_text="its not necessarily if your order is digital")
    description = models.TextField()
    # digital info
    auth_info = models.TextField(null=True, blank=True, help_text="its not necessarily if your order is physical")
    account_address = models.CharField(max_length=255, null=True, blank=True,
                                       help_text="its not necessarily if your order is physical")

    def __str__(self):
        return f"{self.user} Shipping details - {self.type} "


class Chat(BaseModel):
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="chats")
    vendor = models.ForeignKey(Vendor, on_delete=models.PROTECT, related_name="chats")

    def __str__(self):
        return f"{self.user} chat - {self.vendor}"


class Message(BaseModel):
    content = models.TextField()
    author = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.PROTECT)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="messages")

    def last_messages(self, ):
        return Message.objects.order_by('-timestamp').filter(chat__id=self.chat.id)
