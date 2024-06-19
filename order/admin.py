from django.contrib import admin

from order.models import Order, Freeze_money, Shipping_details, Chat, Message
from product.models import Product


# Register your models here.
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("product", "total_price", "status")
    list_filter = ("status",)


admin.site.register(Freeze_money)
admin.site.register(Shipping_details)
admin.site.register(Chat)
admin.site.register(Message)
