from django.db import models
from django.conf import settings

from account.utils import get_random_filename

STATUS_CHOICES = [
    ('rejected', 'Rejected'),
    ('active', 'Active'),
    ('inactive', 'Inactive'),
    ('pending', 'Pending'),
]


class Vendor(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='vendor')
    description = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"{self.user} - {self.status}"


class VendorImage(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to="vendor/%Y/%m/%d")
    # image = models.ImageField(upload_to=get_random_filename("vendor/%Y/%m/%d"))
