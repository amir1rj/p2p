from django.db import models
from django.utils.text import slugify
from vendor.models import Vendor
from account.utils import get_random_filename
from core.models import BaseModel
from p2p import settings
import string
import random
from datetime import datetime, timezone
from django.db import models
from django.conf import settings
from django.utils import timezone as django_timezone
from django.core.exceptions import ValidationError

REQUEST_STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
]
PRODUCT_TYPE_CHOICES = [
    ('physical', 'Physical'),
    ('digital', 'Digital'),
]


class Category(BaseModel):
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, related_name="subsets", null=True, blank=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class Product(BaseModel):
    vendor = models.ForeignKey(Vendor, on_delete=models.PROTECT, related_name="products")
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]
    title = models.CharField(max_length=30)
    category = models.ManyToManyField(Category, related_name="products")
    description = models.TextField()
    price = models.IntegerField()
    slug = models.SlugField(unique=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    is_promoted = models.BooleanField(default=False)
    quantity = models.IntegerField(default=1)
    unit = models.ForeignKey("Unit", on_delete=models.PROTECT)
    src = models.ForeignKey("Place", on_delete=models.PROTECT, related_name="src_products")
    dst = models.ForeignKey("Place", on_delete=models.PROTECT, related_name="dst_products")
    type = models.CharField(max_length=10, choices=PRODUCT_TYPE_CHOICES, default='digital')
    shipping_options = models.ManyToManyField('Shipping_options', related_name='products', null=True, blank=True)

    class Meta:
        verbose_name = "product"
        verbose_name_plural = "products"
        ordering = ("-is_promoted", "-create_datetime",)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def add_parent_categories(self):
        parents_to_add = set()
        for category in self.category.all():
            parent = category.parent
            if parent:
                parents_to_add.add(parent)

        if parents_to_add:
            self.category.add(*parents_to_add)
            self.save()


class Information(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="information")
    text = models.TextField()

    def __str__(self):
        return self.text[:30]


class Image(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name="images")
    image = models.ImageField("products/%Y/%m/%d/")

    # image = models.ImageField(get_random_filename("products/%Y/%m/%d/"))

    class Meta:
        verbose_name = "image"
        verbose_name_plural = "images"

    def __str__(self):
        return self.product.title


class Unit(BaseModel):
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class Place(BaseModel):
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class Shipping_options(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name="shipping_options")
    text = models.CharField(max_length=255)
    price = models.FloatField(default=0)

    def __str__(self):
        return self.text


class ProductChangeRequest(BaseModel):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name="change_requests")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="change_requests")
    title = models.CharField(max_length=60)
    description = models.TextField()
    price = models.IntegerField()
    is_promoted = models.BooleanField(default=False)
    quantity = models.IntegerField(default=1)
    status = models.CharField(max_length=10, choices=Product.STATUS_CHOICES, default='inactive')
    request_status = models.CharField(max_length=10, choices=REQUEST_STATUS_CHOICES, default='pending')
    categories = models.ManyToManyField(Category, related_name="change_requests")

    def __str__(self):
        return f"Change request for {self.product.title} by {self.vendor.user.username}"


class Coupon(models.Model):
    TYPE_CHOICES = [
        ('percent', 'percent'),
        ('value', 'value')
    ]
    ISSUED_BY_CHOICES = (
        ("site", "site"),
        ("vendor", "vendor"),
    )
    issued_by = models.CharField(max_length=10, choices=ISSUED_BY_CHOICES, default="site")
    type = models.CharField(max_length=7, choices=TYPE_CHOICES)
    expire_at = models.DateTimeField()
    amount = models.FloatField()
    description = models.TextField()
    code = models.CharField(max_length=25, blank=True)
    min_price = models.FloatField()
    max_value = models.FloatField()
    quantity = models.IntegerField(default=1)
    user_used = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="used_coupons", blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="owned_coupons",
                             null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="coupon_categories", blank=True,
                                 null=True)
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="coupon_products", blank=True,
                                null=True)

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self._generate_unique_code()
        super().save(*args, **kwargs)

    def _generate_unique_code(self):
        length = 8  # Define the length of the code
        characters = string.ascii_uppercase + string.digits
        while True:
            code = ''.join(random.choice(characters) for _ in range(length))
            if not Coupon.objects.filter(code=code).exists():
                return code

    def is_valid(self, user=None, order=None):
        now = django_timezone.now()

        if self.expire_at < now:
            return {"bool": False, "msg": "coupon code has expired"}

        if self.quantity <= 0:
            return {"bool": False, "msg": "coupon code is used before "}

        if user and self.user_used.filter(id=user).exists():
            return {"bool": False, "msg": "you cannot use this coupon two time "}

        if order:

            if self.product and self.product.id != order.product.id:
                return {"bool": False, "msg": "This coupon is not valid for the selected product"}
            if self.category and not order.product.category.filter(id=self.category.id).exists():
                return {"bool": False, "msg": "This coupon is not valid for the selected product category"}

            if order.product.price * order.quantity < self.min_price:
                return {"bool": False, "msg": f"The order total must be at least {self.min_price} to use this coupon"}
        if self.user and user:
            bool = self.user.id == user
            if bool:
                return {"bool": True, "msg": "coupon code has been successfully applied"}
            else:
                return {"bool": False, "msg": "this coupon not belongs to you"}
        return {"bool": True, "msg": "coupon code has been successfully applied"}

    def use_coupon(self, user):
        if self.is_valid(user):
            self.quantity -= 1
            self.user_used.add(user)
            self.save()
            return True
        else:
            raise ValidationError("Coupon is not valid")

    def __str__(self):
        return f"Coupon(code={self.code}, type={self.type}, amount={self.amount})"
