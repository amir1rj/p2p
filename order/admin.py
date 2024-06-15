from django.contrib import admin

from order.models import Order, Freeze_money
from product.models import Product


# Register your models here.
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("product", "total_price", "status")
    list_filter = ("status",)


admin.site.register(Freeze_money)
