from django.db import models
from django.utils.text import slugify
from vendor.models import Vendor
from account.utils import get_random_filename
from core.models import BaseModel

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


class Shipping_options(BaseModel):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name="shipping_options")
    text = models.CharField(max_length=255)

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
