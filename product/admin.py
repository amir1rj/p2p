from rangefilter.filters import NumericRangeFilter, DateRangeFilter

from .models import Information, Image, Product, Category, Place, Unit, ProductChangeRequest, Shipping_options, Coupon
from django.contrib import admin


@admin.action(description='Approve selected change requests')
def approve_change_requests(modeladmin, request, queryset):
    for change_request in queryset:
        product = change_request.product
        product.title = change_request.title
        product.description = change_request.description
        product.price = change_request.price
        product.is_promoted = change_request.is_promoted
        product.quantity = change_request.quantity
        product.status = change_request.status
        product.category.set(change_request.categories.all())

        product.save()
        product.add_parent_categories()

        change_request.request_status = 'approved'
        change_request.save()


@admin.action(description='Reject selected change requests')
def reject_change_requests(modeladmin, request, queryset):
    for change_request in queryset:
        change_request.request_status = 'rejected'
        change_request.save()


class ProductChangeRequestAdmin(admin.ModelAdmin):
    list_display = ('product', 'title', 'price', 'quantity', 'vendor', 'request_status')
    actions = [approve_change_requests, reject_change_requests]
    list_filter = (
        'request_status',
        ('price', NumericRangeFilter),
    )
    search_fields = ["title", "description", "price", "quantity"]


admin.site.register(ProductChangeRequest, ProductChangeRequestAdmin)


class ImageInline(admin.TabularInline):
    model = Image


class InformationInline(admin.StackedInline):
    model = Information


# class ShippingOptionInline(admin.TabularInline):
#     model = Shipping_options
#

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("title", "price")
    list_editable = ("price",)
    search_fields = ("title",)
    inlines = (ImageInline, InformationInline)
    list_display_links = ("title",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("title", "parent")
    prepopulated_fields = {"slug": ("title",)}


admin.site.register(Place)
admin.site.register(Unit)
admin.site.register(Shipping_options)
admin.site.register(Coupon)
